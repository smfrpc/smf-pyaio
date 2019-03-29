import socket
import asyncio
import collections
import logging
import flatbuffers
import aiosmf
from aiosmf.smf.rpc import header as rpc_header
from aiosmf.smf.rpc.compression_flags import compression_flags

from .util import (
    parse_address,
    payload_checksum
)

logger = logging.getLogger("smf.client")
logging.basicConfig(level=logging.DEBUG)

_INCOMING_TIMEOUT = 0.01
_UINT16_MAX = 65535

_COMPRESSION_FLAGS_DISABLED = compression_flags().disabled
_COMPRESSION_FLAGS_MAX = compression_flags().max
_COMPRESSION_FLAGS_NONE = compression_flags().none


class _Context:
    """
    Manage RPC send and receive state.
    """
    def __init__(self, payload, meta, session_id,
            compression=_COMPRESSION_FLAGS_NONE):
        self.payload = payload
        self.meta = meta
        self.session_id = session_id
        self.compression = compression

    def apply(self, filters):
        for f in filters:
            f(self)

async def create_connection(address, *, timeout=None, loop=None):
    host, port = parse_address(address)

    if timeout is not None and (not isinstance(timeout, (int, float)) \
            or timeout <= 0):
        raise ValueError("Invalid timeout: None or > 0")

    if loop is None:
        loop = asyncio.get_running_loop()

    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port, loop=loop),
        timeout=timeout, loop=loop)

    sock = writer.transport.get_extra_info("socket")
    if sock is not None:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        address = sock.getpeername()

    return SMFConnection(reader, writer,
            address=address,
            loop=loop)

class SMFConnection:
    def __init__(self, reader, writer, *, address, loop=None):
        self._reader = reader
        self._writer = writer
        self._address = address
        self._loop = loop or asyncio.get_running_loop()
        self._incoming_filters = tuple()
        self._outgoing_filters = tuple()
        self._incoming_timeout = None
        self._session_id = 0
        self._sessions = {}
        self._read_task = asyncio.ensure_future(
                self._read_requests(), loop=self._loop)

    def __repr__(self):
        return "<SMFConnection [{}]>".format(self._address)

    def append_incoming_filter(self, f):
        self._incoming_filters += (f,)

    def append_outgoing_filter(self, f):
        self._outgoing_filters += (f,)

    async def call(self, payload, func_id):
        """
        Args:
            payload:
            func_id:
        """
        session_id, future_reply = self._new_session()
        call_ctx = _Context(payload, func_id, session_id)
        await self._send_request(call_ctx)
        return await self._receive_reply(future_reply)

    async def close(self):
        if self._reader:
            self._reader.feed_eof()
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()

    def _new_session(self):
        self._session_id += 1
        if self._session_id > _UINT16_MAX:
            self._session_id = 0
        if self._session_id in self._sessions:
            raise Exception("no rpc slot available")
        future_reply = self._loop.create_future()
        self._sessions[self._session_id] = future_reply
        return (self._session_id, future_reply)

    async def _send_request(self, ctx):
        ctx.apply(self._outgoing_filters)
        header = self._build_header(ctx)
        self._writer.write(header)
        self._writer.write(ctx.payload)
        await self._writer.drain()

    def _build_header(self, ctx):
        checksum = payload_checksum(ctx.payload)
        builder = flatbuffers.Builder(20)
        header = rpc_header.Createheader(builder, ctx.compression, 0,
            ctx.session_id, len(ctx.payload), checksum, ctx.meta)
        builder.Finish(header)
        return builder.Output()[4:]

    async def _receive_reply(self, future_reply):
        recv_ctx = await future_reply
        recv_ctx.apply(self._incoming_filters)
        return recv_ctx.payload, recv_ctx.meta

    async def _read_requests(self):
        while True:
            try:
                await asyncio.wait_for(self._read_request(),
                        timeout=self._incoming_timeout,
                        loop=self._loop)
            except asyncio.TimeoutError:
                logger.error("timeout error")
            except Exception as e:
                # we should pobably reset things here...
                logger.error("got error {}".format(e))
                for response in self._sessions.values():
                    response.set_exception(Exception("something happened"))

    async def _read_request(self):
        header = await self._read_header()
        payload = await self._read_payload(header)
        compression = header.Compression()
        if header.Compression() == _COMPRESSION_FLAGS_DISABLED:
            compression = _COMPRESSION_FLAGS_NONE
        recv_ctx = _Context(payload, header.Meta(), header.Session(), compression)
        session = self._sessions.pop(header.Session(), None)
        if session is not None:
            session.set_result(recv_ctx)
        else:
            # we should probably reset things here by raising an exception
            logging.error("session id {} not found".format(header.Session()))

    async def _read_header(self):
        buf = await self._reader.readexactly(16) #timeout?
        header = rpc_header.header()
        header.Init(buf, 0)
        if header.Size() == 0:
            raise Exception("skipping body its empty")
        if header.Size() > flatbuffers.builder.Builder.MAX_BUFFER_SIZE:
            raise Exception("bad payload. body bigger than flatbuf max size")
        if header.Compression() > _COMPRESSION_FLAGS_MAX:
            raise Exception("compression out of range")
        if header.Checksum() <= 0:
            raise Exception("empty checksum")
        if header.Bitflags() != 0:
            raise NotImplementedError()
        if header.Meta() <= 0:
            raise Exception("empty meta")
        return header

    async def _read_payload(self, header):
        buf = await self._reader.readexactly(header.Size()) #timeout?
        checksum = payload_checksum(buf)
        if header.Checksum() == checksum:
            return buf
        else:
            raise Exception("payload checksum mismatch")
