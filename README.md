* Works with https://github.com/MagicStack/uvloop

# flatc notes

```diff
diff --git a/aiosmf/smf/rpc/compression_flags.py b/aiosmf/smf/rpc/compression_flags.py
index b8bbfb6..2234e32 100644
--- a/aiosmf/smf/rpc/compression_flags.py
+++ b/aiosmf/smf/rpc/compression_flags.py
@@ -17,4 +17,4 @@ class compression_flags(object):
     zstd = 2
 # /// \brief lz4 compression
     lz4 = 3
-
+    max = lz4
```
