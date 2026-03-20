# -*- coding: utf-8 -*-

#  Copyright (C) 2018 Park Systems.
#
#  This file is part of the Park Systems Python Library "PSPYLib".
#
#  Licensees holding valid commercial licenses may use this file in
#  accordance with the license agreement provided with the
#  Software or, alternatively, in accordance with the terms contained in
#  a written agreement between you and Park Systems.
#
#  For licensing terms and conditions see LICENSE.txt.

# import context
import os
import csv
import time
import pspylib as ps
import pspylib.ppt as ppt
import pandas as pd


def extract(loc, dataname):
    
    ################# Please check and modify before run ##################
    # loc = "Source Data/500FeHrich/"
    # dataname = "1a_40nN_PinPoint_Forward 07-02-2025 172"
    input_file = loc + dataname + ".ps-ppt"  # input file name
    #######################################################################
    
    print("Processing csv files for " + dataname + " ...")
    input_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(loc, dataname)
    
    # folder prep.
    os.makedirs(output_dir, exist_ok=True)
    
    # Use absolute path directly if loc is absolute, otherwise prepend script dir
    if os.path.isabs(input_file):
        reader = ppt.Reader(input_file)
    else:
        reader = ppt.Reader(input_dir + '/' + input_file)
    recent = {}
    
    for index, entry in enumerate(reader.table.entries):
    
        frame = reader.read(entry)
    
        if frame.type.id is ppt.FRAME_TYPE_SCAN_STOP:
            break
    
        # if not a fd-curve, save it for later use and continue
        if frame.type.id is not ppt.FRAME_TYPE_PPT_FD_CURVE:
            recent[frame.type.id] = ps.PsDict(frame.contents)
            continue
    
        param = recent[ppt.FRAME_TYPE_PPT_PARAM]
        start = recent[ppt.FRAME_TYPE_SCAN_START]
        fdcurve = ps.PsDict(frame.contents)
    
        slow = fdcurve.value('/info/index')['slow']
        fast = fdcurve.value('/info/index')['fast']
        # print("processing item at slow:{}, fast:{}".format(slow, fast))
    
        # csv file prep.
        csv_path = output_dir + '/ppt-fd-slow{}-fast{}.csv'.format(slow, fast)
        csv_file = open(csv_path, 'w', newline='')
        csv_writer = csv.writer(csv_file)
    
        # meta
        csv_writer.writerow(['export.time', time.asctime(time.localtime())])
        csv_writer.writerow(['scan.geometry', start.value('/geometry')])
        csv_writer.writerow(['cantilever.name', param.value('/cantilever/name')])
        csv_writer.writerow(['cantilever.cal', param.value('/cantilever/cal')])
        csv_writer.writerow(['cantilever.geometry', param.value('/cantilever/geometry')])
        csv_writer.writerow(['pinpoint.basic', param.value('/pinpoint/basic')])
        csv_writer.writerow(['pinpoint.details', param.value('/pinpoint/details')])
        csv_writer.writerow(['sample', param.value('/sample')])
        csv_writer.writerow(['file', start.value('/path')])
        csv_writer.writerow(['info', fdcurve.value('/info')])
        csv_writer.writerow([])
    
        # data - header
        channels = fdcurve.value('/info/channels')
        csv_writer.writerow(['', channels[0]['id'], channels[1]['id'], channels[2]['id']])
        csv_writer.writerow(['no', channels[0]['unit'], channels[1]['unit'], channels[2]['unit']])
    
        # data - numbers
        numbers_encoded = fdcurve.value('/numbers')
        numbers0 = ppt.decode_numbers('f', numbers_encoded[0])
        numbers1 = ppt.decode_numbers('f', numbers_encoded[1])
        numbers2 = ppt.decode_numbers('f', numbers_encoded[2])
        count = min(len(numbers0), len(numbers1), len(numbers2))
    
    
        # Collect data rows
        data_rows = [[row + 1, numbers0[row], numbers1[row], numbers2[row]] 
                     for row in range(count)]
        
        # Write data to CSV
        df = pd.DataFrame(data_rows)
        df.to_csv(csv_path, mode='a', header=False, index=False)
                
    print("Complete.")
        
