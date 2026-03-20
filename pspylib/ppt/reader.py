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

import array
from . import frame as Frame
from . import table as Table

class Reader:
    def __init__(self, path:str = None):
        self._file = None
        self._table = None

        if isinstance(path, str):
            self.load(path)

    def load(self, path):
        self._file = open(path, 'rb')
        self._table = Table.load(self._file)

    @property
    def table(self):
        return self._table

    def read(self, entry):
        return Frame.fromEntry(entry, self._file)
        

 
    

 