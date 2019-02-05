# uncompyle6 version 3.2.5
# Python bytecode 2.6 (62161)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: ComPortList.pyo
# Compiled at: 2012-10-10 12:34:16
import sys

def enumerateSerialPorts(basename='\\Device\\VCP'):
    import winreg as winreg, itertools
    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
    except WindowsError:
        raise IterationError
    else:
        for i in itertools.count():
            try:
                val = winreg.EnumValue(key, i)
                if val[0].startswith(basename):
                    yield str(val[1])
            except EnvironmentError:
                break


def fGetComPortList():
    if sys.platform == 'linux':
        import string, os
        aComPortList = [ '/dev/' + dev for dev in os.popen("ls /dev | grep 'tty[S|U]'").read().split() ]
    else:
        aComPortList = list(enumerateSerialPorts('\\Device\\VCP'))
    return aComPortList


def fMain():
    print(fGetComPortList())


if __name__ == '__main__':
    fMain()