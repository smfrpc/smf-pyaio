import xxhash


def parse_address(address):
    parts = address.split(":")
    assert len(parts) == 2, "Address format is host:port ({})".format(address)
    return parts[0], int(parts[1])


def payload_checksum(data):
    # uint32_t::max = 4294967295
    return xxhash.xxh64(data).intdigest() & 4294967295
