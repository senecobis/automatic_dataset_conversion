import pocolog2msgpack
import msgpack

# Convert Pocolog file to MsgPack format
pocolog_file = "path/to/your/pocolog/file.pocolog"
msgpack_file = "path/to/your/output/file.msgpack"
pocolog2msgpack.convert(pocolog_file, msgpack_file)

# Read and process the MsgPack file
with open(msgpack_file, "rb") as f:
    unpacker = msgpack.Unpacker(f, raw=False)
    for unpacked_data in unpacker:
        print(unpacked_data)