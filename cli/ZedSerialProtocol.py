# uncompyle6 version 3.2.5
# Python bytecode 2.6 (62161)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: ZedSerialProtocol.pyo
# Compiled at: 2013-01-30 12:04:11
import sys, serial, struct, logging, time, ZedSerialEnum

class cZedSerialProtocol:

    def __init__(self, sCOMPort, iBaudrate, RxTimeOut=1000):
        self.logger = logging.getLogger('ZedSerialProtocol(%s)' % sCOMPort)
        self.logger.info('Open device, baudrate %d, timeout %d' % (iBaudrate, RxTimeOut))
        self.sCOMPort = sCOMPort
        self.bDebug = False
        try:
            self.oHandle = serial.Serial(sCOMPort, baudrate=iBaudrate, timeout=float(RxTimeOut / 1000))
        except serial.serialutil.SerialException as e:
            self.logger.debug('Error opening serial port (%s)' % str(e))
            self.oHandle = None
            return
        else:
            if self.oHandle.isOpen():
                self.oHandle.flushInput()
                self.oHandle.flushOutput()

        return

    def mClose(self):
        self.logger.info('Close')
        if self.oHandle:
            self.oHandle.close()
            self.oHandle = None
        return

    def mSetRxTimeOut(self, RxTimeOut):
        timeout = float(RxTimeOut / 1000)
        self.logger.debug('Set timeout: %f' % timeout)
        if self.oHandle:
            self.oHandle.timeout = timeout

    def SetBaudrate(self, iBaudrate):
        self.logger.debug('Set baudrate %d' % iBaudrate)
        if self.oHandle:
            self.oHandle.baudrate = iBaudrate

    def mCheckOpened(self):
        self.logger.debug('Is open')
        if self.oHandle:
            if self.oHandle.isOpen():
                return ZedSerialEnum.OK
        return ZedSerialEnum.INVALID_RESPONSE

    def mSetRTS(self, RTSstate):
        self.logger.debug('Set RTS: %s' % str(RTSstate))
        if self.oHandle:
            self.oHandle.setRTS(RTSstate)

    def mSetDebug(self, bDebug):
        self.bDebug = bDebug

    def mWrite(self, sData):
        self.logger.debug('Write: %s' % str(list(sData)))
        sData = struct.pack('B', len(sData) + 1) + sData
        sData = sData + self.mCalcCrc(sData)
        if self.oHandle:
            iNumWr = self.oHandle.write(sData)
            self.logger.debug('Wrote %d of %d' % (iNumWr, len(sData)))
        else:
            self.logger.error('Attempt to write to closed serial device')
            iNumWr = 0
        if iNumWr != len(sData):
            return ZedSerialEnum.WRITE_FAIL
        return ZedSerialEnum.OK

    def mRead(self, aLenReqList=[
 0]):
        self.logger.debug('Read')
        if not self.oHandle:
            self.logger.error('Attempt to read from closed serial device')
            return ZedSerialEnum.READ_FAIL
        sLenStr = self.oHandle.read(1)
        if len(sLenStr) != 1:
            self.logger.info('Read error receiving length field')
            return (
             ZedSerialEnum.READ_FAIL, 'Error receiving length field')
        iLen = struct.unpack('B', sLenStr)[0]
        if iLen == 0:
            self.logger.info('Received invalid length (0)')
            return (
             ZedSerialEnum.NO_RESPONSE, '')
        if aLenReqList != [0] and iLen not in aLenReqList:
            self.logger.info('Received invalid length (expected %s, got %d)' % (str(aLenReqList), iLen))
            return (
             ZedSerialEnum.INVALID_RESPONSE, '')
        self.logger.debug('Reading %d bytes' % iLen)
        sData = self.oHandle.read(iLen)
        if iLen != len(sData):
            self.logger.debug('Read incorrect length (expected %d, got %d)' % (iLen, len(sData)))
            return (
             ZedSerialEnum.INVALID_RESPONSE, '')
        self.logger.debug('Read %d bytes' % iLen)
        self.logger.debug('Read %s' % str(list(sLenStr + sData)))
        sCrc = self.mCalcCrc(sLenStr + sData[0:iLen - 1])
        if sCrc != sData[iLen - 1]:
            self.logger.info('CRC failed (calculated 0x%x, got 0x%x)' % (ord(sCrc), ord(sData[iLen - 1])))
            return (
             ZedSerialEnum.CRC_ERROR, sData)
        self.logger.debug('Read %d bytes OK' % iLen)
        return (
         ZedSerialEnum.OK, sData[0:iLen - 1])

    def mCalcCrc(self, sData):
        iCrc = 0
        sStrForm = struct.unpack('B' * len(sData), sData)
        for i in range(len(sData)):
            iCrc = iCrc ^ sStrForm[i]

        return struct.pack('B', iCrc)


class cDeviceControlBase:

    def __init__(self, sCOMPort):
        self.logger = logging.getLogger('cDeviceControlDummy(%s)' % sCOMPort)

    def mEnterProgrammingMode(self):
        self.logger.info('EnterProgrammingMode')

    def mReset(self):
        self.logger.info('Reset')


try:
    import d2xx

    class cDeviceControl(cDeviceControlBase):

        def __init__(self, sCOMPort):
            self.logger = logging.getLogger('cDeviceControl(%s)' % sCOMPort)
            self.sComPort = sCOMPort

        def _mGetHandle(self):
            d = d2xx.listDevices()
            comindex = -1
            counter = 0
            if d != 0:
                for j in d:
                    try:
                        hl = d2xx.open(counter)
                        a = hl.getComPortNumber()
                        a = 'COM' + str(a)
                        if self.sComPort == a:
                            return hl
                        hl.close()
                    except Exception as e:
                        self.logger.debug('Exception communicating with FTDI device (%s)' % str(e))
                    else:
                        counter += 1

            return

        def mEnterProgrammingMode(self):
            h = self._mGetHandle()
            if h:
                h.purge()
                h.setBitMode(192, 32)
                time.sleep(0.2)
                h.setBitMode(196, 32)
                time.sleep(0.2)
                h.setBitMode(204, 32)
                time.sleep(0.2)
                h.setBitMode(0, 32)
                time.sleep(0.2)
                h.close()
                self.logger.info('Program-Reset Sent')

        def mReset(self):
            h = self._mGetHandle()
            if h:
                h.setBitMode(64, 32)
                time.sleep(0.2)
                h.setBitMode(0, 32)
                time.sleep(0.2)
                h.close()
                self.logger.info('Reset Sent')


except ImportError:

    class cDeviceControl(cDeviceControlBase):
        pass