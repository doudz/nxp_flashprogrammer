# uncompyle6 version 3.2.5
# Python bytecode 2.6 (62161)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: DeviceInfo.pyo
# Compiled at: 2013-01-22 12:16:04
import logging, struct, ZedSerialEnum, ZedSerialApi
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
JN51XX_ROM_ID_ADDR = 4
SPI_CFG_BUS_WIDTH_24_BIT = 32
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
COUGAR_MAC_INDEX_SECTOR_PAGE = 5
COUGAR_MAC_INDEX_SECTOR_WORD = 7
COUGAR_CUSTOMER_MAC_ADDRESS_LOCATION = 16782704
COUGAR_MAC_ADDRESS_LOCATION = 16782720
BOOTLOADER_VERSION_ADDRESS = 98
JN516x_BOOTLOADER_ENTRY = 102

def Device_JN5121(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5121 r%d' % DeviceInfo.iProcessorRevNo
    DeviceInfo.dMemorySize['RAM'] = 98304


def Device_JN513x(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN513x r%d' % DeviceInfo.iProcessorRevNo


def Device_JN5139(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5139 r%d' % DeviceInfo.iProcessorRevNo
    DeviceInfo.bFlashIsEncrypted = DeviceInfo.bFlashEncrypted(oZsa)
    DeviceInfo.lMacAddressLocationInFlash = 36
    DeviceInfo.lMacAddressLocationInImage = 36
    DeviceInfo.dMemorySize['RAM'] = 98304


def Device_JN5139J01(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5139-J01'
    DeviceInfo.lMacAddressLocationInFlash = 48
    DeviceInfo.lMacAddressLocationInImage = 48


def Device_JN5147(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5147 r%d' % DeviceInfo.iProcessorRevNo
    DeviceInfo.bFlashIsEncrypted = DeviceInfo.bFlashEncrypted(oZsa)
    DeviceInfo.lMacAddressLocationInFlash = 48
    DeviceInfo.lMacAddressLocationInImage = 48


def Device_JN5148(DeviceInfo, oZsa):
    DeviceInfo.bFlashIsEncrypted = DeviceInfo.bFlashEncrypted(oZsa)
    DeviceInfo.lMacAddressLocationInFlash = 48
    DeviceInfo.lMacAddressLocationInImage = 48
    DeviceInfo.dMemorySize['RAM'] = 131072


def Device_JN5148001(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5148-001'


def Device_JN5148J01(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5148-J01'
    DeviceInfo.iBootLoaderVersion = 1
    DeviceInfo.lMacAddressLocationInFlash = 16
    DeviceInfo.lMacAddressLocationInImage = 20


def Device_JN5148Z01(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5148-Z01'
    DeviceInfo.iBootLoaderVersion = 1
    DeviceInfo.lMacAddressLocationInFlash = 16
    DeviceInfo.lMacAddressLocationInImage = 20


def Device_JN5148ZID5(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5148-Z-ID5'
    DeviceInfo.iBootLoaderVersion = 1
    DeviceInfo.lMacAddressLocationInFlash = 16
    DeviceInfo.lMacAddressLocationInImage = 20


def Device_JN5142A(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5142A r%d' % DeviceInfo.iProcessorRevNo
    DeviceInfo.iBootLoaderVersion = 1
    DeviceInfo.lMacAddressLocationInFlash = 16
    DeviceInfo.lMacAddressLocationInImage = 20
    DeviceInfo.dMemorySize['RAM'] = 32768


def Device_JN5142B(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5142B'
    DeviceInfo.iBootLoaderVersion = 1
    DeviceInfo.lMacAddressLocationInFlash = 16
    DeviceInfo.lMacAddressLocationInImage = 20
    DeviceInfo.dMemorySize['RAM'] = 32768


def Device_JN5142C(DeviceInfo, oZsa):
    DeviceInfo.sDevicelabel = 'JN5142-J01'
    DeviceInfo.iBootLoaderVersion = 1
    DeviceInfo.lMacAddressLocationInFlash = 16
    DeviceInfo.lMacAddressLocationInImage = 20
    DeviceInfo.dMemorySize['RAM'] = 32768


def Device_JN516X(DeviceInfo, oZsa):
    eReadResult, DeviceInfo.iBootLoaderVersion = oZsa.ZedRAMRead(BOOTLOADER_VERSION_ADDRESS, 4)
    DeviceInfo.iBootLoaderVersion = ord(DeviceInfo.iBootLoaderVersion[0]) << 24 | ord(DeviceInfo.iBootLoaderVersion[1]) << 16 | ord(DeviceInfo.iBootLoaderVersion[2]) << 8 | ord(DeviceInfo.iBootLoaderVersion[3])
    DeviceInfo.lMacAddressLocationInFlash = 16
    DeviceInfo.lMacAddressLocationInImage = 20
    DeviceInfo.logger.debug('JN516x iBootLoaderVersion 0x%08X' % DeviceInfo.iBootLoaderVersion)
    DeviceInfo.sDevicelabel = 'JN516x, BL 0x%08X' % DeviceInfo.iBootLoaderVersion
    eReadResult, abDeviceConfig = oZsa.ZedRAMRead(FL_INDEX_SECTOR_DEVICE_CONFIG_ADDR, 22)
    DeviceInfo.FlashSize = ord(abDeviceConfig[3]) & 7
    DeviceInfo.RamSize = (ord(abDeviceConfig[3]) & 48) >> 4
    DeviceInfo.dMemorySize['RAM'] = (DeviceInfo.RamSize * 8 + 8) * 1024
    DeviceInfo.dMemorySize['FLASH'] = (DeviceInfo.FlashSize * 32 + 32) * 1024
    DeviceInfo.logger.debug('Device config flash %dk  ram %dk' % (DeviceInfo.FlashSize * 32 + 32, DeviceInfo.RamSize * 8 + 8))
    DeviceInfo.iBootloaderEntryPoint = JN516x_BOOTLOADER_ENTRY


dKnownDevices = {0: Device_JN5121, 
   1: Device_JN513x, 
   2: Device_JN5139, 
   (2, 1, 2): Device_JN5139J01, 
   (4, 0): Device_JN5147, 
   4: Device_JN5148, 
   (4, 1): Device_JN5148001, 
   (4, 1, 3): Device_JN5148J01, 
   (4, 1, 4): Device_JN5148Z01, 
   (4, 1, 5): Device_JN5148ZID5, 
   5: Device_JN5142A, 
   37: Device_JN5142B, 
   69: Device_JN5142C, 
   8: Device_JN516X}

def FlashDevice_Atmel_25F512(DeviceInfo):
    DeviceInfo.sFlashLabel = 'Atmel 25F512'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_ATMEL_AT25F512


def FlashDevice_Atmel_25F512A(DeviceInfo):
    DeviceInfo.sFlashLabel = 'Atmel 25F512A'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_ATMEL_AT25F512


def FlashDevice_ST_M25P10A(DeviceInfo):
    DeviceInfo.sFlashLabel = 'ST M25P10-A'
    if DeviceInfo.iProcessorPartNo == 0:
        DeviceInfo.sFlashLabel += ' (assumed)'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_ST_M25P10_A


def FlashDevice_ST_M25P20(DeviceInfo):
    DeviceInfo.sFlashLabel = 'ST M25P20'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_ST_M25P10_A


def FlashDevice_ST_M25P40(DeviceInfo):
    DeviceInfo.sFlashLabel = 'ST M25P40'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_ST_M25P40
    DeviceInfo.SECTOR_1 = 131072
    DeviceInfo.Sector_Len = 131072


def FlashDevice_ST_M25P05(DeviceInfo):
    DeviceInfo.sFlashLabel = 'ST M25P05'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_ST_M25P10_A


def FlashDevice_SST_25VF512(DeviceInfo):
    DeviceInfo.sFlashLabel = 'SST 25VF512A'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_SST_25VF010


def FlashDevice_SST_25VF010(DeviceInfo):
    DeviceInfo.sFlashLabel = 'SST 25VF010A'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_SST_25VF010


def FlashDevice_SST_25VF020(DeviceInfo):
    DeviceInfo.sFlashLabel = 'SST 25VF020'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_SST_25VF010
    DeviceInfo.SECTOR_1 = 65536
    DeviceInfo.Sector_Len = 65536


def FlashDevice_SST_25VF040B(DeviceInfo):
    DeviceInfo.sFlashLabel = 'SST 25VF040B'
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_SST_25VF010


def FlashDevice_INT_JN516x(DeviceInfo):
    DeviceInfo.sFlashLabel = 'Internal Flash (%dK)' % (DeviceInfo.FlashSize * 32 + 32)
    DeviceInfo.eFlashType = ZedSerialApi.E_FL_CHIP_INTERNAL


dFlashDevices = {(FlashIdManufacturerAtmel, FlashIdDeviceAtmel25F512): FlashDevice_Atmel_25F512, 
   (FlashIdManufacturerAtmel, FlashIdDeviceAtmel25F512A): FlashDevice_Atmel_25F512A, 
   (FlashIdManufacturerST, FlashIdDeviceSTM25P10A): FlashDevice_ST_M25P10A, 
   (FlashIdManufacturerST, FlashIdDeviceSTM25P20): FlashDevice_ST_M25P20, 
   (FlashIdManufacturerST, FlashIdDeviceSTM25P40): FlashDevice_ST_M25P40, 
   (FlashIdDeviceSTM25P40, FlashIdDeviceSTM25P40): FlashDevice_ST_M25P40, 
   (FlashIdDeviceSTM25P05, FlashIdDeviceSTM25P05): FlashDevice_ST_M25P05, 
   (FlashIdManufacturerSST, FlashIdDeviceSST25VF512): FlashDevice_SST_25VF512, 
   (FlashIdManufacturerSST, FlashIdDeviceSST25VF010): FlashDevice_SST_25VF010, 
   (FlashIdManufacturerSST, FlashIdDeviceSST25VF020): FlashDevice_SST_25VF020, 
   (FlashIdManufacturerSST, FlashIdDeviceSST25VF040B): FlashDevice_SST_25VF040B, 
   (FlashIdManufacturerInternal, FlashIdDeviceInternalJN516x): FlashDevice_INT_JN516x}

class cDeviceInfo:

    def __init__(self):
        self.logger = logging.getLogger('cDeviceInfo')
        self.Reset()

    def Reset(self):
        self.abMacAddress = struct.pack('<BBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0)
        self.abZBLicense = struct.pack('<BBBBBBBBBBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.abUserData = struct.pack('<BBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0)
        self.iProcessorPartNo = 0
        self.iProcessorRevNo = 0
        self.iMaskNo = 0
        self.iRomBuildVersion = 0
        self.FlashMID = 0
        self.FlashDID = 0
        self.eFlashType = ZedSerialApi.E_FL_CHIP_CUSTOM
        self.sDevicelabel = '...'
        self.sFlashLabel = '...'
        self.sErrorMsg = ''
        self.lMacAddressLocationInImage = 36
        self.lMacAddressLocationInFlash = 36
        self.lMacAddressLocationInIndex = (None, None)
        self.bFlashIsEncrypted = False
        self.SECTOR_1 = 0
        self.Sector_Len = 32768
        self.iBootLoaderVersion = 0
        self.bChipInfoKnown = False
        self.bInternalFlash = False
        self.FlashSize = 0
        self.RamSize = 0
        self.dMemorySize = {'RAM': 0, 'FLASH': 0}
        self.dMemoryBase = {'RAM': 4026531840}
        self.iBootloaderEntryPoint = 0
        return

    def __repr__(self):
        return ('\n').join([
         'Devicelabel:           %s' % self.sDevicelabel,
         'FlashLabel:            %s' % self.sFlashLabel,
         'Memory:                0x%08X bytes RAM, 0x%08X bytes Flash' % (self.dMemorySize['RAM'], self.dMemorySize['FLASH']),
         'ChipPartNo:            %d' % self.iProcessorPartNo,
         'ChipRevNo:             %d' % self.iProcessorRevNo,
         'ROM Version:           0x%08x' % self.iRomBuildVersion,
         'MAC Address:           %02X:%02X:%02X:%02X:%02X:%02X:%02X:%02X' % struct.unpack('<BBBBBBBB', self.abMacAddress),
         'ZB License:            0x%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X.%02X' % struct.unpack('<BBBBBBBBBBBBBBBB', self.abZBLicense),
         'User Data:             %02X:%02X:%02X:%02X:%02X:%02X:%02X:%02X' % struct.unpack('<BBBBBBBB', self.abUserData),
         'FlashMID:              0x%02X' % self.FlashMID,
         'FlashDID:              0x%02X' % self.FlashDID,
         'MacLocation:           0x%08X' % self.lMacAddressLocationInFlash,
         'Sector Length:         0x%05X' % self.Sector_Len,
         'Bootloader Version:    0x%08X' % self.iBootLoaderVersion,
         ''])

    def Print(self, boShowAll=0):
        print(str(self))

    def mRefreshDeviceInfo(self, oZsa, abEncryptKey, b16BitAccess=False):
        self.Reset()
        eResult = self.mRefreshChipVersion(oZsa)
        if not eResult == ZedSerialEnum.OK:
            return eResult
        eResult = self.mRefreshROMBuildVersion(oZsa)
        if not eResult == ZedSerialEnum.OK:
            return eResult
        eResult = self.mRefreshMacAddress(oZsa, abEncryptKey, b16BitAccess)
        if not eResult == ZedSerialEnum.OK:
            return eResult
        eResult = self.mRefreshFlashType(oZsa, abEncryptKey, b16BitAccess)
        if not eResult == ZedSerialEnum.OK:
            return eResult
        return ZedSerialEnum.OK

    def mRefreshChipVersion(self, oZsa):
        oZsa.mSetRTS(False)
        try:
            eReadResult = oZsa.ZedDetectProcessorVersion()
            self.iProcessorPartNo = oZsa.iProcessorPartNo
            self.iProcessorRevNo = oZsa.iProcessorRevNo
            self.iMaskNo = oZsa.iMaskNo
            if oZsa.iProcessorPartNo == 4 and (oZsa.iMaskNo <= 2 or oZsa.iMaskNo == 3):
                if oZsa.ZedDetectFushSecured() == ZedSerialEnum.FUSE_SECURED_NOT_LOGGEDIN:
                    return ZedSerialEnum.AUTH_ERROR
        except AssertionError:
            self.sErrorMsg = 'Could not read processor ID register\n Please check cabling and power'
            self.logger.debug(self.sErrorMsg)
            oZsa.mSetRTS(True)
            return ZedSerialEnum.NO_RESPONSE

        self.logger.debug('iProcessorPartNo no.=%d' % self.iProcessorPartNo)
        self.logger.debug('imask=%d' % self.iMaskNo)
        self.logger.debug('rev no.=%d' % self.iProcessorRevNo)
        self.sDevicelabel = 'Part no=%d, Rev no=%d, Mask no=%d' % (self.iProcessorPartNo, self.iProcessorRevNo, self.iMaskNo)
        try:
            dKnownDevices[self.iProcessorPartNo](self, oZsa)
        except KeyError:
            self.logger.debug('No information found for Processor part number %d' % self.iProcessorPartNo)

        try:
            dKnownDevices[(self.iProcessorPartNo, self.iProcessorRevNo)](self, oZsa)
        except KeyError:
            self.logger.debug('No information found for Processor part number %d, revision %d' % (self.iProcessorPartNo, self.iProcessorRevNo))

        try:
            dKnownDevices[(self.iProcessorPartNo, self.iProcessorRevNo, self.iMaskNo)](self, oZsa)
        except KeyError:
            self.logger.debug('No information found for Processor part number %d, revision %d, mask %d' % (self.iProcessorPartNo, self.iProcessorRevNo, self.iMaskNo))

        self.bChipInfoKnown = True
        return eReadResult

    def mRefreshROMBuildVersion(self, oZsa):
        eReadResult, abRead = oZsa.ZedRAMRead(JN51XX_ROM_ID_ADDR, 4)
        if eReadResult != ZedSerialEnum.OK:
            raise Exception('Could not read Processor ROM build ID')
        self.iRomBuildVersion = struct.unpack('>L', abRead)
        return eReadResult

    def mRefreshMacAddress(self, oZsa, abEncryptKey, b16BitAccess=False):
        self.bInternalFlash = False
        self.bGetMacAddrFromFlash = True
        if self.iProcessorPartNo == 8:
            abDeviceConfig = ''
            eReadResult, self.abMacAddress = oZsa.ZedRAMRead(COUGAR_CUSTOMER_MAC_ADDRESS_LOCATION, 8)
            self.bCustomerProgrammedMac = True
            if self.abMacAddress == struct.pack('BBBBBBBB', 255, 255, 255, 255, 255, 255, 255, 255):
                eReadResult, self.abMacAddress = oZsa.ZedRAMRead(COUGAR_MAC_ADDRESS_LOCATION, 8)
                self.bCustomerProgrammedMac = False
                self.logger.debug('Using factory MAC Address')
            else:
                self.logger.debug('Using customer MAC Address')
            self.bGetMacAddrFromFlash = False
            self.bInternalFlash = True
            self.lMacAddressLocationInIndex = (COUGAR_MAC_INDEX_SECTOR_PAGE, COUGAR_MAC_INDEX_SECTOR_WORD)
        else:
            if self.iProcessorPartNo > 4:
                eReadResult, abEfuse = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                abEfuseMacAddress = struct.pack('BBBBB', ord(abEfuse[7]), ord(abEfuse[3]), ord(abEfuse[2]), ord(abEfuse[1]), ord(abEfuse[0]))
                if abEfuseMacAddress == struct.pack('BBBBB', 0, 0, 0, 0, 0):
                    self.logger.debug('Efuse not used for MAC address - Get from Flash')
                    self.bGetMacAddrFromFlash = True
                else:
                    self.abMacAddress = struct.pack('BBB', 0, 21, 141) + abEfuseMacAddress
                    self.logger.debug('Got MAC address from Efuse')
                    self.bGetMacAddrFromFlash = False
            else:
                if self.iProcessorPartNo == 4:
                    if self.iProcessorRevNo == 0:
                        if self.bFlashEncrypted(oZsa) == False:
                            eReadResult, self.abMacAddress = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                            if self.abMacAddress == struct.pack('BBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0):
                                self.bGetMacAddrFromFlash = True
                            else:
                                self.bGetMacAddrFromFlash = False
                        else:
                            self.bGetMacAddrFromFlash = True
                    else:
                        eReadResult, self.abMacAddress = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                        if self.abMacAddress == struct.pack('BBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0):
                            self.bGetMacAddrFromFlash = True
                        else:
                            self.logger.debug('Efuse not used for MAC address - Get from Flash')
                            self.bGetMacAddrFromFlash = False
                else:
                    if self.iProcessorPartNo == 2 and self.iProcessorRevNo > 0 or bTestMacInEFuse:
                        eReadResult, self.abMacAddress = oZsa.ZedRAMRead(268435552, 8)
                        if self.abMacAddress == struct.pack('BBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0):
                            self.bGetMacAddrFromFlash = True
                        else:
                            self.bGetMacAddrFromFlash = False
                    else:
                        raise Exception('Unknown device type')
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
                self.logger.debug('PUMA Flash MAC Address: %02X:%02X:%02X:%02X:%02X:%02X:%02X:%02X' % (ord(macAndLicenseRam[0]), ord(macAndLicenseRam[1]), ord(macAndLicenseRam[2]), ord(macAndLicenseRam[3]), ord(macAndLicenseRam[4]), ord(macAndLicenseRam[5]), ord(macAndLicenseRam[6]), ord(macAndLicenseRam[7])))
                self.logger.debug('PUMA Efuse MAC Address: %02X:%02X:%02X:%02X:%02X:%02X:%02X:%02X' % (ord(macAndLicenseEfuse[0]), ord(macAndLicenseEfuse[1]), ord(macAndLicenseEfuse[2]), ord(macAndLicenseEfuse[3]), ord(macAndLicenseEfuse[4]), ord(macAndLicenseEfuse[5]), ord(macAndLicenseEfuse[6]), ord(macAndLicenseEfuse[7])))
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
                self.abUserData = macAndLicenseRam[24:32]
            elif self.bFlashIsEncrypted == False or self.iProcessorPartNo > 4 and self.iProcessorPartNo < 8 or self.iProcessorPartNo == 4 and self.iProcessorRevNo == 1 and self.iMaskNo == 3:
                eReadResult, macAndLicense = oZsa.ZedFlashRead(lMacAddress, 32)
                if self.bGetMacAddrFromFlash:
                    self.abMacAddress = macAndLicense[:8]
                self.abZBLicense = macAndLicense[8:24]
                self.abUserData = macAndLicense[24:32]
            elif self.iProcessorPartNo == 4:
                if self.iProcessorRevNo == 1:
                    if self.bGetMacAddrFromFlash:
                        self.logger.debug('Got encrypted MAC from flash')
                        eReadResult, encryptedMacAddress = oZsa.ZedFlashRead(lMacAddress, 32)
                    else:
                        self.logger.debug('Got encrypted MAC from efuse')
                        eReadResult, self.abMacAddress = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                else:
                    eReadResult, encryptedMacAddress = oZsa.ZedFlashRead(lMacAddress, 32)
                if eReadResult == ZedSerialEnum.OK and self.bGetMacAddrFromFlash:
                    macAndLicense = encryptFlashData([16, 286397204, 353769240, 0], abEncryptKey, encryptedMacAddress, 8)
                    self.abMacAddress = macAndLicense[:8]
                else:
                    macAndLicense = oZsa.ZedFlashRead(lMacAddress, 32)
                self.abZBLicense = macAndLicense[8:24]
                self.abUserData = macAndLicense[24:32]
        if eReadResult != ZedSerialEnum.OK:
            self.sErrorMsg = 'Failed to read device MAC address;\n Please check cabling and power'
            self.logger.debug(self.sErrorMsg)
            oZsa.mSetRTS(True)
        return eReadResult

    def mRefreshFlashType(self, oZsa, abEncryptKey, b16BitAccess=False):
        self.FlashMID = FlashIdManufacturerST
        self.FlashDID = FlashIdDeviceSTM25P10A
        if self.iProcessorPartNo >= 2:
            eReadResult, abFlashId = oZsa.ZedFlashReadId()
            if eReadResult != ZedSerialEnum.OK:
                self.sErrorMsg = 'Failed to read Flash chip id;\n Please check cabling and power'
                self.logger.debug(self.sErrorMsg)
                oZsa.mSetRTS(True)
                return eReadResult
            self.FlashMID, self.FlashDID = struct.unpack('<BB', abFlashId)
        try:
            dFlashDevices[(self.FlashMID, self.FlashDID)](self)
        except KeyError:
            self.logger.debug('Unknown flash device, Manufacturer 0x%X, Device 0x%0x' % (self.FlashMID, self.FlashDID))
            self.sFlashLabel = 'ManufacturerId: 0x%02X, DeviceId: 0x%02X' % (self.FlashMID, self.FlashDID)
            self.eFlashType = ZedSerialApi.E_FL_CHIP_CUSTOM
        else:
            if self.iProcessorPartNo >= 2:
                if self.eFlashType != ZedSerialApi.E_FL_CHIP_CUSTOM:
                    oZsa.ZedFlashSelectType(self.eFlashType)

        oZsa.mSetRTS(True)
        return ZedSerialEnum.OK

    def bFlashEncrypted(self, oZsa):
        if self.iProcessorPartNo > 4:
            eReadResult, key = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION + 16, 4)
            if eReadResult != ZedSerialEnum.OK:
                return True
        else:
            if self.iProcessorPartNo == 4 and self.iProcessorRevNo == 0:
                eReadResult, key = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 4)
            eReadResult, key = oZsa.ZedRAMRead(JAGUAR_EFUSE_LOCATION + 16, 4)
        if eReadResult != ZedSerialEnum.OK:
            return True
        else:
            eReadResult, key = oZsa.ZedRAMRead(268435580, 4)
            if eReadResult != ZedSerialEnum.OK:
                return True
        return False