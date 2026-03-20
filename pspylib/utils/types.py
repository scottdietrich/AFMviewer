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

import json

class PsDict():
    def __init__(self, data = None):
        self.load(data)

    def load(self, data):
        if isinstance(data, dict):
            self.raw = data
        elif isinstance(data, str):
            self.raw = json.loads(data)
        elif isinstance(data, bytes):
            self.raw = json.loads(data.decode('utf8'))
        else:
            self.raw = {}

    def to_dict(self): 
        return self.raw

    def to_json(self): 
        return json.dumps(self.raw)

    def value(self, loc, fallback = None):        
        parsed = loc.split('/')
        current = self.raw

        for i, name in enumerate(parsed):
            if (i == 0 and name == ""):
                continue

            try:
                if (i == (len(parsed) - 1)):
                    return current[name]
                else:
                    current = current[name]

            except KeyError:
                return fallback    
       

