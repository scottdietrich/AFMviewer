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

import base64
import array

def decode_numbers(typecode, base64_str):
    return array.array(typecode, base64.decodebytes(bytes(base64_str, 'utf-8')))

def read_int32s(file, count):
    return [ int.from_bytes(file.read(4), byteorder='big') for x in range(count) ]
