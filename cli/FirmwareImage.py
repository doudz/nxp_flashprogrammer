# uncompyle6 version 3.2.5
# Python bytecode 2.6 (62161)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: FirmwareImage.pyo
# Compiled at: 2013-01-25 12:12:30
import struct, logging, os
from stat import *
import mmap, DeviceInfo
SIZE_MAC = 8
SIZE_LICENSE = 16
SIZE_USER_DATA = 8
SIZE_MAC_AND_LICENSE_HEADER = 24

class FirmwareError(Exception):

    def __init__(self, message):
        self.message = message


class cFirmwareImage:

    def __init__(self, oDeviceInfo=None, sFilename=None, sImage=None):
        self.logger = logging.getLogger('cFirmwareImage')
        self.oDeviceInfo = oDeviceInfo
        self.sFilename = sFilename
        self.oFileHandle = None
        self.sImage = ''
        self.iSize = 0
        if sFilename:
            self._mOpenFile()
        if sImage:
            self._mOpenImage(sImage)
        return

    def __repr__(self):
        return str(list(self.sImage))

    def _mOpenFile(self, sFilename=None):
        if sFilename:
            self.sFilename = sFilename
        if self.sFilename == None:
            raise FirmwareError('No file to open')
        if self.oFileHandle:
            self.logger.debug('Closing file')
            self.oFileHandle.close()
            self.oFileHandle = None
            if isinstance(self.sImage, mmap.mmap):
                self.sImage.close()
        self.logger = logging.getLogger('cFirmwareFile (%s)' % self.sFilename)
        try:
            self.oFileHandle = open(self.sFilename, 'rb')
        except Exception as e:
            raise FirmwareError('Could not find file "%s" (%s)' % (self.sFilename, str(e)))

        self.iSize = os.stat(self.sFilename)[ST_SIZE]
        self.logger.debug('Firmware filesize: %d bytes' % self.iSize)
        self.sImage = mmap.mmap(self.oFileHandle.fileno(), 0, access=mmap.ACCESS_COPY)
        return

    def _mOpenImage(self, sImage):
        self.iSize = len(sImage)
        self.sImage = sImage

    def mSetDeviceInfo(self, oDeviceInfo):
        self.logger.debug('Update device info with new device:\n%s' % str(oDeviceInfo))
        self.oDeviceInfo = oDeviceInfo

    def bIsCompatibile(self, oDeviceInfo=None, sFilename=None, sImage=None):
        if oDeviceInfo:
            self.oDeviceInfo = oDeviceInfo
        if sFilename:
            self._mOpenFile(sFilename)
        if sImage:
            self._mOpenImage(sImage)
        if self.oDeviceInfo.iBootLoaderVersion > 0:
            u32FwBuildVersion = struct.unpack('>L', self.sImage[:4])
        else:
            u32FwBuildVersion = struct.unpack('>L', self.sImage[12:16])
        self.logger.debug('Firmware file is built for device: 0x%08X' % u32FwBuildVersion)
        if self.oDeviceInfo.iProcessorPartNo == 8:
            FwFlashSize = (u32FwBuildVersion[0] & 4278190080) >> 24
            FwRamSize = (u32FwBuildVersion[0] & 16711680) >> 16
            FwProcessorPartNo = u32FwBuildVersion[0] & 255
            if self.oDeviceInfo.FlashSize == FwFlashSize and self.oDeviceInfo.RamSize == FwRamSize and FwProcessorPartNo == self.oDeviceInfo.iProcessorPartNo:
                u32ChipRomBuildVersion = u32FwBuildVersion
            else:
                u32ChipRomBuildVersion = 4294967295
        else:
            u32ChipRomBuildVersion = self.oDeviceInfo.iRomBuildVersion
        self.logger.debug('Device version: 0x%08X' % u32ChipRomBuildVersion)
        if u32FwBuildVersion != u32ChipRomBuildVersion:
            self.logger.warning('Firmware file appears to be built for a different processor version!')
            return False
        self.logger.debug('Firmware file is valid for device')
        return True

    def VerifyMACHeaderAllocated(self, oDeviceInfo=None, sFilename=None):
        if oDeviceInfo:
            self.oDeviceInfo = oDeviceInfo
        self._mOpenFile(sFilename)
        bWarn = 0
        abMACHeader = self.sImage[self.oDeviceInfo.lMacAddressLocationInImage:self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC_AND_LICENSE_HEADER]
        self.logger.debug('Read MAC Header from file: %s' % str(list(abMACHeader)))
        if self.oDeviceInfo.iBootLoaderVersion > 0:
            u8MacHeaderSize = 8
        else:
            u8MacHeaderSize = SIZE_MAC_AND_LICENSE_HEADER
        sFmt = '<' + str(SIZE_MAC_AND_LICENSE_HEADER) + 'B'
        lstMacHeader = struct.unpack(sFmt, abMACHeader)
        for i in range(u8MacHeaderSize):
            if lstMacHeader[i] != 255:
                bWarn = 1

        if bWarn:
            self.logger.warning('Data found in MAC address / license location')
            return False
        self.logger.debug('File has valid space reserved for MAC addres / license')
        return True

    def UpdateMACAddress(self, sMACAddress):
        if len(sMACAddress) != SIZE_MAC:
            self.logger.warning('MAC Address is the wrong size')
            raise FirmwareError('MAC Address is the wrong size')
        self.logger.debug('Update MAC Address to %s' % str(list(sMACAddress)))
        self.sImage[(self.oDeviceInfo.lMacAddressLocationInImage):(self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC)] = sMACAddress

    def GetMACAddress(self):
        return self.sImage[self.oDeviceInfo.lMacAddressLocationInImage:self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC]

    def UpdateZBLicense(self, sLicense):
        if len(sLicense) != SIZE_LICENSE:
            self.logger.warning('Zigbee license is the wrong size')
            raise FirmwareError('Zigbee license is the wrong size')
        if self.oDeviceInfo.iBootLoaderVersion > 0:
            self.logger.debug('Bootloader version %d does not have this field' % self.oDeviceInfo.iBootLoaderVersion)
            return
        self.logger.debug('Update Zigbee license to %s' % str(list(sLicense)))
        self.sImage[(self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC):(self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC + SIZE_LICENSE)] = sLicense

    def GetZBLicense(self):
        return self.sImage[self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC:self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC + SIZE_LICENSE]

    def UpdateUserData(self, sUserData):
        if len(sUserData) != SIZE_USER_DATA:
            self.logger.warning('User data is the wrong size')
            raise FirmwareError('User data is the wrong size')
        if self.oDeviceInfo.iBootLoaderVersion > 0:
            self.logger.debug('Bootloader version %d does not have this field' % self.oDeviceInfo.iBootLoaderVersion)
            return
        self.logger.debug('Update User data to %s' % str(list(sUserData)))
        self.sImage[(self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC + SIZE_LICENSE):(self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC + SIZE_LICENSE + SIZE_USER_DATA)] = sUserData

    def GetUserData(self):
        return self.sImage[self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC + SIZE_LICENSE:self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC + SIZE_LICENSE + SIZE_USER_DATA]

    def UpdateHeaderData(self, sHeaderData):
        if len(sHeaderData) != SIZE_MAC_AND_LICENSE_HEADER:
            self.logger.warning('Header data is the wrong size (%d not %d)' % (len(sHeaderData), SIZE_MAC_AND_LICENSE_HEADER))
            raise FirmwareError('Header data is the wrong size')
        self.logger.debug('Update Header data to %s' % str(list(sHeaderData)))
        self.sImage[(self.oDeviceInfo.lMacAddressLocationInImage):(self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC_AND_LICENSE_HEADER)] = sHeaderData

    def GetHeaderData(self):
        return self.sImage[self.oDeviceInfo.lMacAddressLocationInImage:self.oDeviceInfo.lMacAddressLocationInImage + SIZE_MAC_AND_LICENSE_HEADER]

    def PatchSPIBusCfgFor16BitAddrBus(self):
        if self.oDeviceInfo.iProcessorPartNo < 2 or self.oDeviceInfo.iProcessorPartNo == 2 and self.oDeviceInfo.iProcessorRevNo == 0:
            abCfg = struct.pack('<BBBB', 130, 130, 130, 130)
            abTextSegmDef = self.sImage[DeviceInfo.FH_TEXT_SEGM_ADDR_IDX:DeviceInfo.FH_TEXT_SEGM_ADDR_IDX + 8]
            abTextSegmDef = struct.pack('B', 240) + abTextSegmDef[1:]
            abZero = struct.pack('<L', 0)
            self.sImage[:(DeviceInfo.FH_TEXT_SEGM_ADDR_IDX + 8)] = abCfg + abCfg + abZero + abTextSegmDef
        else:
            u8Scramble1, u8Scramble2, u8SpiCfg1, u8SpiCg2 = struct.unpack('4B', self.sImage[DeviceInfo.FH_CFG_BYTES_IDX:DeviceInfo.FH_CFG_BYTES_IDX + 4])
            if u8SpiCfg1 != u8SpiCg2:
                raise FlashUtilsError('The two SPI bus configuration bytes in the FW file header differ')
            if u8SpiCfg1 & DeviceInfo.SPI_CFG_BUS_WIDTH_24_BIT:
                u8SpiCfg1 = u8SpiCfg1 & ~DeviceInfo.SPI_CFG_BUS_WIDTH_24_BIT
                self.sImage[:(DeviceInfo.FH_CFG_BYTES_IDX + 4)] = struct.pack('<BBBB', u8Scramble1, u8Scramble2, u8SpiCfg1, u8SpiCfg1)

    def ReadChunk(self, iChunkNumber, iChunkSize=128):
        self.logger.debug('Read Chunk %d (size %d) from image' % (iChunkNumber, iChunkSize))
        iStartAddress = iChunkNumber * iChunkSize
        if self.oDeviceInfo.iBootLoaderVersion > 0:
            iStartAddress += 4
        sChunkRemainder = ''
        iEndAddress = iStartAddress + iChunkSize
        if iEndAddress > self.iSize:
            sChunkRemainder = '' * (iEndAddress - self.iSize)
        self.logger.debug('Returning bytes %d to %d (of %d)' % (iStartAddress, iEndAddress, self.iSize))
        return self.sImage[iStartAddress:iEndAddress] + sChunkRemainder