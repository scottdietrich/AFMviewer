import struct

atable = {
    'byte': ('<B', 1),
    'uint16': ('<H', 2), 
    'int16': ('<h', 2),
    'uint32': ('<I', 4),
    'int32': ('<i', 4), 
    'float32': ('<f', 4),
    'double64': ('<d', 8)
}

def read(afile, alist):
    adict = {}

    for i in range(len(alist)):
        akey, atype, count = alist[i]
        marker, offset = atable[atype] 

        result = []
        for x in range(count):
            result.append(struct.unpack(marker, afile.read(offset))[0]) 

        if count == 1:
            adict.update({akey : (result[0], atype)})
        else:
            adict.update({akey : (result, atype)})

    return adict

def write(afile, number, atype):
    marker, _ = atable[atype]
    afile.write(struct.pack(marker, number))

def writeList(afile, alist):
    for i in range(len(alist)):
        lists, atype = alist[i]
        marker, _ = atable[atype]
        
        if isinstance(lists, list):
            for x in range(len(lists)):
                afile.write(struct.pack(marker, lists[x]))
        else:
            afile.write(struct.pack(marker, lists))