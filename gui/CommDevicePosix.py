# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: CommDevicePosix.pyo
# Compiled at: 2005-06-29 16:02:04
import sys
CommException = 'CommError'
if sys.platform[:5] == 'linux':
    import os, fcntl, termios, struct, string, select
    if sys.hexversion < 33620208:
        import TERMIOS
    else:
        TERMIOS = termios
    if sys.hexversion < 33685744:
        import FCNTL
    else:
        FCNTL = fcntl
    LIDX_ATTR_IFLAG = 0
    LIDX_ATTR_OFLAG = 1
    LIDX_ATTR_CFLAG = 2
    LIDX_ATTR_LFLAG = 3
    LIDX_ATTR_ISPEED = 4
    LIDX_ATTR_OSPEED = 5
    LIDX_ATTR_CC = 6

    class cCommDeviceBase:

        def __init__(self, sDevice, aMode):
            dBaudEnumToRate = {}
            dBaudRateToEnum = {}
            for iRate in (0, 50, 75, 110, 134, 150, 200, 300, 600, 1200, 2400, 4800,
                          9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000,
                          576000, 921600):
                try:
                    iEnum = eval('TERMIOS.B' + str(iRate))
                    dBaudEnumToRate[iEnum] = iRate
                    dBaudRateToEnum[iRate] = iEnum
                except:
                    pass

            try:
                aAttr = termios.tcgetattr(self._oFd)
            except:
                print('Failed to open COM port')
                self._oFd = None
                return
            else:
                aAttr[LIDX_ATTR_ISPEED] = aAttr[LIDX_ATTR_OSPEED] = dBaudRateToEnum[aMode[0]]
                aAttr[LIDX_ATTR_IFLAG] = aAttr[LIDX_ATTR_IFLAG] & ~(TERMIOS.INPCK | TERMIOS.ISTRIP)
                if aMode[1] == 'N':
                    aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] & ~(TERMIOS.PARENB | TERMIOS.PARODD)
                else:
                    if aMode[1] == 'E':
                        aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] & ~TERMIOS.PARODD
                        aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] | TERMIOS.PARENB
                    else:
                        if aMode[1] == 'O':
                            aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] | (TERMIOS.PARENB | TERMIOS.PARODD)
                aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] & ~TERMIOS.CSIZE
                if aMode[2] == 8:
                    aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] | TERMIOS.CS8
                else:
                    if aMode[2] == 7:
                        aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] | TERMIOS.CS7
                    else:
                        if aMode[2] == 6:
                            aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] | TERMIOS.CS6
                        else:
                            if aMode[2] == 5:
                                aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] | TERMIOS.CS5
                if aMode[3] == 1:
                    aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] & ~TERMIOS.CSTOPB
                else:
                    if aMode[3] == 2:
                        aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] | TERMIOS.CSTOPB
                if hasattr(TERMIOS, 'IXANY'):
                    aAttr[LIDX_ATTR_IFLAG] = aAttr[LIDX_ATTR_IFLAG] & ~(TERMIOS.IXON | TERMIOS.IXOFF | TERMIOS.IXANY)
                else:
                    aAttr[LIDX_ATTR_IFLAG] = aAttr[LIDX_ATTR_IFLAG] & ~(TERMIOS.IXON | TERMIOS.IXOFF)
                if hasattr(TERMIOS, 'CRTSCTS'):
                    aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] & ~TERMIOS.CRTSCTS
                else:
                    if hasattr(TERMIOS, 'CNEW_RTSCTS'):
                        aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] & ~TERMIOS.CNEW_RTSCTS
                aAttr[LIDX_ATTR_CFLAG] = aAttr[LIDX_ATTR_CFLAG] | (TERMIOS.CLOCAL | TERMIOS.CREAD)
                aAttr[LIDX_ATTR_LFLAG] = aAttr[LIDX_ATTR_LFLAG] & ~(TERMIOS.ICANON | TERMIOS.ECHO | TERMIOS.ECHOE | TERMIOS.ECHOK | TERMIOS.ECHONL | TERMIOS.ECHOCTL | TERMIOS.ECHOKE | TERMIOS.ISIG | TERMIOS.IEXTEN)
                aAttr[LIDX_ATTR_OFLAG] = aAttr[LIDX_ATTR_OFLAG] & ~TERMIOS.OPOST
                if hasattr(TERMIOS, 'IUCLC'):
                    aAttr[LIDX_ATTR_IFLAG] = aAttr[LIDX_ATTR_IFLAG] & ~(TERMIOS.INLCR | TERMIOS.IGNCR | TERMIOS.ICRNL | TERMIOS.IUCLC | TERMIOS.IGNBRK)
                aAttr[LIDX_ATTR_IFLAG] = aAttr[LIDX_ATTR_IFLAG] & ~(TERMIOS.INLCR | TERMIOS.IGNCR | TERMIOS.ICRNL | TERMIOS.IGNBRK)

            aAttr[LIDX_ATTR_CC][TERMIOS.VMIN] = 0
            aAttr[LIDX_ATTR_CC][TERMIOS.VTIME] = 0
            termios.tcsetattr(self._oFd, TERMIOS.TCSANOW, aAttr)
            fcntl.ioctl(self._oFd, TERMIOS.TIOCMBIS, struct.pack('I', TERMIOS.TIOCM_RTS))
            return

        def __del__(self):
            self.mClose()

        def mDisableRTS(self):
            fcntl.ioctl(self._oFd, TERMIOS.TIOCMBIC, struct.pack('I', TERMIOS.TIOCM_RTS))

        def mEnableRTS(self):
            fcntl.ioctl(self._oFd, TERMIOS.TIOCMBIS, struct.pack('I', TERMIOS.TIOCM_RTS))

        def mSetRTS(self, bState):
            if bState:
                self.mEnableRTS()
            else:
                self.mDisableRTS()

        def mClose(self):
            if self._oFd:
                os.close(self._oFd)
                self._oFd = None
            return

        def mShutdown(self):
            self.mClose()
            
        def mSetRxTimeOut(self, RxTimeOut):
            print('mSetRxTimeOut not supported')


    class cCommDeviceOL(cCommDeviceBase):

        def __init__(self, sDevice, aMode):
            try:
                self._oFd = os.open('/dev/' + sDevice, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            except:
                print('Failed to open COM port')
                self._oFd = None
                return

            fcntl.fcntl(self._oFd, FCNTL.F_SETFL, 0)
            self.iTimeout = 3
            cCommDeviceBase.__init__(self, sDevice, aMode)
            return

        def mRead(self, iLen):
            sData = ''
            if self._oFd and iLen > 0:
                while len(sData) < iLen:
                    ready, _, _ = select.select([self._oFd], [], [], self.iTimeout)
                    if not ready:
                        break
                    sBuf = os.read(self._oFd, iLen - len(sData))
                    sData = sData + sBuf
                    if self.iTimeout >= 0 and not sBuf:
                        break

            return sData

        def mWrite(self, sData):
            if self._oFd:
                iOrigLen = iLen = len(sData)
                sBuf = sData
                while iLen > 0:
                    iWr = os.write(self._oFd, sBuf)
                    sBuf = sBuf[iWr:]
                    iLen = iLen - iWr

            return iOrigLen

        def mFlush(self):
            termios.tcflush(self._oFd, TERMIOS.TCOFLUSH)


else:
    print('Using linux version in non-linux system')

def fMain():
    pass


if __name__ == '__main__':
    fMain()