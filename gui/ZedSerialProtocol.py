# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: ZedSerialProtocol.pyo
# Compiled at: 2010-10-07 11:23:32
import sys
if sys.platform[:-1] == 'linux':
    import CommDevicePosix as CommDevice
else:
    if sys.platform == 'win32':
        import CommDeviceWin32 as CommDevice
import ZedSerialEnum, struct, PrintData

class cZedSerialProtocol:

    def __init__(self, sCOMPort, aMode):
        self.oHandle = CommDevice.cCommDeviceOL(sCOMPort, aMode)
        self.bDebug = False

    def mClose(self):
        self.oHandle.mClose()

    def mSetRxTimeOut(self, RxTimeOut):
        self.oHandle.mSetRxTimeOut(RxTimeOut)

    def SetBaudrate(self, Baudrate):
        self.oHandle.SetBaudrate(Baudrate)

    def mCheckOpened(self):
        if self.oHandle._oFd != 0:
            return ZedSerialEnum.OK
        return ZedSerialEnum.INVALID_RESPONSE

    def mSetDebug(self, bDebug):
        self.bDebug = bDebug

    def mWrite(self, sData):
        self.oHandle.mFlush()
        sData = struct.pack('B', len(sData) + 1) + sData
        sData = sData + self.mCalcCrc(sData)
        iNumWr = self.oHandle.mWrite(sData)
        if self.bDebug:
            print('Wrote %d of %d' % (iNumWr, len(sData)))
            PrintData.fPrintData(sData, 0, 16)
        if iNumWr != len(sData):
            return ZedSerialEnum.WRITE_FAIL
        return ZedSerialEnum.OK

    def mRead(self, aLenReqList=[
 0]):
        sLenStr = self.oHandle.mRead(1)
        if len(sLenStr) != 1:
            return (ZedSerialEnum.READ_FAIL, 'Error receiving length field')
        iLen = struct.unpack('B', sLenStr)[0]
        if iLen == 0:
            if self.bDebug:
                print('Length 0')
            return (ZedSerialEnum.NO_RESPONSE, '')
        if aLenReqList != [0] and iLen not in aLenReqList:
            print(sLenStr)
            print(len(sLenStr))
            return (
             ZedSerialEnum.INVALID_RESPONSE, '')
        sData = self.oHandle.mRead(iLen)
        if self.bDebug:
            print('Read %d' % iLen)
            PrintData.fPrintData(sLenStr + sData, 0, 16)
        sCrc = self.mCalcCrc(sLenStr + sData[0:iLen - 1])
        if sCrc != sData[iLen - 1]:
            return (
             ZedSerialEnum.CRC_ERROR, sData)
        return (
         ZedSerialEnum.OK, sData[0:iLen - 1])

    def mCalcCrc(self, sData):
        iCrc = 0
        sStrForm = struct.unpack('B' * len(sData), sData)
        for i in range(len(sData)):
            iCrc = iCrc ^ sStrForm[i]

        return struct.pack('B', iCrc)


class cZedSerialProtocolRemote(cZedSerialProtocol):

    def __init__(self, sCOMPort, aMode, sRemoteServer):
        if sRemoteServer != '':
            try:
                ignore = dir(remoteclient)
            except:
                try:
                    sys.path.append('..\\..\\CommonFiles\\Trunk\\python\\pyro')
                    import remoteclient
                except ImportError:
                    print('Could not find remoteclient.py, please update PYTHONPATH to include the path to remoteclient.py')
                    sys.exit(1)

            else:
                print('Getting remote COM device %s on host %s' % (sCOMPort, sRemoteServer))
                try:
                    ComDeviceFactory = remoteclient.getproxy(sRemoteServer + ':ComDeviceFactory')
                    self.oHandle = ComDeviceFactory.create(sCOMPort, [38400, 'N', 8, 1])
                except ValueError as err:
                    print(err)
                    ComDeviceFactory.reset()
                    ComDeviceFactory = remoteclient.getproxy(sRemoteServer + ':ComDeviceFactory')
                    self.oHandle = ComDeviceFactory.create(sCOMPort, [38400, 'N', 8, 1])
                else:
                    print('Opened %s on %s, mCheckOpened()=%d' % (sCOMPort, sRemoteServer, self.mCheckOpened()))
                    tCommTimeouts = (sys.maxsize, 0, 5000, 0, 5000)
                    self.oHandle.mSetCommTimeouts(tCommTimeouts)
        else:
            self.oHandle = CommDevice.cCommDeviceOL(sCOMPort, aMode)
        self.bDebug = False