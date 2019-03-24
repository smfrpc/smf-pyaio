import zstandard as zstd
from aiosmf.smf.rpc.compression_flags import compression_flags

_COMPRESSION_FLAG_ZSTD = compression_flags().zstd
_COMPRESSION_FLAG_NONE = compression_flags().none

class ZstdDecompressionFilter:
    def __init__(self):
        self._compress_ctx = zstd.ZstdDecompressor()

    def __call__(self, ctx):
        ctx.compression = _COMPRESSION_FLAG_NONE
        ctx.payload = self._compress_ctx.decompress(ctx.payload)

class ZstdCompressionFilter:
    def __init__(self, min_compression_size):
        self._min_size = min_compression_size
        self._compress_ctx = zstd.ZstdCompressor()

    def __call__(self, ctx):
        if len(ctx.payload) >= self._min_size:
            ctx.compression = _COMPRESSION_FLAG_ZSTD
            ctx.payload = self._compress_ctx.compress(ctx.payload)
