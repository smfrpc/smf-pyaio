Development notes
=================

When making changes to the smf flatbuffers idl make the following updates if
still relevant.

.. code-block:: diff

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

Convenience copies of the compression flags should also be updated in constants.py

.. code-block:: diff

    diff --git a/aiosmf/connection.py b/aiosmf/connection.py
    index 69ba45c..81dc102 100644
    --- a/aiosmf/connection.py
    +++ b/aiosmf/connection.py
    @@ -148,7 +148,13 @@ class SMFConnection:
             header = aiosmf.smf.rpc.header.Createheader(builder, ctx.compression, 0,
                     ctx.session_id, len(ctx.payload), checksum, ctx.meta)
             builder.Finish(header)
    -        return builder.Output()[4:]
    +        # XXX: the flatbuffers python code doesn't offer a sizeof option for
    +        # structs and the serialization also adds a size header into the buffer.
    +        # so when integrating an update the codegen make sure that the header is
    +        # stripped off and the size is correct.
    +        buf = builder.Output()[4:]
    +        assert len(buf) == 16
    +        return buf
