ByteMarkLittleEndian = 0x4949
ByteMarkBigEndian = 0x4d4d
MagicNumber = 0x2a
PsiaMagicNumber = 0x0e031301

TagIdImageWidth = 256
TagIdImageLength = 257
TagIdBitsPerSample = 258
TagIdCompression = 259
TagIdPhotoMetricInterpretation = 262
TagIdStripOffsets = 273
TagIdOrientation = 274
TagIdSamplesPerPixel = 277
TagIdRowsPerStrip = 278
TagIdStripByteCounts = 279
TagIdXResolution = 282
TagIdYResolution = 283
TagIdPlanarConfiguration = 284
TagIdResolutionUnit = 296
TagIdSoftware = 305
TagIdDateTime = 306
TagIdColorMap = 320
TagIdPsiaMagicNumber = 50432
TagIdPsiaVersion = 50433
TagIdPsiaScanData = 50434
TagIdPsiaScanHeader = 50435
TagIdPsiaComments = 50436
TagIdPsiaLineProfileHeader = 50437
TagIdPsiaSpectHeader = 50438
TagIdPsiaSpectData = 50439
TagIdPsiaPddRegionData = 50440
TagIdPsiaReserved = 50441

TagDataTypeByte8 = 1
TagDataTypeAscii8 = 2
TagDataTypeShort16 = 3
TagDataTypeLong32 = 4
TagDataTypeRational64 = 5
TagDataTypeSByte8 = 6
TagDataTypeUndefined8 = 7
TagDataTypeSShort16 = 8
TagDataTypeSLong32 = 9
TagDataTypeSRational64 = 10
TagDataTypeFloat32 = 11
TagDataTypeDouble64 = 12

CompressionNA = 1
CompressionHuffmanRle = 2
CompressionPackBits = 3

PhtometricGrayWhiteZero = 0
PhtometricGrayBlackZero = 1
PhtometricRgb = 2
PhtometricPalette = 3

PhtometricTopography = 0
PhtometricLineProfile = 1
PhtometricSpectroscopy = 2

PsiaDataCategoryTopography = 0
PsiaDataCategoryLineProfile = 1
PsiaDataCategorySpectroscopy = 2

PsiaDataTypeInt16 = 0
PsiaDataTypeInt32 = 1
PsiaDataTypeFloat32 = 2

class ErrorIndicator:
    def __init__(self):
        self.tagNames = {
            TagIdPsiaScanHeader: 'Scan header',
            TagIdPsiaScanData: 'Scan data',
            TagIdPsiaSpectHeader: 'Spect header',
            TagIdPsiaSpectData: 'Spect data',
            TagIdStripOffsets: 'Strip offsets',
            TagIdStripByteCounts: 'Strip byte counts',
            TagIdColorMap: 'Color map'
        }

    def fileNotFound(self, path):
        print('%s not found.' % path)
        return False

    def notTiff(self):
        print('The format of this file is not TIFF with little endian.')
        return False

    def notValidated(self):
        print('This file is not validated.')
        return False

    def notPsiaTiff(self):
        print('The format of this file is not PSIA TIFF.')
        return False

    def tagsNotLoaded(self):
        print('Tags are not loaded.')
        return False

    def tagNotExist(self):
        print('This ID of tag is not exist.')
        return False

    def tagNotLoaded(self, tagId):
        print('%s tag is not loaded.' % self.tagNames[tagId])
        return False

