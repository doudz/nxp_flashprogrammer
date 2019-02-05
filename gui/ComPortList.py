# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: ComPortList.pyo
# Compiled at: 2007-10-26 10:28:27
import sys, os


def fGetComPortList():
    if sys.platform == 'linux':
        aComPortList = os.popen("ls /dev | grep 'tty[S|U]'").read().split()
    else:
        import win32file, win32con
        aComPortList = []
        for i in range(0, 257):
            try:
                sComPort = 'COM%d' % i
                oFd = win32file.CreateFile('\\\\.\\' + sComPort, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0, None, win32con.OPEN_EXISTING, 0, 0)
                aComPortList.append(sComPort)
                win32file.CloseHandle(oFd)
            except:
                pass

    return aComPortList


def fMain():
    pass


if __name__ == '__main__':
    fMain()