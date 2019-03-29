from aiosmf.smf.rpc.compression_flags import compression_flags

COMPRESSION_ZSTD = compression_flags().zstd
COMPRESSION_NONE = compression_flags().none
COMPRESSION_DISABLED = compression_flags().disabled
COMPRESSION_MAX = compression_flags().max
