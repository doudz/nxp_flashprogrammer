# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: LicenceManager.pyo
# Compiled at: 2007-10-31 14:49:37
import wx, time, os, sys, binascii, tempfile
MAX_LOCK_RETRIES = 10

class CLicenceManager():

    def __init__(self, sLicenceFile):
        self.sLicenceFile = sLicenceFile
        self.sLockFile = sLicenceFile + '.lock'
        self.lockfd = None
        try:
            licFile = file(self.sLicenceFile, 'r')
        except:
            sWarning = 'licence file ' + sLicenceFile + ' not found'
            raise UserWarning(sWarning, None)

        licFile.close()
        return

    def __del__(self):
        self.unlock()

    def locked(self):
        if self.lockfd is None:
            return 0
        else:
            return 1
        return

    def lock(self):
        if self.locked():
            return 0
        for iRetries in range(MAX_LOCK_RETRIES):
            try:
                self.lockfd = os.open(self.sLockFile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                if sys.platform == 'win32':
                    sOwner = os.getenv('USERNAME') + '@' + os.getenv('COMPUTERNAME')
                else:
                    sOwner = os.getenv('USER') + '@' + os.getenv('SESSION_SRV')
                os.write(self.lockfd, '%s:%d' % (sOwner, os.getpid()))
                break
            except OSError:
                time.sleep(0.1 * iRetries)

        if iRetries < MAX_LOCK_RETRIES - 1:
            return 1
        else:
            self.lockfd = None
            self.sLockFile = None
            self.sLicenceFile = None
            return 0
        return

    def unlock(self):
        if not self.locked():
            return 0
        try:
            os.close(self.lockfd)
            os.remove(self.sLockFile)
            self.sLicenceFile = None
            self.sLockFile = None
            self.lockfd = None
            return 1
        except OSError:
            return 0

        return

    def ParseLicenceFile(self, sSearchMacAddress=''):
        abDataBlock = ''
        boEntryFound = False
        try:
            oFile = file(self.sLicenceFile, 'r')
        except:
            return (
             'File not found', [])
        else:
            LicenceLines = oFile.readlines()
            oFile.close()
            for line in LicenceLines[1:]:
                stripped_line = line.strip()
                if len(stripped_line) == 0:
                    pass
                elif stripped_line[0] == '#':
                    pass
                else:
                    split_line = stripped_line.split(',')
                    usedAlready = split_line[0].strip()
                    macAddr = split_line[1].strip()
                    if sSearchMacAddress != '':
                        if sSearchMacAddress == macAddr:
                            boEntryFound = True
                        else:
                            boEntryFound = False
                    else:
                        if usedAlready == '0':
                            boEntryFound = True
                    if boEntryFound:
                        abDataBlock = ''
                        for i in range(8):
                            abDataBlock = abDataBlock + binascii.a2b_hex(macAddr[2 + i * 2:4 + i * 2])

                        if len(split_line) > 2:
                            licenceKey = split_line[2].strip()
                            for i in range(16):
                                abDataBlock = abDataBlock + binascii.a2b_hex(licenceKey[2 + i * 2:4 + i * 2])

                        else:
                            abDataBlock = abDataBlock + ''
                        return (
                         'OK', abDataBlock)

            if sSearchMacAddress != '':
                return ('MAC address ' + sSearchMacAddress + ' was not found in the license file', [])
            return (
             'All addresses/licences in the file ' + self.sLicenceFile + ' have been used', [])

    def UpdateLicenceFile(self, parentFrame=None):
        try:
            oFile = file(self.sLicenceFile, 'r')
        except:
            sWarning = 'Could not open licence file for updating 1'
            raise UserWarning(sWarning, None)
        else:
            LicenceLines = oFile.readlines()
            bMarked = False
            LicenceLines[0] = LicenceLines[0].rstrip()
            for lineNo in range(1, len(LicenceLines)):
                LicenceLines[lineNo] = LicenceLines[lineNo].rstrip()
                line = LicenceLines[lineNo]
                stripped_line = line.strip()
                if bMarked == True:
                    pass
                elif len(stripped_line) == 0:
                    pass
                elif stripped_line[0] == '#':
                    pass
                else:
                    split_line = stripped_line.split(',')
                    usedAlready = split_line[0].strip()
                    if usedAlready == '0':
                        bMarked = True
                        stripped_line = '1'
                        for i in range(len(split_line) - 1):
                            stripped_line = stripped_line + ',' + split_line[i + 1]

                        LicenceLines[lineNo] = stripped_line

            oFile.close()
            try:
                oFile = file(self.sLicenceFile, 'w')
            except:
                sWarning = 'Could not open licence file for updating 2'
                raise UserWarning(sWarning, None)

            sUpdatedLicenceText = ''
            for line in LicenceLines:
                sUpdatedLicenceText += line + '\n'

        oFile.write(sUpdatedLicenceText)
        oFile.close()
        return

    def AddLicence(self, sMacAddress, sLicense):
        try:
            oFile = file(self.sLicenceFile, 'r')
        except:
            sWarning = 'Could not open licence file for updating 1'
            raise UserWarning(sWarning, None)
        else:
            LicenceLines = oFile.readlines()
            bMarked = False
            LicenceLines[0] = LicenceLines[0].rstrip()
            for lineNo in range(1, len(LicenceLines)):
                LicenceLines[lineNo] = LicenceLines[lineNo].rstrip()
                line = LicenceLines[lineNo]
                stripped_line = line.strip()
                if bMarked == True:
                    pass
                elif stripped_line[0] == '#':
                    pass
                else:
                    split_line = stripped_line.split(',')
                    usedAlready = split_line[0].strip()
                    macAddr = split_line[1].strip()
                    license = split_line[2].strip()
                    if sMacAddress == macAddr:
                        bMarked = license == sLicense and True

            oFile.close()
            if bMarked == False:
                LicenceLines.append('1, ' + sMacAddress + ', ' + sLicense)
            try:
                oFile = file(self.sLicenceFile, 'w')
            except:
                sWarning = 'Could not open licence file for updating 2'
                raise UserWarning(sWarning, None)

            sUpdatedLicenceText = ''
            for line in LicenceLines:
                sUpdatedLicenceText += line + '\n'

        oFile.write(sUpdatedLicenceText)
        oFile.close()
        return


if __name__ == '__main__':
    sTestFile = 'temp.txt'
    print('Running a series of tests on the Licence Manager')
    licMgr = CLicenceManager(sTestFile)
    boAccessFailed = 0
    try:
        licMgr2 = CLicenceManager(sTestFile)
    except AssertionError as e:
        boAccessFailed = 1
    else:
        del licMgr
        boAccessFailed = 0
        try:
            licMgr2 = CLicenceManager(sTestFile)
        except UserWarning as w:
            boAccessFailed = 1
        else:
            lic1 = licMgr2.ParseLicenceFile()
            licMgr2.UpdateLicenceFile()
            lic2 = licMgr2.ParseLicenceFile()
            del licMgr2
            print('OK')