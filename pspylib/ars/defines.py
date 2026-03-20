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
FILE_EXT = b'ps-ars'
FILE_MARKER = b'PS-ARS/v1'

PUB_URL = 'tcp://127.0.0.1:5559'
PUB_PROTOCOL = b'PS-ARSP/v1'

FRAME_TYPE_INVALID = -1,
FRAME_TYPE_SCAN_START = 0
FRAME_TYPE_SCAN_STOP = 1
FRAME_TYPE_ARS_PARAM = 16
FRAME_TYPE_ARS_ID_CURVE = 17

FRAME_NAMES = {
    FRAME_TYPE_SCAN_START: "scan.start",
    FRAME_TYPE_SCAN_STOP: "scan.stop",
    FRAME_TYPE_ARS_PARAM: "ars.param",
    FRAME_TYPE_ARS_ID_CURVE: "ars.rtid"
}
