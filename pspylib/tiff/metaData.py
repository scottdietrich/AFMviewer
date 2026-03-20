class Tag: 
    def __init__(self):
        self.id = 0
        self.type = 0
        self.count = 0
        self.valueOrOffset = 0

class MultiTag:
    def __init__(self):
        self.numOfTags = {}
        self.tagList = []
        self.nextIFD_Offset = {}

class ScanHeader:
    def __init__(self):
        self.scanHeader = {}
        
class ScanData:
    def __init__(self):
        self.ZData = []

class SpectHeader:
    def __init__(self):
        self.channelInfo = {}
        self.pointInfo = {}
        self.spectHeader = {}
        self.dummyExtended = {}
        self.dummyInput = {}

class SpectData:
    def __init__(self):
        self.rawData = []
        self.rawDataDict = {}

class Strip:
    def __init__(self):
        self.offset = {}
        self.byteCounts = {}

class MetaData:
    def __init__(self):
        self.strip = Strip()
        self.colorMap = {}
        self.thumbnail = []

class Data:
    def __init__(self):
        self.tags = MultiTag()
        self.scanHeader = ScanHeader()
        self.scanData = ScanData()
        self.spectHeader = SpectHeader()
        self.spectData = SpectData()
        self.metaData = MetaData()