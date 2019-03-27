import asyncio
import collections
import logging
import flatbuffers
import xxhash
import aiosmf.smf.rpc.header
import aiosmf.smf.rpc.compression_flags
import aiosmf.smf.rpc.header_bit_flags
from aiosmf.smf.rpc.compression_flags import compression_flags

logger = logging.getLogger("smf.client")

_INCOMING_TIMEOUT = 0.01
_UINT16_MAX = 65535
_UINT32_MAX = 4294967295

_COMPRESSION_FLAGS_DISABLED = compression_flags().disabled
_COMPRESSION_FLAGS_MAX = compression_flags().max

def _checksum(data):
    return xxhash.xxh64(data).intdigest() & _UINT32_MAX

class _Context:
    """
    Manage RPC send and receive state.
    """
    def __init__(self, payload, meta, session_id,
            compression=aiosmf.smf.rpc.compression_flags.compression_flags().none):
        self.payload = payload
        self.meta = meta
        self.session_id = session_id
        self.compression = compression

    def apply(self, filters):
        for f in filters:
            f(self)

class Client:
    def __init__(self, host, port, *, incoming_filters=(),
            outgoing_filters=(), incoming_timeout=_INCOMING_TIMEOUT, loop=None):
        self._host = host
        self._port = port
        self._incoming_filters = incoming_filters
        self._outgoing_filters = outgoing_filters
        self._loop = loop or asyncio.get_running_loop()
        self._incoming_timeout = incoming_timeout
        self._reader = None
        self._writer = None
        self._session_id = 0
        self._sessions = {}

    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(
            self._host, self._port, loop=self._loop)
        asyncio.create_task(self._read_requests())

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
        checksum = _checksum(ctx.payload)
        builder = flatbuffers.Builder(20)
        header = aiosmf.smf.rpc.header.Createheader(builder,
                ctx.compression,
                0, ctx.session_id, len(ctx.payload), checksum, ctx.meta)
        builder.Finish(header)
        return builder.Output()[4:]

    async def _receive_reply(self, response):
        ctx = await response
        ctx.apply(self._incoming_filters)
        return ctx.payload, ctx.meta

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
        header = aiosmf.smf.rpc.header.header()
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
        checksum = _checksum(buf)
        if header.Checksum() == checksum:
            return buf
        else:
            raise Exception("payload checksum mismatch")
