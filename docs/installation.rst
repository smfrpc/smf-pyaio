Installation
============

There are three main components needed to use aiosmf:

1. The `flatbuffers <https://google.github.io/flatbuffers/>`_ compiler
2. The `smf <https://github.com/smfrpc/smf>`_ rpc service definition compiler
3. The aiosmf package (you're in the right place!)

The aiosmf library may be installed using pip:

    pip install aiosmf

Most Linux distributions include the flatbuffers compiler.  Please consult the
`flatbuffers website <https://google.github.io/flatbuffers>`_ or your
distribution package manaager for installation instructions.

Installation instructions for the smf compiler can be found at
https://github.com/smfrpc/smf which must currently be installed from source.
There you can also find links to instructions on using smf to build
high-performance rpc servers with c++.
