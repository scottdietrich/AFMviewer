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

# constants

import json
from . import defines as Defines

class Type:
    def __init__(self, aid = Defines.FRAME_TYPE_INVALID):
        self._id = aid

    @property
    def name(self):
        return Defines.FRAME_NAMES.get(self._id, '')

    @property
    def id(self):
        return self._id

    @property
    def valid(self):
        return self._id in Defines.FRAME_NAMES


class Frame:
    def __init__(self, atype, ajson):
        self._type = atype
        self._contents = ajson

    @property
    def type(self):
        return self._type

    @property
    def contents(self):
        return self._contents


def fromEntry(entry, f):
    f.seek(entry.offset)
    ajson = json.loads(f.readline().decode('utf-8')) 
    return Frame(entry.type, ajson)