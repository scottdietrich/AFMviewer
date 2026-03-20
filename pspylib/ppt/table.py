# -*- coding: utf-8 -*-

#  Copyright (C) 2017 Park Systems.
#
#  This file is part of the Park Systems Python Library "PSPYLib".
#
#  Licensees holding valid commercial licenses may use this file in
#  accordance with the license agreement provided with the
#  Software or, alternatively, in accordance with the terms contained in
#  a written agreement between you and Park Systems.
#
#  For licensing terms and conditions see LICENSE.txt.

from . import tools as Tools
from . import frame as Frame
from . import defines as Defines

class Entry:
    def __init__(self, atype, aoffset):
        self._type = Frame.Type(atype)
        self._offset = aoffset

    def __repr__(self):
        return "<{}>".format(self.__str__)

    def __str__(self):
        return "Entry(type = {}, offset = {})".format(self._type.name, self._offset)

    @property
    def type(self):
        return self._type

    @property
    def offset(self):
        return self._offset    

    def valid(self):
        return self._type.valid and self._offset > 0

class Table:
    def __init__(self, f):
        self._marker = ''
        self._entries = []
        self._file = None
        self.load(f)

    def load(self, f):
        # header
        self._file = f
        self._marker = f.readline().strip()
        if self._marker != Defines.FILE_MARKER:
            raise ValueError('file marker is invalid')

        first, *_ = Tools.read_int32s(f, 4)
        num_entries = first & 0x00ffffff
        entry_start = f.tell()
        entry_length = 8
        
        # entries
        self._entries = []
        
        for i in range(num_entries):
            f.seek(entry_start + (i * entry_length))
            first, second = Tools.read_int32s(f, 2)
            e = Entry((first & 0xff000000) >> 24, second)
            if not e.valid:
                break

            self._entries.append(e)

    @property
    def entries(self):
        return self._entries

    def entry(self, index:int):
        return self._entries[index]



def load(file):
    return Table(file)