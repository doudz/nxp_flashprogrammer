# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: FlashUtils.pyo
# Compiled at: 2012-12-07 20:18:00
from stat import *
import os, sys, struct, time, wx, ZedSerialEnum, ZedSerialApi, traceback, PrintData, FlashProgrammer
from EncryptUtils import *
SECTOR_0 = 0
SECTOR_1 = 32768
FlashIdManufacturerST = 16
FlashIdDeviceSTM25P10A = 16
FlashIdDeviceSTM25P20 = 17
FlashIdDeviceSTM25P40 = 18
FlashIdDeviceSTM25P05 = 5
FlashIdManufacturerAtmel = 31
FlashIdDeviceAtmel25F512 = 96
FlashIdDeviceAtmel25F512A = 101
FlashIdManufacturerSST = 191
FlashIdDeviceSST25VF512 = 72
FlashIdDeviceSST25VF010 = 73
FlashIdDeviceSST25VF020 = 67
FlashIdDeviceSST25VF040B = 141
FlashIdManufacturerInternal = 204
FlashIdDeviceInternalJN516x = 238
FL_INDEX_SECTOR_DEVICE_CONFIG_ADDR = 16782592
SPI_CFG_BUS_WIDTH_24_BIT = 1 << 5
FH_CFG_BYTES_IDX = 0
FH_TEXT_SEGM_ADDR_IDX = 4
FH_TEXT_SEGM_LEN_IDX = 8
FH_DATA_SEGM_ADDR_IDX = 12
FH_DATA_SEGM_LEN_IDX = 16
FH_BSS_SEGM_ADDR_IDX = 20
FH_BSS_SEGM_LEN_IDX = 24
FH_WAKEUP_ENTRY_POINT_IDX = 28
FH_RESET_ENTRY_POINT_IDX = 32
bTestMacInEFuse = 0
bHdkTest = False
if bHdkTest == False:
    JAGUAR_EFUSE_LOCATION = 33558624
else:
    JAGUAR_EFUSE_LOCATION = 128
COUGAR_CUSTOMER_MAC_ADDRESS_LOCATION = 16782704
COUGAR_MAC_ADDRESS_LOCATION = 16782720
BOOTLOADER_VERSION_ADDRESS = 98

class teHeaderProcessing():
    OVERWRITE = 0
    RETAIN_ALL = 1
    CHANGE_MAC = 2
    CHANGE_MAC_AND_LICENCE = 3


def ProgressIndication(progressDlg, progressCount, sInformativeText=None):
    if progressDlg is not None:
        if sInformativeText == None:
            if not progressDlg.Update(progressCount):
                if progressDlg is not None:
                    progressDlg.Destroy()
                return 0
        elif not progressDlg.Update(progressCount, sInformativeText):
            if progressDlg is not None:
                progressDlg.Destroy()
            return 0
    else:
        if sInformativeText == None:
            sys.stdout.write(str(progressCount) + '\r')
        else:
            print(sInformativeText)
    return 1


class cDeviceInfo():

    def __init__(self):
        self.Reset()

    def Reset(self):
        self.abMacAddress = ''
        self.iProcessorPartNo = 0
        self.iProcessorRevNo = 0
        self.FlashMID = 0
        self.FlashDID = 0
        self.eFlashType = ZedSerialApi.E_FL_CHIP_CUSTOM
        self.sDevicelabel = '...'
        self.sFlashLabel = '...'
        self.sErrorMsg = ''
        self.lMacAddressLocationInFlash = 36
        self.bFlashIsEncrypted = False
        self.abZBLicense = ''
        self.Sector_Len = 32768

    def Print(self, boShowAll=0):
        if boShowAll:
            print("sErrorMsg:   '%s'" % self.sErrorMsg)
        print('MAC Address: 0x%02X.%02X.%02X.%02X:%02X.%02X.%02X.%02X' % struct.unpack('<BBBBBBBB', self.abMacAddress))
        print('ZB License:  0x%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X' % struct.unpack('<BBBBBBBBBBBBBBBB', self.abZBLicense))
        print('ChipPartNo:  %d' % self.iProcessorPartNo)
        print('ChipRevNo:   %d' % self.iProcessorRevNo)
        print('FlashMID:    0x%02X' % self.FlashMID)
        print('FlashDID:    0x%02X' % self.FlashDID)
        print('Devicelabel: %s' % self.sDevicelabel)
        print('FlashLabel:  %s' % self.sFlashLabel)
        if boShowAll:
            print('MacLocation: 0x%08X' % self.lMacAddressLocationInFlash)
            print('Sector Length: 0x%05X' % self.Sector_Len)

    def mRefreshDeviceInfo(self, oZsa, abEncryptKey, FlashSelection, b16BitAccess=False):
        self.Reset()
        oZsa.oZsp.oHandle.mDisableRTS()
        try:
            eReadResult = oZsa.ZedDetectProcessorVersion()
            self.iProcessorPartNo = oZsa.iProcessorPartNo
            self.iProcessorRevNo = oZsa.iProcessorRevNo
            self.iMaskNo = oZsa.iMaskNo
            if eReadResult != ZedSerialEnum.OK:
                self.sErrorMsg = 'Could not read processor ID register\n Please check cabling and power'
                oZsa.oZsp.oHandle.mEnableRTS()
                return eReadResult
            else:
                if oZsa.iProcessorPartNo == 4 and (oZsa.iMaskNo <= 2 or oZsa.iMaskNo == 3):
                    if oZsa.ZedDetectFushSecured() == ZedSerialEnum.FUSE_SECURED_NOT_LOGGEDIN:
                        return ZedSerialEnum.AUTH_ERROR
        except AssertionError:
            self.sErrorMsg = 'Could not read processor ID register\n Please check cabling and power'
            oZsa.oZsp.oHandle.mEnableRTS()
            return ZedSerialEnum.NO_RESPONSE
        else:
            self.iProcessorPartNo = oZsa.iProcessorPartNo
            self.iProcessorRevNo = oZsa.iProcessorRevNo
            self.iMaskNo = oZsa.iMaskNo
            if self.iProcessorPartNo == 0:
                self.sDevicelabel = 'JN5121 r%d' % self.iProcessorRevNo
            else:
                if self.iProcessorPartNo == 1:
                    self.sDevicelabel = 'JN513x r%d' % self.iProcessorRevNo
                else:
                    if self.iProcessorPartNo == 2:
                        if self.iProcessorRevNo == 0:
                            self.sDevicelabel = 'JN5139 r%d' % self.iProcessorRevNo
                        else:
                            if self.iProcessorRevNo == 1:
                                if self.iMaskNo == 2:
                                    self.sDevicelabel = 'JN5139-J01'
                                else:
                                    self.sDevicelabel = 'JN5139'
                            else:
                                self.sDevicelabel = 'JN5139'
                        self.bFlashIsEncrypted = self.bFlashEncrypted(oZsa)
                    else:
                        if self.iProcessorPartNo == 4:
                            if self.iProcessorRevNo == 0:
                                self.sDevicelabel = 'JN5147 r%d' % self.iProcessorRevNo
                            else:
                                if self.iProcessorRevNo == 1:
                                    if self.iMaskNo == 0:
                                        self.sDevicelabel = 'JN5148 r0'
                                    elif self.iMaskNo == 3:
                                        self.sDevicelabel = 'JN5148-J01'
                                    elif self.iMaskNo == 4:
                                        self.sDevicelabel = 'JN5148-Z01'
                                        self.iMaskNo = 3
                                    elif self.iMaskNo == 5:
                                        self.sDevicelabel = 'JN5148-Z-ID5'
                                        self.iMaskNo = 3
                                    else:
                                        self.sDevicelabel = 'JN5148-001'
                                else:
                                    self.sDevicelabel = 'Part no=%d, Rev no=%d, Mask no=%d'(self.iProcessorPartNo, self.iProcessorRevNo, self.iMaskNo)
                            self.bFlashIsEncrypted = self.bFlashEncrypted(oZsa)
                        else:
                            if self.iProcessorPartNo == 5:
                                self.sDevicelabel = 'JN5142A r%d' % self.iProcessorRevNo
                            else:
                                if self.iProcessorPartNo == 37:
                                    self.sDevicelabel = 'JN5142B'
                                else:
                                    if self.iProcessorPartNo == 69:
                                        self.sDevicelabel = 'JN5142-J01'
                                    else:
                                        if self.iProcessorPartNo == 8:
                                            abDeviceConfig = ''
                                            eReadResult, self.abMacAddress = oZsa.ZedRAMRead(COUGAR_CUSTOMER_MAC_ADDRESS_LOCATION, 8)
                                            self.bCustomerProgrammedMac = True
                                            if self.abMacAddress == struct.pack('BBBBBBBB', 255, 255, 255, 255, 255, 255, 255, 255):
                                                eReadResult, self.abMacAddress = oZsa.ZedRAMRead(COUGAR_MAC_ADDRESS_LOCATION, 8)
                                                self.bCustomerProgrammedMac = False
                                            eReadResult, abDeviceConfig = oZsa.ZedRAMRead(FL_INDEX_SECTOR_DEVICE_CONFIG_ADDR, 22)
                                            self.FlashSize = ord(abDeviceConfig[3]) & 7
                                            self.RamSize = (ord(abDeviceConfig[3]) & 48) >> 4
                                            print('Flash-%d Ram-%d' % (self.FlashSize, self.RamSize))
                                            print('device config flash %dk  ram %dk' % (self.FlashSize * 32 + 32, self.RamSize * 8 + 8))
                                            eReadResult, BootLoaderVersion = oZsa.ZedRAMRead(BOOTLOADER_VERSION_ADDRESS, 4)
                                            print('BootLoaderVersion %s' % ord(BootLoaderVersion[3]))
                                            if self.FlashSize == 7:
                                                self.sDevicelabel = self.RamSize == 3 and 'JN5168,'
                                            else:
                                                if self.FlashSize == 4:
                                                    self.sDevicelabel = self.RamSize == 3 and 'JN5164,'
                                                else:
                                                    if self.FlashSize == 1:
                                                        self.sDevicelabel = self.RamSize == 0 and 'JN5161,'
                                                    else:
                                                        self.sDevicelabel = 'JN516x,'
                                            self.sDevicelabel += ' BL 0x%02X%02X%02X%02X' % (ord(BootLoaderVersion[0]), ord(BootLoaderVersion[1]), ord(BootLoaderVersion[2]), ord(BootLoaderVersion[3]))
                                        else:
                                            self.sDevicelabel = 'JN 51xx, Part 0x%X, Rev 0x%X' % (self.iProcessorPartNo, self.iProcessorRevNo)
            self.bInternalFlash = False
            self.bGetMacAddrFromFlash = True
            if self.iProcessorPartNo == 8:
                self.bGetMacAddrFromFlash = False
                self.bInternalFlash = True
            else:
                if self.iProcessorPartNo > 4:
                    self.lMacAddressLocationInFlash = 16
                    eReadResult, abEfuse = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                    abEfuseMacAddress = struct.pack('BBBBB', ord(abEfuse[7]), ord(abEfuse[3]), ord(abEfuse[2]), ord(abEfuse[1]), ord(abEfuse[0]))
                    if abEfuseMacAddress == struct.pack('LB', 0, 0):
                        print('Efuse not used for MAC address - Get from Flash')
                        self.bGetMacAddrFromFlash = True
                    else:
                        print('MAC in Efuse !! ', ord(abEfuseMacAddress[0]), ord(abEfuseMacAddress[1]), ord(abEfuseMacAddress[2]), ord(abEfuseMacAddress[3]), ord(abEfuseMacAddress[4]))
                        self.abMacAddress = struct.pack('BBB', 0, 21, 141) + abEfuseMacAddress
                        self.bGetMacAddrFromFlash = False
                else:
                    if self.iProcessorPartNo == 4 and self.iProcessorRevNo == 1:
                        if self.iMaskNo == 3:
                            self.lMacAddressLocationInFlash = 16
                        else:
                            self.lMacAddressLocationInFlash = self.lMacAddressLocationInFlash + 12
                        if self.iProcessorRevNo == 0:
                            if self.bFlashEncrypted(oZsa) == False:
                                eReadResult, self.abMacAddress = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                                if self.abMacAddress == struct.pack('LL', 0, 0):
                                    self.bGetMacAddrFromFlash = True
                                else:
                                    self.bGetMacAddrFromFlash = False
                            else:
                                self.bGetMacAddrFromFlash = True
                        else:
                            eReadResult, self.abMacAddress = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                            if self.abMacAddress == struct.pack('LL', 0, 0):
                                self.bGetMacAddrFromFlash = True
                            else:
                                self.bGetMacAddrFromFlash = False
                    else:
                        if self.iProcessorPartNo == 2 and self.iProcessorRevNo > 0 or bTestMacInEFuse:
                            self.lMacAddressLocationInFlash = self.lMacAddressLocationInFlash + 12
                            eReadResult, self.abMacAddress = oZsa.ZedRAMRead(268435552, 8)
                            if self.abMacAddress == struct.pack('LL', 0, 0):
                                self.bGetMacAddrFromFlash = True
                            else:
                                self.bGetMacAddrFromFlash = False
            if b16BitAccess:
                lMacAddress = self.lMacAddressLocationInFlash - 1 << 8
            else:
                lMacAddress = self.lMacAddressLocationInFlash
            if self.iProcessorPartNo != 8 and self.iProcessorPartNo > 4:
                if self.iProcessorPartNo < 8:
                    MacAddress = [
                     0, 0, 0, 0, 0, 0, 0, 0]
                    eReadResult, macAndLicenseRam = oZsa.ZedFlashRead(lMacAddress, 32)
                    eReadResult, macAndLicenseEfuse = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                    if ord(macAndLicenseRam[3]) != 255 or ord(macAndLicenseRam[4]) != 255 or ord(macAndLicenseRam[5]) != 255 or ord(macAndLicenseRam[6]) != 255 or ord(macAndLicenseRam[7]) != 255:
                        MacAddress[:8] = macAndLicenseRam[:8]
                    else:
                        if ord(macAndLicenseEfuse[3]) != 0 or ord(macAndLicenseEfuse[4]) != 0 or ord(macAndLicenseEfuse[5]) != 0 or ord(macAndLicenseEfuse[6]) != 0 or ord(macAndLicenseEfuse[7]) != 0:
                            MacAddress[3:8] = macAndLicenseEfuse[3:8]
                            if ord(macAndLicenseRam[0]) != 255 or ord(macAndLicenseRam[1]) != 255 or ord(macAndLicenseRam[2]) != 255:
                                MacAddress[:3] = macAndLicenseRam[:3]
                            else:
                                MacAddress[0] = chr(0)
                                MacAddress[1] = chr(21)
                                MacAddress[2] = chr(141)
                        else:
                            MacAddress[:8] = macAndLicenseRam[:8]
                    self.abMacAddress = struct.pack('<BBBBBBBB', ord(MacAddress[0]), ord(MacAddress[1]), ord(MacAddress[2]), ord(MacAddress[3]), ord(MacAddress[4]), ord(MacAddress[5]), ord(MacAddress[6]), ord(MacAddress[7]))
                    self.abZBLicense = macAndLicenseRam[8:24]
                elif self.bFlashIsEncrypted == False or self.iProcessorPartNo > 4 and self.iProcessorPartNo < 8 or self.iProcessorPartNo == 4 and self.iProcessorRevNo == 1 and self.iMaskNo == 3:
                    eReadResult, macAndLicense = oZsa.ZedFlashRead(lMacAddress, 32)
                    if self.bGetMacAddrFromFlash:
                        self.abMacAddress = macAndLicense[:8]
                    self.abZBLicense = macAndLicense[8:24]
                else:
                    if self.iProcessorPartNo == 4:
                        if self.iProcessorRevNo == 1:
                            if self.bGetMacAddrFromFlash:
                                eReadResult, encryptedMacAddress = oZsa.ZedFlashRead(lMacAddress, 32)
                            else:
                                eReadResult, self.abMacAddress = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                        else:
                            eReadResult, encryptedMacAddress = oZsa.ZedFlashRead(lMacAddress, 32)
                        if eReadResult == ZedSerialEnum.OK:
                            if self.bGetMacAddrFromFlash:
                                macAndLicense = encryptFlashData([16, 286397204, 353769240, 0], abEncryptKey, encryptedMacAddress, 8)
                                self.abMacAddress = macAndLicense[:8]
                            else:
                                macAndLicense = oZsa.ZedFlashRead(lMacAddress, 32)
                            self.abZBLicense = macAndLicense[8:24]
                    if eReadResult != ZedSerialEnum.OK:
                        self.sErrorMsg = 'Failed to read device MAC address;\n Please check cabling and power'
                        oZsa.oZsp.oHandle.mEnableRTS()
                        return eReadResult
                    self.FlashMID = FlashIdManufacturerST
                    self.FlashDID = FlashIdDeviceSTM25P10A
                    if FlashSelection == 0:
                        eResult = oZsa.ZedFlashSelectType(ZedSerialApi.E_FL_CHIP_INTERNAL)
                    else:
                        eResult = oZsa.ZedFlashSelectType(ZedSerialApi.E_FL_CHIP_ST_M25P10_A)
                    if self.iProcessorPartNo >= 2:
                        eReadResult, abFlashId = oZsa.ZedFlashReadId()
                        if eReadResult != ZedSerialEnum.OK:
                            self.sErrorMsg = 'Failed to read Flash chip id;\n Please check cabling and power'
                            oZsa.oZsp.oHandle.mEnableRTS()
                            return eReadResult
                        self.FlashMID, self.FlashDID = struct.unpack('<BB', abFlashId)
                    self.sFlashLabel = self.FlashMID == FlashIdManufacturerAtmel and self.FlashDID == FlashIdDeviceAtmel25F512 and 'Atmel 25F512'
                    self.eFlashType = ZedSerialApi.E_FL_CHIP_ATMEL_AT25F512
            else:
                if self.FlashMID == FlashIdManufacturerAtmel:
                    self.sFlashLabel = self.FlashDID == FlashIdDeviceAtmel25F512A and 'Atmel 25F512A'
                    self.eFlashType = ZedSerialApi.E_FL_CHIP_ATMEL_AT25F512
                else:
                    if self.FlashMID == FlashIdManufacturerST:
                        self.sFlashLabel = self.FlashDID == FlashIdDeviceSTM25P10A and 'ST M25P10-A'
                        if self.iProcessorPartNo == 0:
                            self.sFlashLabel += ' (assumed)'
                        self.eFlashType = ZedSerialApi.E_FL_CHIP_ST_M25P10_A
                    else:
                        if self.FlashMID == FlashIdManufacturerST:
                            self.sFlashLabel = self.FlashDID == FlashIdDeviceSTM25P20 and 'ST M25P20'
                            self.eFlashType = ZedSerialApi.E_FL_CHIP_ST_M25P10_A
                        else:
                            if self.FlashMID == FlashIdManufacturerST and self.FlashDID == FlashIdDeviceSTM25P40 or self.FlashMID == 18 and self.FlashDID == FlashIdDeviceSTM25P40:
                                self.sFlashLabel = 'ST M25P40'
                                self.eFlashType = ZedSerialApi.E_FL_CHIP_ST_M25P40
                                self.SECTOR_1 = 131072
                                self.Sector_Len = 131072
                            else:
                                if self.FlashMID == FlashIdDeviceSTM25P05:
                                    self.sFlashLabel = self.FlashDID == FlashIdDeviceSTM25P05 and 'ST M25P05'
                                    self.eFlashType = ZedSerialApi.E_FL_CHIP_ST_M25P10_A
                                else:
                                    if self.FlashMID == FlashIdManufacturerSST:
                                        self.sFlashLabel = self.FlashDID == FlashIdDeviceSST25VF512 and 'SST 25VF512A'
                                        self.eFlashType = ZedSerialApi.E_FL_CHIP_SST_25VF010
                                    else:
                                        if self.FlashMID == FlashIdManufacturerSST:
                                            self.sFlashLabel = self.FlashDID == FlashIdDeviceSST25VF010 and 'SST 25VF010A'
                                            self.eFlashType = ZedSerialApi.E_FL_CHIP_SST_25VF010
                                        else:
                                            if self.FlashMID == FlashIdManufacturerSST:
                                                self.sFlashLabel = self.FlashDID == FlashIdDeviceSST25VF020 and 'SST 25VF020'
                                                self.eFlashType = ZedSerialApi.E_FL_CHIP_SST_25VF010
                                                self.SECTOR_1 = 65536
                                                self.Sector_Len = 65536
                                            else:
                                                if self.FlashMID == FlashIdManufacturerSST:
                                                    self.sFlashLabel = self.FlashDID == FlashIdDeviceSST25VF040B and 'SST 25VF040B'
                                                    self.eFlashType = ZedSerialApi.E_FL_CHIP_SST_25VF010
                                                else:
                                                    if self.FlashMID == FlashIdManufacturerInternal:
                                                        self.sFlashLabel = self.FlashDID == FlashIdDeviceInternalJN516x and 'Internal Flash (%dK)' % (self.FlashSize * 32 + 32)
                                                        self.eFlashType = ZedSerialApi.E_FL_CHIP_INTERNAL
                                                    else:
                                                        self.sFlashLabel = 'ManufacturerId: 0x%02X, DeviceId: 0x%02X' % (self.FlashMID, self.FlashDID)
                                                        self.eFlashType = ZedSerialApi.E_FL_CHIP_CUSTOM
            if self.iProcessorPartNo >= 2:
                if self.eFlashType != ZedSerialApi.E_FL_CHIP_CUSTOM:
                    oZsa.ZedFlashSelectType(self.eFlashType)

        oZsa.oZsp.oHandle.mEnableRTS()
        return ZedSerialEnum.OK

    def bFlashEncrypted(self, oZsa):
        if self.iProcessorPartNo > 4:
            eReadResult, key = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION + 16, 4)
            if eReadResult != ZedSerialEnum.OK:
                return True
        else:
            if self.iProcessorPartNo == 4:
                if self.iProcessorRevNo == 0:
                    eReadResult, key = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 4)
                else:
                    eReadResult, key = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION + 16, 4)
                if eReadResult != ZedSerialEnum.OK:
                    return True
            else:
                eReadResult, key = oZsa.ZedRAMRead(268435580, 4)
                if eReadResult != ZedSerialEnum.OK:
                    return True
        return False


class cFlashUtilIF():

    def __init__(self, bRTSAsserted, DeviceInfo=None):
        self.bRTSAsserted = bRTSAsserted
        self.DeviceInfo = DeviceInfo
        if self.DeviceInfo is None:
            self.DeviceInfo = cDeviceInfo()
        return

    def SetRTSAsserted(self, bRTSAsserted):
        self.bRTSAsserted = bRTSAsserted

    def mRefreshDeviceInfo(self, oZsa, b16BitAccess=False):
        self.DeviceInfo.mRefreshDeviceInfo(oZsa, b16BitAccess)

    def DefineHeaderData(self, oZsa, eHeaderProc, abNewHeaderData):
        if eHeaderProc == teHeaderProcessing.OVERWRITE:
            abHeaderData = ''
        else:
            eReadResult, abHeaderData = oZsa.ZedFlashRead(self.DeviceInfo.lMacAddressLocationInFlash, 32)
            if eReadResult != ZedSerialEnum.OK:
                if eReadResult == ZedSerialEnum.AUTH_ERROR:
                    sWarning = 'Authentication error - please check the pass key'
                else:
                    sWarning = 'Failed to read from flash; check cabling and power'
                    raise UserWarning(sWarning, None)
        if eHeaderProc == teHeaderProcessing.OVERWRITE:
            pass
        else:
            if eHeaderProc == teHeaderProcessing.RETAIN_ALL:
                pass
            else:
                if eHeaderProc == teHeaderProcessing.CHANGE_MAC:
                    abHeaderData = abNewHeaderData + abHeaderData[8:]
                else:
                    if eHeaderProc == teHeaderProcessing.CHANGE_MAC_AND_LICENCE:
                        abHeaderData = abNewHeaderData + abHeaderData[24:]
                    else:
                        print('Invalid header data processing selection specified - retaining existing header')
        if eHeaderProc != teHeaderProcessing.OVERWRITE:
            if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                abHeaderData = abHeaderData[:8]
        return abHeaderData

    def ReadBlock(self, parentFrame, oZsa, iStartAddress, iLen, sProgressHeading='Reading block of data from flash', cbfProgInd=ProgressIndication):
        abBlockData = ''
        iAddress = 0
        progressDlg = None
        try:
            if oZsa is not None:
                if oZsa.mCheckOpened() == ZedSerialEnum.OK:
                    oZsa.oZsp.oHandle.mDisableRTS()
                    iResidue = 0
                    iChunk = 128
                    iFullReads = iLen / iChunk
                    print('Preserve Sector %d, Sector Length %d' % (FlashProgrammer.PRESERVE_SECTOR_NUM, FlashProgrammer.SECTOR_LEN))
                    if FlashProgrammer.SECTOR_LEN % iChunk:
                        iResidue = iLen - iFullReads * iChunk
                    max = iFullReads + 1
                    count = 0
                    if parentFrame is not None:
                        progressDlg = wx.ProgressDialog(sProgressHeading, 'Reading', maximum=max, parent=parentFrame, style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)
                    else:
                        progressDlg = None
                        if not cbfProgInd(progressDlg, count, sProgressHeading):
                            raise UserWarning(sProgressHeading + ' cancelled', None)
                    iAddress = iStartAddress
                    if iFullReads:
                        for i in range(iFullReads):
                            tFlashRead = oZsa.ZedFlashRead(iAddress, iChunk)
                            abBlockData += tFlashRead[1]
                            iAddress += iChunk
                            count += 1
                            if not cbfProgInd(progressDlg, count):
                                raise UserWarning('Flash programming cancelled', None)

                    if iResidue:
                        tFlashRead = oZsa.ZedFlashRead(iAddress, iResidue)
                        abBlockData += tFlashRead[1]
                        iAddress += iResidue
                        raise cbfProgInd(progressDlg, count) or UserWarning(sProgressHeading + ' cancelled', None)
            else:
                raise UserWarning('Serial port not open', None)
        except UserWarning as w:
            if w[0] is not None:
                if parentFrame is not None:
                    wx.MessageBox(w[0], 'Flash Programmer', wx.ICON_EXCLAMATION)
                else:
                    print(w[0])
        except:
            traceback.print_exc(file=sys.stdout)
        else:
            if oZsa is not None:
                oZsa.oZsp.oHandle.mSetRTS(self.bRTSAsserted)
            try:
                if progressDlg is not None:
                    progressDlg.Destroy()
            except:
                pass

        return (
         iAddress, abBlockData)

    def WriteBlock(self, parentFrame, oZsa, iStartAddress, abBlockData, sProgressHeading='Writing block of data to flash', cbfProgInd=ProgressIndication):
        progressDlg = None
        bRetVal = True
        try:
            if oZsa is not None:
                if oZsa.mCheckOpened() == ZedSerialEnum.OK:
                    oZsa.oZsp.oHandle.mDisableRTS()
                    iLen = len(abBlockData)
                    iResidue = 0
                    iChunk = 128
                    iFullWrites = iLen / iChunk
                    if iLen % iChunk:
                        iResidue = iLen - iFullWrites * iChunk
                    count = 0
                    max = iFullWrites + 1
                    if parentFrame is not None:
                        progressDlg = wx.ProgressDialog(sProgressHeading, 'Writing', maximum=max, parent=parentFrame, style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)
                    else:
                        progressDlg = None
                        if not cbfProgInd(progressDlg, count, sProgressHeading):
                            raise UserWarning(sProgressHeading + ' cancelled', None)
                    tFlashRead = oZsa.ZedFlashRead(iStartAddress, iChunk)
                    if tFlashRead[1][0:8] != '':
                        raise UserWarning('Cannot write to flash twice', None)
                    iIdx = 0
                    if iFullWrites > 0:
                        for i in range(iFullWrites):
                            abBytesRead = abBlockData[iIdx:iIdx + iChunk]
                            eStatus = oZsa.ZedFlashProg(iStartAddress + iIdx, abBytesRead)
                            count += 1
                            if eStatus != ZedSerialEnum.OK:
                                raise UserWarning(sProgressHeading + ' error (0x%02X) writing to flash device' % eStatus, None)
                            if not cbfProgInd(progressDlg, count):
                                raise UserWarning(sProgressHeading + ' cancelled', None)
                            iIdx += iChunk

                    if iResidue > 0:
                        abBytesRead = abBlockData[iIdx:iIdx + iResidue]
                        eStatus = oZsa.ZedFlashProg(iStartAddress + iIdx, abBytesRead)
                        if eStatus != ZedSerialEnum.OK:
                            raise UserWarning(sProgressHeading + ' error (%s) writing to flash device' % ZedSerialEnum.StatusStr(eStatus), None)
                    count += 1
                    raise cbfProgInd(progressDlg, count) or UserWarning(sProgressHeading + ' cancelled', None)
            else:
                raise UserWarning('Serial port not open', None)
        except UserWarning as w:
            if w[0] is not None:
                if parentFrame is not None:
                    wx.MessageBox(w[0], 'Flash Programmer', wx.ICON_EXCLAMATION)
                else:
                    print(w[0])
            bRetVal = False
        except:
            traceback.print_exc(file=sys.stdout)
            bRetVal = False
        else:
            if oZsa is not None:
                oZsa.oZsp.oHandle.mSetRTS(self.bRTSAsserted)
            try:
                if progressDlg is not None:
                    progressDlg.Destroy()
                if oFile is not None:
                    oFile.close()
            except:
                pass

        return bRetVal

    def bProgramFileIntoFlash(self, parentFrame, oZsa, eHeaderProc, abNewHeaderData, sFlashFile, sTitle='Writing program to flash', bPatchSPIBusCfgFor16BitAddrBus=False, cbfProgInd=ProgressIndication):
        progressDlg = None
        oFile = None
        bRetVal = True
        try:
            if oZsa is not None:
                abHeaderData = oZsa.mCheckOpened() == ZedSerialEnum.OK and self.DefineHeaderData(oZsa, eHeaderProc, abNewHeaderData)
                oZsa.oZsp.oHandle.mDisableRTS()
                try:
                    oFile = open(sFlashFile, 'rb')
                except:
                    raise UserWarning('Could not find file "' + sFlashFile + '" for programming', None)
                else:
                    iFileLength = os.stat(sFlashFile)[ST_SIZE]
                    if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                        iFileLength = iFileLength - 4
                        iBytesRead = oFile.read(4)
                    iResidue = 0
                    iChunk = 128
                    iFullReads = iFileLength / iChunk
                    if iFileLength % iChunk:
                        iResidue = iFileLength * iChunk
                    count = 0
                    max = iFullReads + 1
                    if parentFrame is not None:
                        progressDlg = wx.ProgressDialog(sTitle, 'Erasing flash', maximum=max, parent=parentFrame, style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)
                    else:
                        progressDlg = None
                        if not cbfProgInd(progressDlg, count, 'Erasing flash'):
                            raise UserWarning('Flash programming cancelled', None)
                    try:
                        oZsa.mSetRxTimeOut(10000)
                        bProgressOK = oZsa.ZedFlashBulkErase() == ZedSerialEnum.OK
                        oZsa.mSetRxTimeOut(ZedSerialApi.DEFAULT_READ_TIMEOUT)
                    except:
                        bProgressOK = 0
                    else:
                        if bProgressOK == 0:
                            sWarning = 'Failed to issue erase command; check cabling and power'
                            raise UserWarning(sWarning, None)
                        if not cbfProgInd(progressDlg, count, 'Verifying flash has been erased'):
                            raise UserWarning('Flash programming cancelled', None)
                        tFlashRead = oZsa.ZedFlashRead(0, iChunk)
                        if tFlashRead[1][0:8] != '':
                            raise UserWarning('%s: Failed to erase flash; check write protect pin' % sTitle, None)
                        if not cbfProgInd(progressDlg, count, 'Writing ' + str(iFullReads) + ' blocks of ' + str(iChunk) + ' bytes'):
                            raise UserWarning('Flash programming cancelled', None)
                        iAddress = 0
                        if iFullReads > 0:
                            for i in range(iFullReads):
                                abBytesRead = oFile.read(iChunk)
                                if i == 0:
                                    if eHeaderProc != teHeaderProcessing.OVERWRITE:
                                        abBytesRead = abBytesRead[0:self.DeviceInfo.lMacAddressLocationInFlash] + abHeaderData + abBytesRead[self.DeviceInfo.lMacAddressLocationInFlash + len(abHeaderData):]
                                    if bPatchSPIBusCfgFor16BitAddrBus:
                                        if self.DeviceInfo.iProcessorPartNo < 2 or self.DeviceInfo.iProcessorPartNo == 2 and self.DeviceInfo.iProcessorRevNo == 0:
                                            abCfg = struct.pack('<BBBB', 130, 130, 130, 130)
                                            abTextSegmDef = abBytesRead[FH_TEXT_SEGM_ADDR_IDX:FH_TEXT_SEGM_ADDR_IDX + 8]
                                            abTextSegmDef = struct.pack('B', 240) + abTextSegmDef[1:]
                                            abZero = struct.pack('<L', 0)
                                            abBytesRead = abCfg + abCfg + abZero + abTextSegmDef + abBytesRead[FH_BSS_SEGM_ADDR_IDX:]
                                        else:
                                            u8Scramble1, u8Scramble2, u8SpiCfg1, u8SpiCg2 = struct.unpack('4B', abBytesRead[FH_CFG_BYTES_IDX:FH_CFG_BYTES_IDX + 4])
                                            if u8SpiCfg1 != u8SpiCg2:
                                                raise UserWarning('The two SPI bus configuration bytes in the FW file header differ', None)
                                            if u8SpiCfg1 & SPI_CFG_BUS_WIDTH_24_BIT:
                                                u8SpiCfg1 = u8SpiCfg1 & ~SPI_CFG_BUS_WIDTH_24_BIT
                                                abBytesRead = struct.pack('<BBBB', u8Scramble1, u8Scramble2, u8SpiCfg1, u8SpiCfg1) + abBytesRead[FH_CFG_BYTES_IDX + 4:]
                                oZsa.ZedFlashProg(iAddress, abBytesRead)
                                count += 1
                                if not cbfProgInd(progressDlg, count, sTitle):
                                    raise UserWarning('Flash programming cancelled', None)
                                iAddress += iChunk

                        if iResidue > 0:
                            abBytesRead = oFile.read(iResidue)
                            oZsa.ZedFlashProg(iAddress, abBytesRead)
                        count += 1
                        if not cbfProgInd(progressDlg, count, sTitle):
                            raise UserWarning('Flash programming cancelled', None)
                        oFile.close()
                        oFile = None
            else:
                raise UserWarning('Serial port not open', None)
        except UserWarning as w:
            if w[0] is not None:
                if parentFrame is not None:
                    wx.MessageBox(w[0], 'Flash Programmer', wx.ICON_EXCLAMATION)
                else:
                    print(w[0])
            bRetVal = False
        except:
            bRetVal = False
        else:
            if oZsa is not None:
                oZsa.oZsp.oHandle.mSetRTS(self.bRTSAsserted)
            try:
                if progressDlg is not None:
                    progressDlg.Destroy()
                if oFile is not None:
                    oFile.close()
            except:
                pass

        return bRetVal

    def bProgramFileIntoRAM(self, parentFrame, oZsa, eHeaderProc, abNewHeaderData, sFile, sTitle='Copying program to RAM', cbfProgInd=ProgressIndication):
        progressDlg = None
        oFile = None
        bRetVal = True
        print("bProgramFileIntoRAM('%s')" % str(abNewHeaderData))
        try:
            if oZsa is not None:
                abHeaderData = oZsa.mCheckOpened() == ZedSerialEnum.OK and self.DefineHeaderData(oZsa, eHeaderProc, abNewHeaderData)
                oZsa.oZsp.oHandle.mDisableRTS()
                try:
                    oFile = open(sFile, 'rb')
                except:
                    raise UserWarning('Could not find file "' + sFile + '" for programming', None)
                else:
                    iFileLength = os.stat(sFile)[ST_SIZE]
                    iFileLength -= self.DeviceInfo.lMacAddressLocationInFlash
                    sFlashHeader = oFile.read(self.DeviceInfo.lMacAddressLocationInFlash)
                    iRAMStart, iRAMLen = struct.unpack('>LL', sFlashHeader[FH_TEXT_SEGM_ADDR_IDX:FH_TEXT_SEGM_ADDR_IDX + 8])
                    if iRAMLen == 0:
                        iRAMStart, iRAMLen = struct.unpack('>LL', sFlashHeader[FH_DATA_SEGM_ADDR_IDX:FH_DATA_SEGM_ADDR_IDX + 8])
                    iRAMResetEntry = struct.unpack('>L', sFlashHeader[FH_RESET_ENTRY_POINT_IDX:FH_RESET_ENTRY_POINT_IDX + 4])[0]
                    iResidue = 0
                    iChunk = 128
                    iFullReads = iFileLength / iChunk
                    if iFileLength % iChunk:
                        iResidue = iFileLength * iChunk
                    count = 0
                    max = iFullReads + 1
                    if parentFrame is not None:
                        progressDlg = wx.ProgressDialog(sTitle, '', maximum=max, parent=parentFrame, style=wx.PD_APP_MODAL | wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)
                    else:
                        progressDlg = None
                        if not cbfProgInd(progressDlg, count, ''):
                            raise UserWarning('RAM copying cancelled', None)
                    iAddress = iRAMStart
                    if iFullReads > 0:
                        for i in range(iFullReads):
                            abBytesRead = oFile.read(iChunk)
                            if i == 0 and eHeaderProc != teHeaderProcessing.OVERWRITE:
                                abBytesRead = abBytesRead[0:self.DeviceInfo.lMacAddressLocationInFlash] + abHeaderData + abBytesRead[self.DeviceInfo.lMacAddressLocationInFlash + len(abHeaderData):]
                            oZsa.ZedRAMwrite(iAddress, abBytesRead)
                            count += 1
                            if not cbfProgInd(progressDlg, count):
                                raise UserWarning('RAM copying cancelled', None)
                            iAddress += iChunk

                    if iResidue > 0:
                        abBytesRead = oFile.read(iResidue)
                        oZsa.ZedRAMwrite(iAddress, abBytesRead)
                    count += 1
                    if not cbfProgInd(progressDlg, count):
                        raise UserWarning('RAM programming cancelled', None)
                    oFile.close()
                    oFile = None
            else:
                raise UserWarning('Serial port not open', None)
        except UserWarning as w:
            if w[0] is not None:
                if parentFrame is not None:
                    wx.MessageBox(w[0], 'RAM Programmer', wx.ICON_EXCLAMATION)
                else:
                    print(w[0])
            bRetVal = False
        except:
            traceback.print_exc(file=sys.stdout)
            bRetVal = False
        else:
            if oZsa is not None:
                oZsa.oZsp.oHandle.mSetRTS(self.bRTSAsserted)
            try:
                if progressDlg is not None:
                    progressDlg.Destroy()
                if oFile is not None:
                    oFile.close()
            except:
                pass

            if bRetVal:
                return iRAMResetEntry
            return 0

        return

    def bProgramNewHeaderFileIntoRAM(self, parentFrame, oZsa, eHeaderProc, abNewHeaderData, sFile, sTitle='Copying program to RAM', cbfProgInd=ProgressIndication):
        progressDlg = None
        oFile = None
        bRetVal = True
        print("bProgramNewHeaderFileIntoRAM('%s')" % str(abNewHeaderData))
        try:
            if oZsa is not None:
                abHeaderData = oZsa.mCheckOpened() == ZedSerialEnum.OK and self.DefineHeaderData(oZsa, eHeaderProc, abNewHeaderData)
                oZsa.oZsp.oHandle.mDisableRTS()
                try:
                    oFile = open(sFile, 'rb')
                except:
                    raise UserWarning('Could not find file "' + sFile + '" for programming', None)
                else:
                    iFileLength = os.stat(sFile)[ST_SIZE]
                    iFileLength -= 60
                    sFlashHeader = oFile.read(60)
                    iRAMStart, iRAMLen = struct.unpack('>HH', sFlashHeader[44:48])
                    iRAMStart = iRAMStart * 4 + 67108864
                    iRAMLen = iRAMLen * 4
                    if iRAMLen == 0:
                        return 0
                    iRAMResetEntry = struct.unpack('>L', sFlashHeader[56:60])[0]
                    iResidue = 0
                    iChunk = 128
                    iFullReads = iFileLength / iChunk
                    if iFileLength % iChunk:
                        iResidue = iFileLength * iChunk
                    count = 0
                    max = iFullReads + 1
                    if parentFrame is not None:
                        progressDlg = wx.ProgressDialog(sTitle, '', maximum=max, parent=parentFrame, style=wx.PD_APP_MODAL | wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)
                    else:
                        progressDlg = None
                        if not cbfProgInd(progressDlg, count, ''):
                            raise UserWarning('RAM copying cancelled', None)
                    iAddress = iRAMStart
                    if iFullReads > 0:
                        for i in range(iFullReads):
                            abBytesRead = oFile.read(iChunk)
                            if i == 0 and eHeaderProc != teHeaderProcessing.OVERWRITE:
                                abBytesRead = abBytesRead[0:self.DeviceInfo.lMacAddressLocationInFlash] + abHeaderData + abBytesRead[self.DeviceInfo.lMacAddressLocationInFlash + len(abHeaderData):]
                            oZsa.ZedRAMwrite(iAddress, abBytesRead)
                            count += 1
                            if not cbfProgInd(progressDlg, count):
                                raise UserWarning('RAM copying cancelled', None)
                            iAddress += iChunk

                    if iResidue > 0:
                        abBytesRead = oFile.read(iResidue)
                        oZsa.ZedRAMwrite(iAddress, abBytesRead)
                    count += 1
                    if not cbfProgInd(progressDlg, count):
                        raise UserWarning('RAM programming cancelled', None)
                    oFile.close()
                    oFile = None
            else:
                raise UserWarning('Serial port not open', None)
        except UserWarning as w:
            if w[0] is not None:
                if parentFrame is not None:
                    wx.MessageBox(w[0], 'RAM Programmer', wx.ICON_EXCLAMATION)
                else:
                    print(w[0])
            bRetVal = False
        except:
            traceback.print_exc(file=sys.stdout)
            bRetVal = False
        else:
            if oZsa is not None:
                oZsa.oZsp.oHandle.mSetRTS(self.bRTSAsserted)
            try:
                if progressDlg is not None:
                    progressDlg.Destroy()
                if oFile is not None:
                    oFile.close()
            except:
                pass

            if bRetVal:
                return iRAMResetEntry
            return 0

        return

    def bVerifyFlashFile(self, parentFrame, oZsa, eHeaderProc, abNewHeaderData, sFlashFile, bPatchSPIBusCfgFor16BitAddrBus=False, cbfProgInd=ProgressIndication):
        progressDlg = None
        oFile = None
        bRetVal = True
        try:
            if oZsa is not None:
                if oZsa.mCheckOpened() == ZedSerialEnum.OK:
                    oZsa.oZsp.oHandle.mDisableRTS()
                    iFileLength = os.stat(sFlashFile)[ST_SIZE]
                    if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                        iFileLength = iFileLength - 4
                    iResidue = 0
                    iChunk = 128
                    iFullReads = iFileLength / iChunk
                    if iFileLength % iChunk:
                        iResidue = iFileLength - iFullReads * iChunk
                    count = 0
                    max = iFullReads + 1
                    progressDlg = parentFrame is not None and wx.ProgressDialog('Verifying program in flash', '', maximum=max, parent=parentFrame, style=wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)
                else:
                    progressDlg = None
                if not cbfProgInd(progressDlg, count, 'Verifying ' + str(iFullReads) + ' blocks of ' + str(iChunk) + ' bytes'):
                    raise UserWarning('Flash verification cancelled', None)
                abHeaderData = self.DefineHeaderData(oZsa, eHeaderProc, abNewHeaderData)
                oFile = open(sFlashFile, 'rb')
                if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                    iBytesRead = oFile.read(4)
                iAddress = 0
                iErrors = 0
                if iFullReads > 0:
                    for i in range(iFullReads):
                        abBytesRead = oFile.read(iChunk)
                        if i == 0:
                            if eHeaderProc != teHeaderProcessing.OVERWRITE:
                                abBytesRead = abBytesRead[0:self.DeviceInfo.lMacAddressLocationInFlash] + abHeaderData + abBytesRead[self.DeviceInfo.lMacAddressLocationInFlash + len(abHeaderData):]
                            if bPatchSPIBusCfgFor16BitAddrBus:
                                if self.DeviceInfo.iProcessorPartNo < 2 or self.DeviceInfo.iProcessorPartNo == 2 and self.DeviceInfo.iProcessorRevNo == 0:
                                    abCfg = struct.pack('<BBBB', 130, 130, 130, 130)
                                    abTextSegmDef = abBytesRead[FH_TEXT_SEGM_ADDR_IDX:FH_TEXT_SEGM_ADDR_IDX + 8]
                                    abTextSegmDef = struct.pack('B', 240) + abTextSegmDef[1:]
                                    abZero = struct.pack('<L', 0)
                                    abBytesRead = abCfg + abCfg + abZero + abTextSegmDef + abBytesRead[FH_BSS_SEGM_ADDR_IDX:]
                                else:
                                    u8SpiCfg1, u8SpiCg2, u8Scramble1, u8Scramble2 = struct.unpack('4B', abBytesRead[FH_CFG_BYTES_IDX:FH_CFG_BYTES_IDX + 4])
                                    if u8SpiCfg1 != u8SpiCg2:
                                        UserWarning('The two SPI bus configuration bytes in the FW file header differ', None)
                                    if u8SpiCfg1 & SPI_CFG_BUS_WIDTH_24_BIT:
                                        u8SpiCfg1 = u8SpiCfg1 & ~SPI_CFG_BUS_WIDTH_24_BIT
                                        abBytesRead = struct.pack('<BBBB', u8Scramble1, u8Scramble2, u8SpiCfg1, u8SpiCfg1) + abBytesRead[FH_CFG_BYTES_IDX + 4:]
                        tFlashRead = oZsa.ZedFlashRead(iAddress, iChunk)
                        if abBytesRead != tFlashRead[1]:
                            iErrors += 1
                        iAddress += iChunk
                        count += 1
                        if not cbfProgInd(progressDlg, count):
                            raise UserWarning('Flash verification cancelled', None)

                if iResidue > 0:
                    abBytesRead = oFile.read(iResidue)
                    tFlashRead = oZsa.ZedFlashRead(iAddress, iResidue)
                    if abBytesRead != tFlashRead[1]:
                        iErrors += 1
                count += 1
                if not cbfProgInd(progressDlg, count):
                    raise UserWarning('Flash verification cancelled', None)
                if iErrors > 0:
                    sWarning = 'Errors in data verification ' + str(iErrors)
                    raise UserWarning(sWarning, None)
                oFile.close()
                oFile = None
            else:
                raise UserWarning('Serial port not open', None)
        except UserWarning as w:
            if w[0] is not None:
                if parentFrame is not None:
                    wx.MessageBox(w[0], 'Flash Programmer', wx.ICON_EXCLAMATION)
                else:
                    print(w[0])
            bRetVal = False
        except:
            traceback.print_exc(file=sys.stdout)
            bRetVal = False
        else:
            if oZsa is not None:
                oZsa.oZsp.oHandle.mSetRTS(self.bRTSAsserted)
            try:
                if progressDlg is not None:
                    progressDlg.Destroy()
                if oFile is not None:
                    oFile.close()
            except:
                pass

        return bRetVal


if __name__ == '__main__':
    import ComPortList, ZedSerialApi

    def TstProgressIndication(progressDlg, progressCount, sInformativeText=None):
        print('TstProgressIndication %d, %s' % (progressCount, sInformativeText))
        return 1


    sComPort = ComPortList.fGetComPortList()[0]
    print('Connecting to device on %s' % sComPort)
    oZsa = ZedSerialApi.cZedSerialApi(38400, sComPort)
    eHeaderDataProcessing = teHeaderProcessing.RETAIN_ALL
    abNewHeaderData = None
    sFlashFile = 'echo.bin'
    oZsa.oZsp.oHandle.mSetRTS(True)
    oZsa.oZsp.mSetDebug(0)
    print('Cycle power on the device (to enable connection to flash loader)\n\nPress <ENTER> when done')
    sys.stdin.readline()
    print('Verifying connection to flash')
    oZsa.oZsp.oHandle.mDisableRTS()
    FlashUtilIF = cFlashUtilIF()
    bSuccess = FlashUtilIF.bProgramFileIntoFlash(None, oZsa, eHeaderDataProcessing, abNewHeaderData, sFlashFile, 0, TstProgressIndication)
    if bSuccess:
        bSuccess = FlashUtilIF.bVerifyFlashFile(None, oZsa, eHeaderDataProcessing, abNewHeaderData, sFlashFile, 0, TstProgressIndication)