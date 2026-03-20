"""
TiffReader(path) Read Park Systems Tiff Data from File
Input:
    path: full file path of intended "Park Systems tiff file" 
Output: 
    tiff file: Park Systems Tiff Image
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

## Example 
    path = 'C:/SWDev/NXSWDev/src/trunk/prototypes/tiff/spect_sample.tiff' # sample for spect data
    TiffReader(path)

Copyright (c) 2018 Park Systems
"""
from pspylib.tiff import constant
from pspylib.tiff import metaData
from pspylib.tiff import tools
import numpy as np

class TiffReader: 
    def __init__(self, path:str = None):
        self.data = metaData.Data()
        self.error = constant.ErrorIndicator()

        if isinstance(path, str): 
            self.load(path)

    def load(self, path):
        self.path = path

        try: 
            self.f = open(path, 'rb')
        except FileNotFoundError: 
            return self.error.fileNotFound(path)

        self.__validateFile__()
        self.__loadTags__()

        if not self.__isPsiaTiff__(): 
            return False

        self.__loadScanHeader__()

        if self.data.scanHeader.scanHeader['dataCategory'][0] == constant.PsiaDataCategoryTopography:
            self.__loadScanData__()
        #elif self.data.scanHeader.scanHeader['dataCategory'][0] == constant.PsiaDataCategoryLineProfile: #line profile image
        elif self.data.scanHeader.scanHeader['dataCategory'][0] == constant.PsiaDataCategorySpectroscopy:
            self.__loadSpectHeaderAndData__()

        self.__loadStrip__()
        self.__loadColorMap__()
        self.__loadThumbnail__()

        self.f.close()

    def __validateFile__(self):
        f = self.f
        f.seek(0)
        
        entries = [
            ('endianess', 'uint16', 1),
            ('magicNumber', 'uint16', 1),
            ('firstIFDOffset', 'uint32', 1)
        ]
        header = tools.read(f, entries[:2])

        if (header['endianess'][0] == constant.ByteMarkLittleEndian):
            if(header['magicNumber'][0] == constant.MagicNumber):
                self.firstIFDOffset = tools.read(f, entries[2:])
                return True
        return self.error.notTiff()

    def __loadTags__(self):
        if not hasattr(self, 'firstIFDOffset'): 
            return self.error.notValidated()

        f = self.f
        tags = self.data.tags
        f.seek(self.firstIFDOffset['firstIFDOffset'][0])

        tagEntries = [
            ('numOfTags', 'uint16', 1),
            ('id', 'uint16', 1),
            ('type', 'uint16', 1),
            ('count', 'uint32', 1),
            ('valueOrOffset', 'uint32', 1),
            ('nextIFD_Offset', 'uint32', 1)
        ]

        tags.numOfTags = tools.read(f, tagEntries[:1])

        for i in range(tags.numOfTags['numOfTags'][0]):
            tag = metaData.Tag()
            tagInfo = tools.read(f, tagEntries[1:5])
        
            tag.id = tagInfo['id'][0]
            tag.type = tagInfo['type'][0]
            tag.count = tagInfo['count'][0]
            tag.valueOrOffset = tagInfo['valueOrOffset'][0]
            tags.tagList.append(tag)

        tags.nextIFD_Offset = tools.read(f, tagEntries[5:])

        self.isTagLoaded = True
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
        if not hasattr(self, 'isTagLoaded'): 
            return self.error.tagsNotLoaded()

        for tag in self.data.tags.tagList:
            if tag.id == tagId:
                return tag

        return self.error.tagNotExist()

    def __loadScanHeader__(self):
        tag = self.__findTagFromId__(constant.TagIdPsiaScanHeader)
        if not tag: 
            return self.error.tagNotLoaded(constant.TagIdPsiaScanHeader)

        f = self.f
        scan = self.data.scanHeader
        f.seek(tag.valueOrOffset)

        # note!
        # order must be kept
        entries = [
            ('dataCategory', 'int32', 1),
            ('channelName', 'uint16', 32), 
            ('headMode', 'uint16', 8),
            ('lowPassStrength', 'double64', 1),
            ('isAutoFlatten', 'int32', 1),
            ('isAcTrack', 'int32', 1),
            ('width', 'int32', 1),
            ('height', 'int32', 1), 
            ('scanRotation', 'double64', 1), 
            ('isSineScan', 'int32', 1), 
            ('overScanRatio', 'double64', 1), 
            ('isFastScanLeftToRight', 'int32', 1), 
            ('isSlowScanBottomToTop', 'int32', 1), 
            ('isXYSwapped', 'int32', 1), 
            ('scanSizeWidth', 'double64', 1), 
            ('scanSizeHeight', 'double64', 1), 
            ('scanOffsetX', 'double64', 1), 
            ('scanOffsetY', 'double64', 1), 
            ('scanRate', 'double64', 1), 
            ('setpoint', 'double64', 1), 
            ('setpointUnit', 'uint16', 8), 
            ('tipBias', 'double64', 1),
            ('sampleBias', 'double64', 1),
            ('dataGain', 'double64', 1),
            ('ZScale', 'double64', 1),
            ('ZOffset', 'double64', 1),
            ('unit', 'uint16', 8),
            ('dataMin', 'int32', 1),
            ('dataMax', 'int32', 1),
            ('dataAverage', 'int32', 1),
            ('compression', 'int32', 1),
            ('isLogScale', 'int32', 1),
            ('isSquared', 'int32', 1),
            ('zServoGain', 'double64', 1),
            ('zScannerRange', 'double64', 1),
            ('xyVoltageMode', 'uint16', 8),
            ('zVoltageMode', 'uint16', 8),
            ('xyServoMode', 'uint16', 8),
            ('dataType', 'int32', 1),
            ('numOfPddRegionX', 'int32', 1),
            ('numOfPddRegionY', 'int32', 1),
            ('ncmAmplitude', 'double64', 1),
            ('ncmFrequency', 'double64', 1),
            ('headRotation', 'double64', 1),
            ('cantileverName', 'uint16', 16),
            ('ncmDrivePercent', 'double64', 1),
            ('intensityFactor', 'double64', 1),
            ('headTilting', 'double64', 1),
            ('logAmpOffset', 'double64', 1),
            ('tipSampleDistance', 'double64', 1),
            ('zServoNcGain', 'double64', 1),
            ('zServoPGain', 'double64', 1),
            ('zServoIGain', 'double64', 1),
            ('isTapping', 'int32', 1),
            ('dataMinV2', 'double64', 1),
            ('dataMaxV2', 'double64', 1),
            ('stageX', 'double64', 1),
            ('stageY', 'double64', 1),
            ('sampleX', 'double64', 1),
            ('sampleY', 'double64', 1),
            ('imageQualityIndex', 'double64', 1),
            ('reservedForImage', 'int32', 11),
        ]

        scan.scanHeader = tools.read(f, entries)

        return True

    def __loadScanData__(self):
        tag = self.__findTagFromId__(constant.TagIdPsiaScanData)
        if not tag: 
            return self.error.tagNotLoaded(constant.TagIdPsiaScanData)

        f = self.f
        scan = self.data.scanHeader
        scanData = self.data.scanData
        f.seek(tag.valueOrOffset)

        dataCounts = scan.scanHeader['width'][0] * scan.scanHeader['height'][0]
        dataType = scan.scanHeader['dataType'][0]

        entries = [
            ('ZData_i16', 'int16', dataCounts),
            ('ZData_i32', 'int32', dataCounts),
            ('ZData_f32', 'float32', dataCounts)
        ]

        if dataType == constant.PsiaDataTypeInt16:
            ZData = tools.read(f, entries[:1])
            scanData.ZData = np.array(ZData['ZData_i16'][0]) * scan.scanHeader['dataGain'][0]
        elif dataType == constant.PsiaDataTypeInt32:
            ZData = tools.read(f, entries[1:2])
            scanData.ZData = np.array(ZData['ZData_i32'][0]) * scan.scanHeader['dataGain'][0]
        elif dataType == constant.PsiaDataTypeFloat32:
            ZData = tools.read(f, entries[2:])
            scanData.ZData = np.array(ZData['ZData_f32'][0]) * scan.scanHeader['dataGain'][0]

        return True

    def __loadSpectHeaderAndData__(self):
        tagHeader = self.__findTagFromId__(constant.TagIdPsiaSpectHeader)
        if not tagHeader: 
            return self.error.tagNotLoaded(constant.TagIdPsiaSpectHeader)

        f = self.f
        spect = self.data.spectHeader
        spectData = self.data.spectData

        # loadSpectHeader

        # note!
        # order must be kept
        f.seek(tagHeader.valueOrOffset)

        channel = [
            ('name', 'uint16', 32),
            ('unit', 'uint16', 8),
            ('gain', 'double64', 1),
            ('isXAxis', 'int32', 1),
            ('isYAxis', 'int32', 1),
        ]

        for i in range(8):
            spect.channelInfo[i] = tools.read(f, channel)

        currentOffset = f.tell()
        entries = [
            ('numOfChannels', 'int32', 1),
            ('average', 'int32', 1),
            ('numOfDataAllDir', 'int32', 1),
            ('numOfPoints', 'int32', 1),
            ('drivingChannelIndex', 'int32', 1),
            ('forwardPeriod', 'float32', 1),
            ('backwardPeriod', 'float32', 1),
            ('forwardSpeed', 'float32', 1),
            ('backwardSpeed', 'float32', 1),
            ('gridUsed', 'int32', 1),
            ('channelOffset', 'double64', 8),
            ('channelIsLog', 'int32', 8),
            ('channelIsSquared', 'int32', 8),
            ('gridNumOfColumn', 'int32', 1),
            ('hasRefImage', 'int32', 1),
            ('gridSizeWidth', 'double64', 1),
            ('gridSizeHeight', 'double64', 1),
            ('gridOffsetX', 'double64', 1),
            ('gridOffsetY', 'double64', 1),

            # F/D Spectroscopy Information
            ('ForceConstantNewtonPerMeter', 'double64', 1),
            ('SensitivityVoltPerMicroMeter', 'double64', 1),
            ('ForceLimitVolt', 'float32', 1),
            ('TimeInterval', 'float32', 1),

            # I/V Spectroscopy Information
            ('MaxVoltage', 'float32', 1),
            ('MinVoltage', 'float32', 1),
            ('StartVoltage', 'float32', 1),
            ('EndVoltage', 'float32', 1),
            ('DelayedStartTime', 'float32', 1),

            ('useZServo', 'int32', 1),
            ('sourceGain', 'double64', 1),
            ('sourceUnit', 'int16', 8),
            ('hasEXtendedHeader', 'int32', 1),
            ('spectType', 'int32', 1),
        ]
        spect.spectHeader = tools.read(f, entries)
        f.seek(currentOffset)

        if spect.spectHeader['spectType'][0] == 9:
            peSpectInfo = [
                # P/E Spectroscopy Information
                ('writingTime', 'float32', 1),
                ('waitingTime', 'float32', 1),
                ('readingTime', 'float32', 1),
                ('biasStep', 'float32', 1),
                ('numberOfLoops', 'int32', 1),
                ('usePulse', 'int32', 1),
                ('timeBeforeLightOn', 'float32', 1),
                ('timeLightDuration', 'float32', 1),
            ]

            for j in range(len(peSpectInfo)):
                entries.append(peSpectInfo[j])
        else:
            photoCurrentInfo = [
                # Photo-current Information
                ('resetLevel', 'float32', 1),
                ('resetDuration', 'float32', 1),
                ('operationLevel', 'float32', 1),
                ('operationDuration', 'float32', 1),
                ('timeBeforeReset', 'float32', 1),
                ('timeAfterReset', 'float32', 1),
                ('timeBeforeLightOn', 'float32', 1),
                ('timeLightDuration', 'float32', 1),
            ]

            for j in range(len(photoCurrentInfo)):
                entries.append(photoCurrentInfo[j])
        info = [
            # TA Information
            ('offsetTemperature', 'float32', 1),
            ('offsetSThMError', 'float32', 1),
            ('referenceTemperature', 'float32', 1),
            ('referenceProbeCurrent', 'float32', 1),
            ('referenceSThMError', 'float32', 1),
            ('dataType', 'int32', 1),
            ('setpoint', 'float32', 1),
            ('setpointUnitType', 'float32', 1),
            ('dummy', 'int32', 22)
        ]
        for i in range(len(info)):
            entries.append(info[i])

        spect.spectHeader = tools.read(f, entries)

        pointInfo = [
            ('fPosX', 'float32', 1),
            ('fPosY', 'float32', 1),
            ('fTime', 'float32', 1)
        ]
        for i in range(spect.spectHeader['numOfPoints'][0]):
            if f.tell() < tagHeader.valueOrOffset + tagHeader.count:
                spect.pointInfo[i] = tools.read(f, pointInfo)
        
        if spect.spectHeader['hasEXtendedHeader'][0] != 0:
            for i in range(spect.spectHeader['numOfPoints'][0]):
                if f.tell() < tagHeader.valueOrOffset + tagHeader.count:
                    dummyList = [('extendedReservedNum', 'int32', 10)]
                    spect.dummyExtended[i] = tools.read(f, dummyList)
            for i in range(spect.spectHeader['numOfPoints'][0]):
                for j in range(spect.spectHeader['numOfChannels'][0]):
                    if f.tell() < tagHeader.valueOrOffset + tagHeader.count:
                        offsetList = [
                            ('fOffset', 'float32', 1),
                            ('fValue', 'float32', 1),
                            ('inputReservedNum', 'int32', 8)
                        ]
                        spect.dummyInput[j] =  tools.read(f, offsetList)
                        dummyInput = [spect.dummyInput[j]['fOffset'][0], spect.dummyInput[j]['fValue'][0], spect.dummyInput[j]['inputReservedNum'][0]]

        # load spectData
        tagData = self.__findTagFromId__(constant.TagIdPsiaSpectData)
        if not tagData: 
            return self.error.tagNotLoaded(constant.TagIdPsiaSpectData)

        f.seek(tagData.valueOrOffset)

        rawDataList = []
        entries = [
            ('rawData_i16', 'int16', spect.spectHeader['numOfDataAllDir'][0]),
            ('rawData_i32', 'int32', spect.spectHeader['numOfDataAllDir'][0]),
            ('rawData_f32', 'float32', spect.spectHeader['numOfDataAllDir'][0])
        ]

        for i in range(spect.spectHeader['numOfPoints'][0]):
            for j in range(spect.spectHeader['numOfChannels'][0]):
                if spect.spectHeader['dataType'][0] == constant.PsiaDataTypeInt16:
                    spectData.rawDataDict[j] = tools.read(f, entries[:1])
                    rawDataList.append(spectData.rawDataDict[j]['rawData_i16'][0])
                elif spect.spectHeader['dataType'][0] == constant.PsiaDataTypeInt32:
                    spectData.rawDataDict[j] = tools.read(f, entries[1:2])
                    rawDataList.append(spectData.rawDataDict[j]['rawData_i32'][0])
                elif spect.spectHeader['dataType'][0] == constant.PsiaDataTypeFloat32:
                    spectData.rawDataDict[j] = tools.read(f, entries[2:])
                    rawDataList.append(spectData.rawDataDict[j]['rawData_f32'][0])
            spectData.rawData.append(rawDataList)
                
        spectData.rawData = np.array(spectData.rawData)
        
        return True

    def __loadStrip__(self):
        # load Strip Offsets
        tagOffset = self.__findTagFromId__(constant.TagIdStripOffsets)
        if not tagOffset: 
            return self.error.tagNotLoaded(constant.TagIdStripOffsets)

        f = self.f
        strip = self.data.metaData.strip
        f.seek(tagOffset.valueOrOffset)

        entries = [('stripOffset', 'uint32', tagOffset.count)]
        strip.offset = tools.read(f, entries)

        # load Strip ByteCounts
        tagByteCounts = self.__findTagFromId__(constant.TagIdStripByteCounts)
        if not tagByteCounts: 
            return self.error.tagNotLoaded(constant.TagIdStripByteCounts)

        f.seek(tagByteCounts.valueOrOffset)

        entries = [('stripByteCounts', 'uint32', tagByteCounts.count)]
        strip.byteCounts = tools.read(f, entries)

        return True

    def __loadColorMap__(self):
        tag = self.__findTagFromId__(constant.TagIdColorMap)
        if not tag: 
            return self.error.tagNotLoaded(constant.TagIdColorMap)

        f = self.f
        f.seek(tag.valueOrOffset)

        entries = [('colorMap', 'uint16', tag.count)]
        self.data.metaData.colorMap = tools.read(f, entries)

        return True

    def __loadThumbnail__(self):
        f = self.f
        strip = self.data.metaData.strip
        thumbnailList = self.data.metaData.thumbnail

        for i in range(len(strip.offset['stripOffset'][0])):
            f.seek(strip.offset['stripOffset'][0][i])

            entries = [('thumbnail', 'byte', strip.byteCounts['stripByteCounts'][0][i])]
            thumbnail = tools.read(f, entries)
            thumbnailList += thumbnail['thumbnail'][0]

        thumbnailList = np.array(thumbnailList)

        return True

if __name__ == '__main__':
    path = 'C:/SWDev/NXSWDev/src/trunk/utils/pspylib/src/tests/tiff/scan_sample.tiff' # sample for scan data
    #path = 'C:/SWDev/NXSWDev/src/trunk/utils/pspylib/src/tests/tiff/spect_sample.tiff' # sample for spect data

    a = TiffReader(path)