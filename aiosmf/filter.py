import zstandard as zstd

from .constants import (
    COMPRESSION_ZSTD,
    COMPRESSION_NONE
)

class ZstdDecompressionFilter:
    def __init__(self):
        self._compress_ctx = zstd.ZstdDecompressor()

    def __call__(self, ctx):
        if ctx.compression == COMPRESSION_ZSTD:
            ctx.payload = self._compress_ctx.decompress(ctx.payload)
            ctx.compression = COMPRESSION_NONE

class ZstdCompressionFilter:
    def __init__(self, min_compression_size, *, strategy=zstd.STRATEGY_FAST):
        self._min_compression_size = min_compression_size
        self._params = zstd.CompressionParameters(strategy=strategy)
        self._compress_ctx = zstd.ZstdCompressor(compression_params=self._params)

    def __call__(self, ctx):
        if ctx.compression != COMPRESSION_NONE and \
                len(ctx.payload) >= self._min_compression_size:
            ctx.payload = self._compress_ctx.compress(ctx.payload)
            ctx.compression = COMPRESSION_ZSTD
