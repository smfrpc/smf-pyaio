# automatically generated by the FlatBuffers compiler, do not modify

# namespace: rpc

import flatbuffers

# /// \brief, useful when the type is empty
# /// i.e.: void foo();
# /// rpc my_rpc { null_type MutateOnlyOnServerMethod(int); }
# ///
class null_type(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsnull_type(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = null_type()
        x.Init(buf, n + offset)
        return x

    # null_type
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

def null_typeStart(builder): builder.StartObject(0)
def null_typeEnd(builder): return builder.EndObject()
