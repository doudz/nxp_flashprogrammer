# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: CommDeviceWin32.pyo
# Compiled at: 2009-02-05 18:12:41
import sys, string
CommException = 'CommError'
if sys.platform == 'win32':
    import pywintypes, winerror, win32file, win32con, win32api, win32event

    class cCommDeviceBase:

        def __init__(self, sDevice, aMode):
            oDCB = win32file.GetCommState(self._oFd)
            dParity = {'N': win32file.NOPARITY, 'E': win32file.EVENPARITY, 'O': win32file.ODDPARITY}
            dStop = {1: win32file.ONESTOPBIT, 2: win32file.TWOSTOPBITS}
            oDCB.BaudRate = aMode[0]
            oDCB.Parity = dParity[aMode[1]]
            oDCB.ByteSize = aMode[2]
            oDCB.StopBits = dStop[aMode[3]]
            oDCB.fBinary = 1
            oDCB.fParity = 1
            oDCB.fOutxCtsFlow = 0
            oDCB.fOutxDsrFlow = 0
            oDCB.fDtrControl = win32file.DTR_CONTROL_DISABLE
            oDCB.fDsrSensitivity = 0
            oDCB.fTXContinueOnXoff = 0
            oDCB.fOutX = 0
            oDCB.fInX = 0
            oDCB.fErrorChar = 0
            oDCB.fNull = 0
            oDCB.fRtsControl = win32file.RTS_CONTROL_ENABLE
            oDCB.fAbortOnError = 0
            win32file.SetCommState(self._oFd, oDCB)
            self.RxTimeOut = 1000
            self.TxTimeOut = 1000

        def __del__(self):
            self.mClose()

        def mCheckOpened(self):
            return self._oFd != 0

        def mDisableRTS(self):
            oDCB = win32file.GetCommState(self._oFd)
            oDCB.fRtsControl = win32file.RTS_CONTROL_DISABLE
            win32file.SetCommState(self._oFd, oDCB)

        def mEnableRTS(self):
            oDCB = win32file.GetCommState(self._oFd)
            oDCB.fRtsControl = win32file.RTS_CONTROL_ENABLE
            win32file.SetCommState(self._oFd, oDCB)

        def mSetRTS(self, bState):
            if bState:
                self.mEnableRTS()
            else:
                self.mDisableRTS()

        def SetBaudrate(self, Baudrate):
            oDCB = win32file.GetCommState(self._oFd)
            oDCB.BaudRate = Baudrate
            win32file.SetCommState(self._oFd, oDCB)

        def mClose(self):
            if self._oFd:
                win32file.CloseHandle(self._oFd)
                self._oFd = 0

        def mShutdown(self):
            self.mClose()

        def mSetRxTimeOut(self, RxTimeOut):
            self.RxTimeOut = RxTimeOut
            tCommTimeouts = (sys.maxsize, 0, self.RxTimeOut, 0, self.TxTimeOut)
            self.mSetCommTimeouts(tCommTimeouts)

        def mGetCommTimeouts(self):
            return win32file.GetCommTimeouts(self._oFd)

        def mFlush(self):
            if self._oFd:
                win32file.PurgeComm(self._oFd, win32file.PURGE_TXABORT | win32file.PURGE_RXABORT | win32file.PURGE_TXCLEAR | win32file.PURGE_RXCLEAR)

        def mSetCommTimeouts(self, tCommTimeouts):
            win32file.SetCommTimeouts(self._oFd, tCommTimeouts)


    class cCommDevice(cCommDeviceBase):

        def __init__(self, sDevice, sMode):
            try:
                sDevice = '\\\\.\\' + sDevice
                self._oFd = win32file.CreateFile(sDevice, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0, None, win32con.OPEN_EXISTING, 0, 0)
            except:
                print('Failed to open COM port ' + sDevice)
                self._oFd = 0
                raise CommException
                return

            tCommTimeouts = (
             sys.maxsize, 0, 1000, 0, 1000)
            win32file.SetCommTimeouts(self._oFd, tCommTimeouts)
            win32file.PurgeComm(self._oFd, win32file.PURGE_TXABORT | win32file.PURGE_RXABORT | win32file.PURGE_TXCLEAR | win32file.PURGE_RXCLEAR)
            cCommDeviceBase.__init__(self, sDevice, sMode)
            return

        def mRead(self, iLen):
            iOl, sData = win32file.ReadFile(self._oFd, iLen)
            return sData

        def mWrite(self, sData):
            iOl, iNumWr = win32file.WriteFile(self._oFd, sData)
            return iNumWr


    class cCommDeviceOL(cCommDeviceBase):

        def __init__(self, sDevice, sMode):
            oSecurityAttributes = pywintypes.SECURITY_ATTRIBUTES()
            oSecurityAttributes.bInheritHandle = 1
            try:
                sDevice = '\\\\.\\' + sDevice
                self._oFd = win32file.CreateFile(sDevice, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0, oSecurityAttributes, win32con.OPEN_EXISTING, win32file.FILE_FLAG_OVERLAPPED, 0)
            except:
                print('Failed to open COM port' + sDevice)
                self._oFd = 0
                return

            win32file.SetCommMask(self._oFd, win32file.EV_RXCHAR)
            win32file.SetupComm(self._oFd, 4096, 4096)
            win32file.PurgeComm(self._oFd, win32file.PURGE_TXABORT | win32file.PURGE_RXABORT | win32file.PURGE_TXCLEAR | win32file.PURGE_RXCLEAR)
            tCommTimeouts = (1000, 2, 2000, 2, 1000)
            win32file.SetCommTimeouts(self._oFd, tCommTimeouts)
            cCommDeviceBase.__init__(self, sDevice, sMode)

        def mRead(self, iLen):
            oOl = pywintypes.OVERLAPPED()
            oOl.hEvent = win32event.CreateEvent(None, 1, 0, None)
            if not oOl.hEvent:
                print('Could not create overlapped handle')
                raise CommException
            iEr, sData = win32file.ReadFile(self._oFd, iLen, oOl)
            if iEr == winerror.ERROR_IO_PENDING:
                try:
                    iNumRd = win32file.GetOverlappedResult(self._oFd, oOl, 1)
                except win32api.error:
                    print('...wait error')
                    raise CommException

            oOl.hEvent.Close()
            return sData

        def mWrite(self, sData):
            oOl = pywintypes.OVERLAPPED()
            oOl.hEvent = win32event.CreateEvent(None, 1, 0, None)
            if not oOl.hEvent:
                print('could not create overlapped handle')
                return 0
            iEr, iNumWr = win32file.WriteFile(self._oFd, sData, oOl)
            if iNumWr == 0:
                if iEr == winerror.ERROR_IO_PENDING:
                    try:
                        iNumWr = win32file.GetOverlappedResult(self._oFd, oOl, 1)
                    except win32api.error:
                        raise CommException

            oOl.hEvent.Close()
            return iNumWr

        def mFlush(self):
            if self._oFd:
                win32file.PurgeComm(self._oFd, win32file.PURGE_TXABORT | win32file.PURGE_RXABORT | win32file.PURGE_TXCLEAR | win32file.PURGE_RXCLEAR)

        def mClose(self):
            self.mFlush()
            cCommDeviceBase.mClose(self)


else:
    print('Only Win32 currently supported')

def fMain():
    pass


if __name__ == '__main__':
    fMain()