"""
Writer(data, path)  Write Park Systems Tiff Data to File
Input:
    data: Park Systems Tiff data
    path: full file path of intended "Park Systems tiff file" 
        'ScanHeader': Park Systems Tiff Header
            'dataCategory': 0 = 2d mapped image, 1 = line profile image, 2 = Spectroscopy image
            'channelName': source name of image(ex: topography, z detector, ...) 
            'headMode': image mode of image(ex: CAFM, NCAFM, MFM, ...)
            'lowPassStrength': Low Pass Filter strength
            'isAutoFlatten': automatic flatten after imaging
            'isAcTrack': acTrack
            'width':  number of pixels in the direction of width (x-axis)
            'height': number of pixels in the direction of height (y-axis)
            'scanRotation':  Angle of Fast direction about positive x-axis. 
            'isSineScan': none-zero for sine scan, 0 for normal scan.
            'overScanRatio': Overscan rate
            'isFastScanLeftToRight': non-zero for forward, 0 for backward.
            'isSlowScanBottomToTop': non-zero when scan up, 0 for scan down.
            'isXYSwapped': Swap fast-slow scanning dirctions.
            'scanSizeWidth':  x scan size (dimension: um)
            'scanSizeHeight': y scan size (dimension: um)
            'scanOffsetX':    x offset (dimension: um)
            'scanOffsetY':    y offset (dimension: um)
            'scanRate': Scan speed in rows per second. 
            'setpoint':  Error signal set point.
            'setpointUnit': SetPoint Unit (um)
            'tipBias':    Tip Bias Voltage
            'sampleBias': Sample Bias Voltage
            'dataGain': Z Data Gain
            'ZScale':  z data scale           
            'ZOffset': z Offset (dimension: um)
            'unit': Z Data Unit (um)
            'dataMin':  Minimum value of data
            'dataMax':  Maximum value of data
            'dataAverage': mean value of data
            'compression': compression Option        
            'isLogScale': Is the data in log scale.
            'isSquared': Is the data squared
            'zServoGain': Z Servo gain
            'zScannerRange': Z Scanner Range
            'xyVoltageMode': XY Voltage mode	
            'zVoltageMode':  Z Voltage mode
            'xyServoMode':   XY Servo mode
            'dataType': 0 = 16bit short, 1 = 32bit int, 2 = 32bit float
            'numOfPddRegionX': number of X PDD Region
            'numOfPddRegionY': number of Y PDD Region
            'ncmAmplitude': NCM Amplitude
            'ncmFrequency': NCM Selected Frequency  in Hz
            'headRotation'
            'cantileverName': Cantilever Name
            'ncmDrivePercent': NCM Drive % (range = 0~100)
            'intensityFactor': intensity factor (dimensionless) = (A+B)/3
            'headTilting': head tilt angle in degree.
            'logAmpOffset'
            'tipSampleDistance'
            'zServoNcGain'
            'zServoPGain'
            'zServoIGain'
            'isTapping'
            'dataMinV2'
            'dataMaxV2'
            'stageX'
            'stageY'
            'sampleX'
            'sampleY'
            'imageQualityIndex'
        'ScanData': 
            'ZData': [Height]X[Width] double array
        'SpectHeader':
            'name': source name of image
            'unit': data unit
            'gain': data gain
            'isXAxis': is X Axis Source
            'isYAxis': is Y Axis Source
            'numOfChannels': Number Of Spect Sources
            'average': mean value of data
            'numOfDataAllDir': data in a line
            'numOfPoints': number of (x,y)'s
            'drivingChannelIndex': driving source index
            'forwardPeriod': (sec)
            'backwardPeriod': (sec)
            'forwardSpeed': Driving Source Unit / sec
            'backwardSpeed': Driving Source Unit / sec
            'gridUsed': is Volume Image
            'channelOffset': Sources offset
            'channelIsLog': Is the data in log scale.
            'channelIsSquared': Is the data squared
            'gridNumOfColumn': number of Spect Points Per X
            'hasRefImage': Is reference image
            ## Grid Information
            'gridSizeWidth':  X ScanSize
            'gridSizeHeight': Y ScanSize
            'gridOffsetX': X Offset
            'gridOffsetY': Y Offset
            ## F/D Spectroscopy Information
            'ForceConstantNewtonPerMeter': Force Constant Newton per Meter
            'SensitivityVoltPerMicroMeter': Sensitivity Voltage per MicroMeter
            'ForceLimitVolt': Force Limit Voltage
            'TimeInterval': Time Interval
            ## I/V and P/E share bleow 4 variables
            'MaxVoltage': Max Voltage
            'MinVoltage': Min Voltage
            'StartVoltage': Start Vlotage
            'EndVoltage': End Voltage
            'DelayedStartTime': Delayed Start Time
            'useZServo': Is ZServo
            'sourceGain': Data Gain
            'source_unit': Source Unit
            'hasEXtendedHeader': Is Use Extend Header
            'spectType': 
                0: FD, IV (Old)
                1: Indenter (Old)
                2: FD
                3: IV
                4: Nano Indenter
                5: Photo Current (TRPCM, PCM)
                6: ID Curve (Current-Distance Curve, ICM Approach Curve)
                7: TA Curve (Thermal Analysis Curve for SThM)
                8: AD Curve (NCM Amplitude vs Distance Curve)
                9: PE Curve (Polarization vs Electric field curve)
            ## Photo-current and P/E share the variables
            ## P/E Spectroscopy Information
            'writingTime': writing time
            'waitingTime': waiting time
            'readingTime': reading time
            'biasStep':    bias step
            'numberOfLoops': loop counts
            'usePulse': Is use pulse
            ## Photo-current Information	
            'resetLevel': reset level
            'resetDuration': reset duration
            'operationLevel': operation level
            'operationDuration': operation duration
            'timeBeforeReset': time before reset
            'timeAfterReset':  time after reset
            'timeBeforeLightOn': time before light on 
            'timeLightDuration': time light duration
            ## TA Information
            'offsetTemperature': offset temperature
            'offsetSThMError': offset SThMError
            'referenceTemperature': reference temperature
            'referenceProbeCurrent': reference probe current
            'referenceSThMError': reference SThMError
            'dataType': 0 = 16bit short, 1 = 32bit int, 2 = 32bit float
            'setpoint'
            'setpointUnitType'
        'SpectData': 
            'rawData': spectroscopy data

## Reliability can not be guaranteed if:
    - 'Tag' is removed or added
    -  the size of 'numpy' objects has changed
   Do not change 'Tag' or data counts.

## Example 
    reader_path_spect = 'C:/SWDev/NXSWDev/src/trunk/prototypes/tiff/spect_sample.tiff' # sample for spect data
    writer_path_spect = 'C:/SWDev/NXSWDev/src/trunk/prototypes/tiff/test_write_spect.tiff'

    data_spect = tiff_reader.TiffReader(reader_path_spect).data

    Writer(data_spect, writer_path_spect)

Copyright (c) 2018 Park Systems
"""
from pspylib.tiff import constant
from pspylib.tiff import reader
from pspylib.tiff import metaData
from pspylib.tiff import tools

class Writer: 
    def __init__(self, data, path:str = None):
        self.isEmpty = True
        self.error = constant.ErrorIndicator()

        if isinstance(data, metaData.Data):
            self.setData(data)

        if isinstance(path, str):
            self.write(path)

    def setData(self, data):
        self.tags = data.tags

        self.scan = data.scanHeader
        self.scanData = data.scanData
        self.spect = data.spectHeader
        self.spectData = data.spectData

        self.strip = data.metaData.strip
        self.colorMap = data.metaData.colorMap
        self.thumbnail = data.metaData.thumbnail

        self.isEmpty = False

    def write(self, path):
        self.path = path

        if self.isEmpty:
            print("Data is not setted.")
            return False

        try:
            self.f = open(path, 'wb')

        except FileNotFoundError:
            print("No such folder.")
            return False

        self.__writeFileHeader__()
        self.__writeTags__()

        if not self.__isPsiaTiff__(): 
            return False

        self.__writeStrip__()
        self.__writeColorMap__()

        if self.scan.scanHeader['dataCategory'][0] == constant.PsiaDataCategoryTopography:
            self.__writeScanData__()
            self.__writeScanHeader__()
        #elif self.scan.scanHeader['dataCategory'][0] == constant.PsiaDataCategoryLineProfile:
        elif self.scan.scanHeader['dataCategory'][0] == constant.PsiaDataCategorySpectroscopy:
            self.__writeScanHeader__()
            self.__writeSpectHeader__()
            self.__writeSpectData__()
        else:
            print("This data type is not supported.")
            return False

        self.__writeThumbnail__()

        self.f.close()
        return True

    def __writeFileHeader__(self):
        f = self.f
        f.seek(0)

        tools.write(f, constant.ByteMarkLittleEndian, 'uint16')
        tools.write(f, constant.MagicNumber, 'uint16')
        tools.write(f, 8, 'uint32')
        self.firstIFDOffset = f.tell()
        return True

    def __writeTags__(self):
        if not hasattr(self, 'firstIFDOffset'): 
            return self.error.notValidated()

        f = self.f
        f.seek(self.firstIFDOffset)

        tools.write(f, self.tags.numOfTags['numOfTags'][0], 'uint16')

        for tag in self.tags.tagList:
            tools.write(f, tag.id, 'uint16')
            tools.write(f, tag.type, 'uint16')
            tools.write(f, tag.count, 'uint32')
            tools.write(f, tag.valueOrOffset, 'uint32')

        tools.write(f, self.tags.nextIFD_Offset['nextIFD_Offset'][0], 'uint32')

        self.isTagWritten = True
        return True

    def __isPsiaTiff__(self):
        tag = self.__findTagFromId__(constant.TagIdPsiaMagicNumber)

        if not tag: 
            return False
        elif tag.valueOrOffset == constant.PsiaMagicNumber: 
            return True
        else: 
            return self.error.notPsiaTiff()

    def __findTagFromId__(self, tagId):
        if not hasattr(self, 'isTagWritten'):
            return self.error.tagsNotLoaded 

        for tag in self.tags.tagList:
            if tag.id == tagId:
                return tag

        return self.error.tagNotExist()

    def __writeStrip__(self):
        #write Strip Offsets
        tagOffset = self.__findTagFromId__(constant.TagIdStripOffsets)
        if not tagOffset: 
            return self.error.tagNotLoaded(constant.TagIdStripOffsets) 

        f = self.f
        f.seek(tagOffset.valueOrOffset)

        for i in range(tagOffset.count):
            tools.write(f, self.strip.offset['stripOffset'][0][i], 'uint32')

        #write Strip ByteCounts
        tagByteCounts = self.__findTagFromId__(constant.TagIdStripByteCounts)
        if not tagByteCounts: 
            return self.error.tagNotLoaded(constant.TagIdStripByteCounts) 

        f.seek(tagByteCounts.valueOrOffset)
        for i in range(tagByteCounts.count):
            tools.write(f, self.strip.byteCounts['stripByteCounts'][0][i], 'uint32')

        return True

    def __writeColorMap__(self):
        tag = self.__findTagFromId__(constant.TagIdColorMap)
        if not tag: 
            return self.error.tagNotLoaded(constant.TagIdColorMap) 

        f = self.f
        f.seek(tag.valueOrOffset)

        for i in range(tag.count):
            tools.write(f, self.colorMap['colorMap'][0][i], 'uint16')

        return True

    def __writeScanData__(self):
        tag = self.__findTagFromId__(constant.TagIdPsiaScanData)
        if not tag: 
            return self.error.tagNotLoaded(constant.TagIdPsiaScanData) 

        f = self.f
        f.seek(tag.valueOrOffset)

        dataCounts = self.scan.scanHeader['width'][0] * self.scan.scanHeader['height'][0]
        dataType = self.scan.scanHeader['dataType'][0]

        for i in range(dataCounts):
            ZData = self.scanData.ZData[i] / self.scan.scanHeader['dataGain'][0]
            if dataType == constant.PsiaDataTypeInt16:
                tools.write(f, int(ZData), 'int16')
            elif dataType == constant.PsiaDataTypeInt32:
                tools.write(f, int(ZData), 'int32')
            elif dataType == constant.PsiaDataTypeFloat32:
                tools.write(f, ZData, 'float32')

        return True

    def __writeScanHeader__(self):
        tag = self.__findTagFromId__(constant.TagIdPsiaScanHeader)
        if not tag: 
            return self.error.tagNotLoaded(constant.TagIdPsiaScanHeader) 

        f = self.f
        f.seek(tag.valueOrOffset)

        alist = list(self.scan.scanHeader.values())
        tools.writeList(f, alist)
        
        return True

    def __writeSpectHeader__(self):
        tag = self.__findTagFromId__(constant.TagIdPsiaSpectHeader)
        if not tag: return self.error.tagNotLoaded(constant.TagIdPsiaSpectHeader) 

        f = self.f
        f.seek(tag.valueOrOffset)

        for i in range(8):
            alist = list(self.spect.channelInfo[i].values())
            tools.writeList(f, alist)
            
        alist = list(self.spect.spectHeader.values())
        tools.writeList(f, alist)

        for i in range(self.spect.spectHeader['numOfPoints'][0]):
            if f.tell() < tag.valueOrOffset + tag.count:
                alist = list(self.spect.pointInfo[i].values())
                tools.writeList(f, alist)

        if self.spect.spectHeader['hasEXtendedHeader'][0] != 0:
            for i in range(self.spect.spectHeader['numOfPoints'][0]):
                if f.tell() < tag.valueOrOffset + tag.count:
                    alist = list(self.spect.dummyExtended[i].values())
                    tools.writeList(f, alist)
            for i in range(self.spect.spectHeader['numOfPoints'][0]):
                for j in range(self.spect.spectHeader['numOfChannels'][0]):
                    if f.tell() < tag.valueOrOffset + tag.count:
                        alist = list(self.spect.dummyInput[j].values())
                        tools.writeList(f, alist)

        return True

    def __writeSpectData__(self):
        tag = self.__findTagFromId__(constant.TagIdPsiaSpectData)
        if not tag: 
            return self.error.tagNotLoaded(constant.TagIdPsiaSpectData) 

        f = self.f
        f.seek(tag.valueOrOffset)
        
        for i in range(self.spect.spectHeader['numOfPoints'][0]):
            for j in range(self.spect.spectHeader['numOfChannels'][0]):
                if self.spect.spectHeader['dataType'][0] == constant.PsiaDataTypeInt16:
                    alist = list(self.spectData.rawDataDict[j].values())
                    tools.writeList(f, alist)
                elif self.spect.spectHeader['dataType'][0] == constant.PsiaDataTypeInt32:
                    alist = list(self.spectData.rawDataDict[j].values())
                    tools.writeList(f, alist)
                elif self.spect.spectHeader['dataType'][0] == constant.PsiaDataTypeFloat32:
                    alist = list(self.spectData.rawDataDict[j].values())
                    tools.writeList(f, alist)

        return True
    
    def __writeThumbnail__(self):
        f = self.f
        f.seek(self.strip.offset['stripOffset'][0][0])

        for i in range(len(self.thumbnail)):
            tools.write(f, self.thumbnail[i], 'byte')
        
        return True
    
if __name__ == '__main__':
    inputPath = 'C:/SWDev/NXSWDev/src/trunk/utils/pspylib/src/tests/tiff/scan_sample.tiff' # sample for scan data 
    outputPath = inputPath[:inputPath.rfind('/') + 1] + 'test_write_scan.tiff'
    data = reader.TiffReader(inputPath).data
    Writer(data, outputPath)

    inputPath = 'C:/SWDev/NXSWDev/src/trunk/utils/pspylib/src/tests/tiff/spect_sample.tiff' # sample for spect data 
    outputPath = inputPath[:inputPath.rfind('/') + 1] + 'test_write_spect.tiff'
    data = reader.TiffReader(inputPath).data
    Writer(data, outputPath)