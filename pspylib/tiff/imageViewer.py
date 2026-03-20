import sys
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
import numpy as np
import matplotlib.pyplot as plt

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap, qRgb
from PyQt5.QtWidgets import QApplication, QLabel

from pspylib.tiff import reader, writer, tools, constant, metaData
from reader import * 

class TiffImageViewer_PyQt:
    def __init__(self, reader:TiffReader):
        self.label = QLabel()
        self.labelColorMap = QLabel()

        self.show(reader)

    def show(self, reader:TiffReader):
        if not isinstance(reader, TiffReader):
            print('The argument is not the object of TiffReader class.')
            return False

        colorMap = reader.data.metaData.colorMap['colorMap'][0]
        self.colorMap = self.__makeColorMap__(colorMap)

        scan = reader.data.scanHeader
        scanData = reader.data.scanData
        image = self.__dataToImage__(scanData.ZData, scan.scanHeader['width'][0], scan.scanHeader['height'][0], self.colorMap)

        fileName = reader.path.split('/')[-1]
        title = 'Topography - %s' % fileName

        self.__showQImage__(self.label, image, title)
    
    def showColorMap(self):
        if not hasattr(self, 'colorMap'):
            print('Color map is not constructed yet.')
            return False

        width = len(self.colorMap)
        image = self.__dataToImage__([], width, width, self.colorMap)

        title = 'Color Map'

        self.__showQImage__(self.labelColorMap, image, title)
        self.__adjustLabelPosition__()

    def __showQImage__(self, label:QLabel, image:QImage, title:str):
        pixmap = QPixmap.fromImage(image)

        label.setWindowTitle(title)
        label.setPixmap(pixmap)
        label.show()
    
    def __makeColorMap__(self, colorMap):
        length = int(len(colorMap) / 3)
        return [qRgb(colorMap[x] >> 8, colorMap[x + length] >> 8, colorMap[x + length * 2] >> 8) for x in range(length)]

    def __dataToImage__(self, data, width, height, colorMap):
        # To call this method in order to display a color map,
        # pass a empty list as a data argument.

        image = QImage(width, height, QImage.Format_ARGB32)

        try:
            minData = min(data)
            divider = max(data) - minData
            isDataEmpty = False

            if divider == 0:
                print("The values in Data are all same.")
                return image
        except ValueError: 
            isDataEmpty = True

        for i in range(width * height):
            index = int(i / width)
            x = i % width
            y = height - 1 - index

            if not isDataEmpty:
                norm = int(256 * (data[i] - minData) / divider)
                if norm == 256: 
                    norm = 255
            else: 
                norm = index

            image.setPixel(x, y, colorMap[norm])

        return image

    def __adjustLabelPosition__(self):
        x = self.label.x()
        widthData = self.label.frameGeometry().width()
        widthColorMap = self.labelColorMap.frameGeometry().width()

        if x + widthData + widthColorMap < 1920 * 2: 
            x += widthData
        else: 
            x -= widthColorMap

        y = self.label.y()

        self.labelColorMap.move(x, y)

class TiffImageViewer_pyplot:
    def __init__(self, reader:TiffReader):
        self.path = reader.path
        self.show(reader)

    def show(self, reader:TiffReader):
        if not isinstance(reader, TiffReader):
            print('The argument is not the object of TiffReader class.')
            return False

        self.data = reader.data

        self.__makeGrid__()
        self.__makeColorMap__()
        self.__showImage__()

    def __makeGrid__(self):
        data = self.data

        xStart = data.scanHeader.scanHeader['scanOffsetX'][0] - data.scanHeader.scanHeader['scanSizeWidth'][0] / 2
        yStart = data.scanHeader.scanHeader['scanOffsetY'][0] - data.scanHeader.scanHeader['scanSizeHeight'][0] / 2

        xEnd = xStart + data.scanHeader.scanHeader['scanSizeWidth'][0]
        yEnd = yStart + data.scanHeader.scanHeader['scanSizeHeight'][0]

        dx = data.scanHeader.scanHeader['scanSizeWidth'][0] / data.scanHeader.scanHeader['width'][0]
        dy = data.scanHeader.scanHeader['scanSizeHeight'][0] / data.scanHeader.scanHeader['height'][0]

        self.y, self.x = np.mgrid[slice(yStart, yEnd + dy, dy), slice(xStart, xEnd + dx, dx)]
        self.z = np.copy(data.scanData.ZData).reshape(data.scanHeader.scanHeader['height'][0], data.scanHeader.scanHeader['width'][0])

    def __makeColorMap__(self):
        z = self.z

        colorMap = self.data.metaData.colorMap['colorMap'][0]
        length = int(len(colorMap) / 3)
        self.cmap = colors.ListedColormap([(colorMap[x] / 0xff00, colorMap[x + length] / 0xff00, colorMap[x + length * 2] / 0xff00) for x in range(length)])

        levels = MaxNLocator(nbins=self.cmap.N).tick_values(z.min(), z.max())
        self.norm = colors.BoundaryNorm(levels, ncolors=self.cmap.N, clip=True)

    def __showImage__(self):
        fig, ax0 = plt.subplots()
        image = ax0.pcolormesh(self.x, self.y, self.z, cmap = self.cmap, norm = self.norm)
        ax0.set_aspect(1)

        fig.colorbar(image, ax = ax0)
        ax0.set_title(self.path.split('/')[-1])

        micro = chr(0x00b5)
        plt.xlabel('X (%sm)' % micro)
        plt.ylabel('Y (%sm)' % micro)
        plt.show()

def showTopography_PyQt():
    # Enter the main event loop
    app = QApplication(sys.argv)

    path = 'C:/SWDev/NXSWDev/src/trunk/utils/pspylib/src/tests/tiff/scan_sample.tiff' # sample for scan data
    reader = TiffReader(path)
    viewer = TiffImageViewer_PyQt(reader)

    # If you want to display a color map, execute below line.
    viewer.showColorMap()

    app.exec_()

def showTopography_pyplot():
    path = 'C:/SWDev/NXSWDev/src/trunk/utils/pspylib/src/tests/tiff/scan_sample.tiff'
    #path = 'D:/Users/koala/Downloads/1.tiff.tiff'
    reader = TiffReader(path)
    TiffImageViewer_pyplot(reader)

def listToText(textList):
    return ''.join(map(chr, textList[:textList.index(0)]))

def textToList(text, length):
    return [ord(text[x]) if len(text) > x else 0 for x in range(length)]


from writer import *

def test():
    path = 'C:/SWDev/NXSWDev/src/trunk/utils/pspylib/src/tests/tiff/scan_sample.tiff'
    reader = TiffReader(path)

    # Ex.1 change channel_name
    name = reader.data.scanHeader.scanHeader['channelName'][0]
    print(listToText(name))
    name = textToList('Height', len(name))
    print(name)
    print(listToText(name))
    for x in range(len(reader.data.scanHeader.scanHeader['channelName'][0])):
        reader.data.scanHeader.scanHeader['channelName'][0][x] = name[x]

    #Ex.2 change head mode
    head_mode = reader.data.scanHeader.scanHeader['headMode'][0]
    print(listToText(head_mode))
    head_mode = textToList('Contact', len(head_mode))
    print(head_mode)
    print(listToText(head_mode))
    for x in range(len(reader.data.scanHeader.scanHeader['headMode'][0])):
        reader.data.scanHeader.scanHeader['headMode'][0][x] = head_mode[x]

    outputPath = path[:path.rfind('/') + 1] + 'temp.tiff'
    Writer(reader.data, outputPath)

# test()

def printSpectroscopyChannels(spect):
    for i in range(len(spect.channelInfo)):
        if spect.channelInfo[i]['name'][0][0] == 0:
            print('Total %d channels' % i)
            break

        print('%d: %s (%s)' % (i, listToText(spect.channelInfo[i]['name'][0]), listToText(spect.channelInfo[i]['unit'][0])))

def showSpectroscopyData():
    path = 'C:/SWDev/NXSWDev/src/trunk/utils/pspylib/src/tests/tiff/spect_sample.tiff' # sample for P/E Spectroscopy data
    reader = TiffReader(path)
    spectHeader = reader.data.spectHeader
    spectData = reader.data.spectData

    printSpectroscopyChannels(spectHeader)

    point = 0
    sourceX = 5 # Time Stamp
    sourceY = 4 # PFM Bias

    loopCount = spectHeader.spectHeader['numberOfLoops'][0]
    loopIndex = 0

    if loopIndex < 0: loopIndex = 0
    elif loopIndex >= loopCount: loopIndex = loopCount - 1

    isLoopCountWrong = False
    if spectHeader.spectHeader['numOfDataAllDir'][0] % loopCount:
        isLoopCountWrong = True
        print('loopCount variable has a wrong value.')

    dataLength = int(spectHeader.spectHeader['numOfDataAllDir'][0] / loopCount)
    start = loopIndex * dataLength
    end = start + dataLength

    if isLoopCountWrong and (loopIndex == loopCount - 1): 
        end = spectHeader.spectHeader['numOfDataAllDir'][0]

    x = spectData.rawData[point][sourceX][start:end]
    y = spectData.rawData[point][sourceY][start:end]


    # If you want to display all, execute below lines.
    # x = spectData.rawData[point][sourceX]
    # y = spectData.rawData[point][sourceY]

    plt.xlabel('%s (%s)' % (listToText(spectHeader.channelInfo[sourceX]['name'][0]), listToText(spectHeader.channelInfo[sourceX]['unit'][0])))
    plt.ylabel('%s (%s)' % (listToText(spectHeader.channelInfo[sourceY]['name'][0]), listToText(spectHeader.channelInfo[sourceY]['unit'][0])))
    plt.plot(x, y)
    plt.show()

#showTopography_PyQt()
showTopography_pyplot()
#showSpectroscopyData()