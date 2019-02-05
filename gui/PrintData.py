# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: PrintData.pyo
# Compiled at: 2005-05-24 16:39:48
import struct

def fPrintData(sData, iBase, iNumPerLine, iFormat=0, iMode=0, oDest=None):
    iOffset = 0
    iBufSize = len(sData)
    while iBufSize > 0:
        if iBufSize < iNumPerLine:
            iNumPerLine = iBufSize
            fDisplayDataLine(sData[iOffset:], iBase, iOffset, iNumPerLine, iFormat, iMode, oDest)
            iBufSize = 0
        else:
            fDisplayDataLine(sData[iOffset:iOffset + iNumPerLine], iBase, iOffset, iNumPerLine, iFormat, iMode, oDest)
            iOffset = iOffset + iNumPerLine
            iBufSize = iBufSize - iNumPerLine


def fDisplayDataLine(sData, iBase, iOffset, iNumPerLine, iFormat, iMode, oDest):
    if iFormat == 1:
        iNumPerLine = iNumPerLine >> 1
        sAddrFmt = '%08X: '
        sDataFmt = '%04X '
        sUnpack = '%dH' % iNumPerLine
    else:
        if iFormat == 2:
            iNumPerLine = iNumPerLine >> 2
            sAddrFmt = '%08X: '
            sDataFmt = '%08X '
            sUnpack = '%dL' % iNumPerLine
        else:
            if iFormat == 3:
                iNumPerLine = iNumPerLine >> 2
                sAddrFmt = '%06x '
                sDataFmt = '%08x '
                sUnpack = '>%dL' % iNumPerLine
            else:
                sAddrFmt = '%08X: '
                sDataFmt = '%02X '
                sUnpack = '%dB' % iNumPerLine
    if iMode == 1:
        oDest.AppendText(sAddrFmt % (iBase + iOffset) + sDataFmt * iNumPerLine % struct.unpack(sUnpack, sData) + '\n')
    else:
        if iMode == 2:
            sLine = sAddrFmt % (iBase + iOffset) + sDataFmt * iNumPerLine % struct.unpack(sUnpack, sData)
            oDest.write(sLine[:-1] + '\n')
        else:
            print(sAddrFmt % (iBase + iOffset) + sDataFmt * iNumPerLine % struct.unpack(sUnpack, sData))


def fMain():
    sData = struct.pack('16b', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    fPrintData(sData, 256, 8, 0, 0)
    fPrintData(sData, 512, 8, 1, 0)
    fPrintData(sData, 768, 8, 2, 0)
    fPrintData(sData, 768, 8, 3, 0)


if __name__ == '__main__':
    fMain()