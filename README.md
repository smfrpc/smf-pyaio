# aiosmf

smf rpc implementation for asyncio -- https://aiosmf.readthedocs.org

The [smf project](https://github.com/smfrpc/smf) is a high-performance rpc
platform built using the c++ [Seastar](https://github.com/scylladb/seastar)
framework. This project is a Python asyncio implementation of the rpc protocol
used by smf. There are also [Go](https://github.com/smfrpc/smf-go) and
[Java](https://github.com/KowalczykBartek/smf-java) implementations.

Note that current support in aiosmf is limited to client implementations.
Servers are written in C++, Go, or Java. Adding a Python server framework is
future work.

Please see https://aiosmf.readthedocs.org for instructions on getting started.
