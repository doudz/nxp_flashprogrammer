#! /usr/bin/env python3
from stat import *
import os, sys, struct, time, ZedSerialEnum, ZedSerialApi, traceback, logging
from EncryptUtils import *
from DeviceInfo import cDeviceInfo
import FirmwareImage


class teHeaderProcessing():
    OVERWRITE = 0
    RETAIN_ALL = 1
    CHANGE_MAC = 2
    CHANGE_MAC_AND_LICENCE = 3


class cFlashProgressIndicator():

    def __init__(self, sTitle='Default Title', sText='', iProgress=0, iNumSteps=0):
        self.sTitle = sTitle
        self.sText = sText
        self.iProgress = iProgress
        self.iNumSteps = iNumSteps

    def __repr__(self):
        return '%s\n  %s\n  Progress: %d/%d' % (self.sTitle, self.sText, self.iProgress, self.iNumSteps)

    def mSetTitle(self, sTitle):
        self.sTitle = sTitle

    def mSetText(self, sText):
        self.sText = sText

    def mSetNumSteps(self, iNumSteps):
        self.iNumSteps = iNumSteps

    def mNewOperation(self, sOperationText, iNumSteps):
        self.mSetText(sOperationText)
        self.mSetNumSteps(iNumSteps)
        self.mUpdateProgress(0)

    def mUpdateProgress(self, iProgress):
        self.iProgress = iProgress
        print(self)

    def bKeepGoing(self):
        return True

    def mDestroy(self):
        pass


class FlashUtilsError(Exception):

    def __init__(self, message):
        self.message = message


class cFlashUtilIF():

    def __init__(self, bRTSAsserted=True, DeviceInfo=None):
        self.logger = logging.getLogger('cFlashUtilIF')
        self.bRTSAsserted = bRTSAsserted
        self.DeviceInfo = DeviceInfo
        if self.DeviceInfo is None:
            self.DeviceInfo = cDeviceInfo()
        return

    def SetRTSAsserted(self, bRTSAsserted):
        self.bRTSAsserted = bRTSAsserted

    def mRefreshDeviceInfo(self, oZsa, b16BitAccess=False):
        status = self.DeviceInfo.mRefreshDeviceInfo(oZsa, b16BitAccess)
        if status != ZedSerialEnum.OK:
            raise FlashUtilsError(ZedSerialEnum.StatusStr(status))

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
                        self.logger.warning('Invalid header data processing selection specified - retaining existing header')
        if eHeaderProc != teHeaderProcessing.OVERWRITE:
            if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                abHeaderData = abHeaderData[:8]
        return abHeaderData

    def ReadBlock(self, oZsa, iStartAddress, iLen,
                  oProgressIndicator=cFlashProgressIndicator('Reading block of data from flash')):
        abBlockData = ''
        iAddress = 0
        try:
            if oZsa is not None and oZsa.mCheckOpened() == ZedSerialEnum.OK:
                oZsa.mSetRTS(False)
                iResidue = 0
                iChunk = 128
                iFullReads = iLen / iChunk
                if iLen % iChunk:
                    iResidue = iLen - iFullReads * iChunk
                maxi = iFullReads + 1
                count = 0
                if oProgressIndicator:
                    oProgressIndicator.mNewOperation('Reading %d blocks of %d bytes' % (maxi, iChunk), maxi)
                    if not oProgressIndicator.bKeepGoing():
                        raise FlashUtilsError('Flash block backup cancelled')
                iAddress = iStartAddress
                if iFullReads:
                    for i in range(iFullReads):
                        tFlashRead = oZsa.ZedFlashRead(iAddress, iChunk)
                        abBlockData += tFlashRead[1]
                        iAddress += iChunk
                        count += 1
                        if oProgressIndicator:
                            oProgressIndicator.mUpdateProgress(count)
                            if not oProgressIndicator.bKeepGoing():
                                raise FlashUtilsError('Flash block backup cancelled')

                if iResidue:
                    tFlashRead = oZsa.ZedFlashRead(iAddress, iResidue)
                    abBlockData += tFlashRead[1]
                    iAddress += iResidue
                    count += 1
                    if oProgressIndicator:
                        oProgressIndicator.mUpdateProgress(count)
                self.logger.info('Block read from Flash successfully')
            else:
                raise FlashUtilsError('Serial port not open')
        finally:
            if oZsa is not None:
                oZsa.mSetRTS(self.bRTSAsserted)
            if oProgressIndicator:
                oProgressIndicator.mDestroy()

        return (iAddress, abBlockData)

    def WriteBlock(self, oZsa, iStartAddress, abBlockData,
                   oProgressIndicator=cFlashProgressIndicator('Writing block of data to flash')):
        bRetVal = False
        try:
            if oZsa is not None and oZsa.mCheckOpened() == ZedSerialEnum.OK:
                oZsa.mSetRTS(False)
                iLen = len(abBlockData)
                iResidue = 0
                iChunk = 128
                iFullWrites = iLen / iChunk
                if iLen % iChunk:
                    iResidue = iLen - iFullWrites * iChunk
                count = 0
                maxi = iFullWrites + 1
                if oProgressIndicator:
                    oProgressIndicator.mNewOperation('Writing %d blocks of %d bytes' % (maxi, iChunk), maxi)
                    if not oProgressIndicator.bKeepGoing():
                        raise FlashUtilsError('Flash block restore cancelled')
                tFlashRead = oZsa.ZedFlashRead(iStartAddress, iChunk)
                if tFlashRead[1][0:8] != '':
                    raise FlashUtilsError('Cannot write to flash twice')
                iIdx = 0
                if iFullWrites > 0:
                    for i in range(iFullWrites):
                        abBytesRead = abBlockData[iIdx:iIdx + iChunk]
                        eStatus = oZsa.ZedFlashProg(iStartAddress + iIdx, abBytesRead)
                        if eStatus != ZedSerialEnum.OK:
                            raise FlashUtilsError('Error (0x%02X) writing to flash device' % eStatus)
                        count += 1
                        if oProgressIndicator:
                            oProgressIndicator.mUpdateProgress(count)
                            if not oProgressIndicator.bKeepGoing():
                                raise FlashUtilsError('Flash block restore cancelled')
                        iIdx += iChunk

                if iResidue > 0:
                    abBytesRead = abBlockData[iIdx:iIdx + iResidue]
                    eStatus = oZsa.ZedFlashProg(iStartAddress + iIdx, abBytesRead)
                    if eStatus != ZedSerialEnum.OK:
                        raise FlashUtilsError('Error (0x%02X) writing to flash device' % eStatus)
                    count += 1
                    if oProgressIndicator:
                        oProgressIndicator.mUpdateProgress(count)
                self.logger.info('Block to Flash successfully')
                bRetVal = True
            else:
                raise FlashUtilsError('Serial port not open')
        finally:
            if oZsa is not None:
                oZsa.mSetRTS(self.bRTSAsserted)
            if oProgressIndicator:
                oProgressIndicator.mDestroy()

        return bRetVal

    def bProgramFileIntoFlash(self, oZsa, eHeaderProc, abNewHeaderData, sFlashFile,
                              oProgressIndicator=cFlashProgressIndicator('Writing program to flash'),
                              bPatchSPIBusCfgFor16BitAddrBus=False, bSectorErase=False):
        oFile = None
        bRetVal = False
        try:
            if oZsa is not None:
                if oZsa.mCheckOpened() == ZedSerialEnum.OK:
                    abHeaderData = self.DefineHeaderData(oZsa, eHeaderProc, abNewHeaderData)
                    oZsa.mSetRTS(False)
                    self.logger.debug('Opening file "%s"' % sFlashFile)
                    try:
                        oFile = open(sFlashFile, 'rb')
                    except Exception:
                        raise FlashUtilsError('Could not find file "' + sFlashFile + '" for programming')
                    else:
                        iFileLength = os.stat(sFlashFile)[ST_SIZE]
                        if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                            iFileLength = iFileLength - 4
                            iBytesRead = oFile.read(4)
                        iResidue = 0
                        iChunk = 128
                        iFullReads = iFileLength / iChunk
                        if iFileLength % iChunk:
                            iResidue = iFileLength - iFullReads * iChunk
                        count = 0
                        maxi = iFullReads + 1
                        if bSectorErase and oProgressIndicator:
                            oProgressIndicator.mNewOperation('Erasing Flash Sectors', 3)
                            if not oProgressIndicator.bKeepGoing():
                                raise FlashUtilsError('Flash programming cancelled')
                        for iSector in range(0, 4):
                            bProgressOK = oZsa.ZedFlashSectorErase(iSector) == ZedSerialEnum.OK
                            if not bProgressOK:
                                raise FlashUtilsError('Sector Erase Failed!')
                            elif oProgressIndicator:
                                oProgressIndicator.mUpdateProgress(iSector)

                if oProgressIndicator:
                    oProgressIndicator.mNewOperation('Erasing Flash Device', 1)
                oZsa.mSetRxTimeOut(10000)
                bProgressOK = oZsa.ZedFlashBulkErase() == ZedSerialEnum.OK
                oZsa.mSetRxTimeOut(ZedSerialApi.DEFAULT_READ_TIMEOUT)
                if oProgressIndicator:
                    oProgressIndicator.mUpdateProgress(1)
                    if not oProgressIndicator.bKeepGoing():
                        raise FlashUtilsError('Flash programming cancelled')
                if bProgressOK == 0:
                    raise FlashUtilsError('Failed to erase device; check cabling and power')
                tFlashRead = oZsa.ZedFlashRead(0, iChunk)
                if tFlashRead[1][0:8] != '':
                    raise FlashUtilsError('Failed to erase flash; check write protect pin')
                if oProgressIndicator:
                    oProgressIndicator.mNewOperation('Writing %d blocks of %d bytes' % (maxi, iChunk), maxi)
                    if not oProgressIndicator.bKeepGoing():
                        raise FlashUtilsError('Flash programming cancelled')
                iAddress = 0
                if iFullReads > 0:
                    for i in range(iFullReads):
                        abBytesRead = oFile.read(iChunk)
                        self.logger.debug('Read chunk: %s' % str(list(abBytesRead)))
                        if i == 0:
                            if eHeaderProc != teHeaderProcessing.OVERWRITE:
                                abBytesRead = abBytesRead[0:self.DeviceInfo.lMacAddressLocationInFlash] + abHeaderData + abBytesRead[self.DeviceInfo.lMacAddressLocationInFlash + len(abHeaderData):]
                                self.logger.debug('Add in MAC Address: %s' % str(list(abBytesRead)))
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
                                        raise FlashUtilsError('The two SPI bus configuration bytes in the FW file header differ')
                                    if u8SpiCfg1 & SPI_CFG_BUS_WIDTH_24_BIT:
                                        u8SpiCfg1 = u8SpiCfg1 & ~SPI_CFG_BUS_WIDTH_24_BIT
                                        abBytesRead = struct.pack('<BBBB', u8Scramble1, u8Scramble2, u8SpiCfg1, u8SpiCfg1) + abBytesRead[FH_CFG_BYTES_IDX + 4:]
                        oZsa.ZedFlashProg(iAddress, abBytesRead)
                        count += 1
                        self.logger.debug('Programming address %d/%d' % (i, iFullReads))
                        if oProgressIndicator:
                            oProgressIndicator.mUpdateProgress(count)
                            if not oProgressIndicator.bKeepGoing():
                                raise FlashUtilsError('Flash programming cancelled')
                        iAddress += iChunk

                if iResidue > 0:
                    abBytesRead = oFile.read(iResidue)
                    oZsa.ZedFlashProg(iAddress, abBytesRead)
                    count += 1
                    if oProgressIndicator:
                        oProgressIndicator.mUpdateProgress(count)
                self.logger.info('Program written to Flash successfully')
                bRetVal = True
            else:
                raise FlashUtilsError('Serial port not open')
        finally:
            if oZsa is not None:
                oZsa.mSetRTS(self.bRTSAsserted)
            if oProgressIndicator:
                oProgressIndicator.mDestroy()
            if oFile is not None:
                oFile.close()

        return bRetVal

    def bProgramImageIntoFlash(self, oZsa, oFirmwareImage,
                               oProgressIndicator=cFlashProgressIndicator('Writing program to flash'),
                               bSectorErase=False):
        oFile = None
        bRetVal = False
        try:
            if oZsa is not None:
                if oZsa.mCheckOpened() == ZedSerialEnum.OK:
                    oZsa.mSetRTS(False)
                    iChunkSize = 128
                    iFullReads = oFirmwareImage.iSize / iChunkSize
                    maxi = iFullReads
                    if oFirmwareImage.iSize % iChunkSize:
                        maxi = iFullReads + 1
                    if bSectorErase and oProgressIndicator:
                        oProgressIndicator.mNewOperation('Erasing Flash Sectors', 3)
                        if not oProgressIndicator.bKeepGoing():
                            raise FlashUtilsError('Flash programming cancelled')
                    for iSector in range(0, 4):
                        bProgressOK = oZsa.ZedFlashSectorErase(iSector) == ZedSerialEnum.OK
                        if not bProgressOK:
                            raise FlashUtilsError('Sector Erase Failed!')
                        elif oProgressIndicator:
                            oProgressIndicator.mUpdateProgress(iSector)

                if oProgressIndicator:
                    oProgressIndicator.mNewOperation('Erasing Flash Device', 1)
                oZsa.mSetRxTimeOut(10000)
                bProgressOK = oZsa.ZedFlashBulkErase() == ZedSerialEnum.OK
                oZsa.mSetRxTimeOut(ZedSerialApi.DEFAULT_READ_TIMEOUT)
                if oProgressIndicator:
                    oProgressIndicator.mUpdateProgress(1)
                    if not oProgressIndicator.bKeepGoing():
                        raise FlashUtilsError('Flash programming cancelled')
                if bProgressOK == 0:
                    raise FlashUtilsError('Failed to erase device; check cabling and power')
                tFlashRead = oZsa.ZedFlashRead(0, iChunkSize)
                if tFlashRead[1][0:8] != '':
                    raise FlashUtilsError('Failed to erase flash; check write protect pin')
                if oProgressIndicator:
                    oProgressIndicator.mNewOperation('Writing %d blocks of %d bytes' % (maxi, iChunkSize), maxi)
                    if not oProgressIndicator.bKeepGoing():
                        raise FlashUtilsError('Flash programming cancelled')
                iAddress = 0
                for i in range(maxi):
                    abBytesRead = oFirmwareImage.ReadChunk(i, iChunkSize)
                    self.logger.debug('Programming address %d/%d with data: %s' % (i, maxi, str(list(abBytesRead))))
                    oZsa.ZedFlashProg(iAddress, abBytesRead)
                    if oProgressIndicator:
                        oProgressIndicator.mUpdateProgress(i + 1)
                        if not oProgressIndicator.bKeepGoing():
                            raise FlashUtilsError('Flash programming cancelled')
                    iAddress += iChunkSize

                self.logger.info('Program written to Flash successfully')
                bRetVal = True
            else:
                raise FlashUtilsError('Serial port not open')
        finally:
            if oZsa is not None:
                oZsa.mSetRTS(self.bRTSAsserted)
            if oProgressIndicator:
                oProgressIndicator.mDestroy()
            if oFile is not None:
                oFile.close()

        return bRetVal

    def bProgramFileIntoRAM(self, oZsa, eHeaderProc, abNewHeaderData, sFile,
                            oProgressIndicator=cFlashProgressIndicator('Copying program to RAM')):
        oFile = None
        bRetVal = False
        self.logger.debug("bProgramFileIntoRAM('%s')" % sFile)
        try:
            if oZsa is not None and oZsa.mCheckOpened() == ZedSerialEnum.OK:
                abHeaderData = self.DefineHeaderData(oZsa, eHeaderProc, abNewHeaderData)
                oZsa.mSetRTS(False)
                try:
                    oFile = open(sFile, 'rb')
                except:
                    raise FlashUtilsError('Could not find file "' + sFile + '" for programming')
                else:
                    iFileLength = os.stat(sFile)[ST_SIZE]
                    if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                        self.logger.debug('Bootloader v2 header')
                        iFileLength -= 60
                        sFlashHeader = oFile.read(60)
                        iRAMStart, iRAMLen = struct.unpack('>HH', sFlashHeader[44:48])
                        iRAMStart = iRAMStart * 4 + 67108864
                        iRAMLen = iRAMLen * 4
                        iRAMResetEntry = struct.unpack('>L', sFlashHeader[56:60])[0]
                    else:
                        self.logger.debug('Bootloader v1 header')
                        iFileLength -= self.DeviceInfo.lMacAddressLocationInFlash
                        sFlashHeader = oFile.read(self.DeviceInfo.lMacAddressLocationInFlash)
                        iRAMStart, iRAMLen = struct.unpack('>LL', sFlashHeader[FH_TEXT_SEGM_ADDR_IDX:FH_TEXT_SEGM_ADDR_IDX + 8])
                        if iRAMLen == 0:
                            iRAMStart, iRAMLen = struct.unpack('>LL', sFlashHeader[FH_DATA_SEGM_ADDR_IDX:FH_DATA_SEGM_ADDR_IDX + 8])
                        iRAMResetEntry = struct.unpack('>L', sFlashHeader[FH_RESET_ENTRY_POINT_IDX:FH_RESET_ENTRY_POINT_IDX + 4])[0]
                    if iRAMLen == 0:
                        self.logger.debug('Invalid RAM Length (0) read from file')
                        raise FlashUtilsError('Invalid header information found in file')
                    self.logger.debug('RAM start address: 0x%08x, length: 0x%08x' % (iRAMStart, iRAMLen))
                    self.logger.debug('Reset Entry point: 0x%08x' % iRAMResetEntry)
                    iResidue = 0
                    iChunk = 128
                    iFullReads = iFileLength / iChunk
                    if iFileLength % iChunk:
                        iResidue = iFileLength - iFullReads * iChunk
                    count = 0
                    maxi = iFullReads + 1
                    if oProgressIndicator:
                        oProgressIndicator.mNewOperation('Copying %d blocks of %d bytes' % (maxi, iChunk), maxi)
                    iAddress = iRAMStart
                    if iFullReads > 0:
                        for i in range(iFullReads):
                            abBytesRead = oFile.read(iChunk)
                            if i == 0 and eHeaderProc != teHeaderProcessing.OVERWRITE:
                                abBytesRead = abBytesRead[0:self.DeviceInfo.lMacAddressLocationInFlash] + abHeaderData + abBytesRead[self.DeviceInfo.lMacAddressLocationInFlash + len(abHeaderData):]
                            oZsa.ZedRAMwrite(iAddress, abBytesRead)
                            count += 1
                            if oProgressIndicator:
                                oProgressIndicator.mUpdateProgress(count)
                                if not oProgressIndicator.bKeepGoing:
                                    raise FlashUtilsError('RAM copying cancelled')
                            iAddress += iChunk

                    if iResidue > 0:
                        abBytesRead = oFile.read(iResidue)
                        oZsa.ZedRAMwrite(iAddress, abBytesRead)
                        count += 1
                        if oProgressIndicator:
                            oProgressIndicator.mUpdateProgress(count)
                    self.logger.info('Program written to RAM successfully')
                    bRetVal = True
            else:
                raise FlashUtilsError('Serial port not open')
        finally:
            if oZsa is not None:
                oZsa.mSetRTS(self.bRTSAsserted)
            if oProgressIndicator:
                oProgressIndicator.mDestroy()
            if oFile is not None:
                oFile.close()

        return iRAMResetEntry

    def bVerifyFlashFile(self, oZsa, eHeaderProc, abNewHeaderData, sFlashFile,
                         oProgressIndicator=cFlashProgressIndicator('Verifying program in flash'),
                         bPatchSPIBusCfgFor16BitAddrBus=False):
        oFile = None
        try:
            if oZsa is not None and oZsa.mCheckOpened() == ZedSerialEnum.OK:
                oZsa.mSetRTS(False)
                self.logger.debug('Opening file "%s"' % sFlashFile)
                try:
                    oFile = open(sFlashFile, 'rb')
                except:
                    raise FlashUtilsError('Could not find file "' + sFlashFile + '" for verifying')
                else:
                    iFileLength = os.stat(sFlashFile)[ST_SIZE]
                    if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                        iFileLength = iFileLength - 4
                        iBytesRead = oFile.read(4)
                    iResidue = 0
                    iChunk = 128
                    iFullReads = iFileLength / iChunk
                    if iFileLength % iChunk:
                        iResidue = iFileLength - iFullReads * iChunk
                    count = 0
                    maxi = iFullReads + 1
                    if oProgressIndicator:
                        oProgressIndicator.mNewOperation('Verifying %d blocks of %d bytes' % (maxi, iChunk), maxi)
                    abHeaderData = self.DefineHeaderData(oZsa, eHeaderProc, abNewHeaderData)
                    iAddress = 0
                    iErrors = []
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
                                            FlashUtilsError('The two SPI bus configuration bytes in the FW file header differ')
                                        if u8SpiCfg1 & SPI_CFG_BUS_WIDTH_24_BIT:
                                            u8SpiCfg1 = u8SpiCfg1 & ~SPI_CFG_BUS_WIDTH_24_BIT
                                            abBytesRead = struct.pack('<BBBB', u8Scramble1, u8Scramble2, u8SpiCfg1, u8SpiCfg1) + abBytesRead[FH_CFG_BYTES_IDX + 4:]
                            tFlashRead = oZsa.ZedFlashRead(iAddress, iChunk)
                            if abBytesRead != tFlashRead[1]:
                                self.logger.warning('Verification error at block %d\n(Read %s\nExpected %s)' % (i, str(list(tFlashRead[1])), str(list(abBytesRead))))
                                iErrors.append(count)
                            iAddress += iChunk
                            count += 1
                            if oProgressIndicator:
                                oProgressIndicator.mUpdateProgress(count)
                                if not oProgressIndicator.bKeepGoing():
                                    raise FlashUtilsError('Flash verification cancelled')

                    if iResidue > 0:
                        abBytesRead = oFile.read(iResidue)
                        tFlashRead = oZsa.ZedFlashRead(iAddress, iResidue)
                        if abBytesRead != tFlashRead[1]:
                            iErrors.append(count)
                        count += 1
                        if oProgressIndicator:
                            oProgressIndicator.mUpdateProgress(count)
                    if len(iErrors) > 0:
                        raise FlashUtilsError('Errors in data verification, blocks %s differ' % str(iErrors))
                    else:
                        self.logger.info('Data verification OK - the device has been reflashed')
            else:
                raise FlashUtilsError('Serial port not open')
        finally:
            if oZsa is not None:
                oZsa.mSetRTS(self.bRTSAsserted)
            if oProgressIndicator:
                oProgressIndicator.mDestroy()
            if oFile is not None:
                oFile.close()

        return len(iErrors) == 0

    def bVerifyFlashImage(self, oZsa, oFirmwareImage,
                          oProgressIndicator=cFlashProgressIndicator('Verifying program in flash')):
        oFile = None
        try:
            if oZsa is not None and oZsa.mCheckOpened() == ZedSerialEnum.OK:
                oZsa.mSetRTS(False)
                iChunkSize = 128
                iFullReads = oFirmwareImage.iSize / iChunkSize
                maxi = iFullReads
                if oFirmwareImage.iSize % iChunkSize:
                    maxi = iFullReads + 1
                if oProgressIndicator:
                    oProgressIndicator.mNewOperation('Verifying %d blocks of %d bytes' % (maxi, iChunkSize), maxi)
                iAddress = 0
                iErrors = []
                count = 0
                for i in range(maxi):
                    abBytesRead = oFirmwareImage.ReadChunk(i, iChunkSize)
                    tFlashRead = oZsa.ZedFlashRead(iAddress, iChunkSize)
                    if abBytesRead != tFlashRead[1]:
                        self.logger.warning('Verification error at block %d\n(Read %s\nExpected %s)' % (i, str(list(tFlashRead[1])), str(list(abBytesRead))))
                        iErrors.append(i)
                    iAddress += iChunkSize
                    count += 1
                    if oProgressIndicator:
                        oProgressIndicator.mUpdateProgress(i)
                        if not oProgressIndicator.bKeepGoing():
                            raise FlashUtilsError('Flash verification cancelled')

                if len(iErrors) > 0:
                    raise FlashUtilsError('Errors in data verification, blocks %s differ' % str(iErrors))
                else:
                    self.logger.info('Data verification OK - the device has been reflashed')
            else:
                raise FlashUtilsError('Serial port not open')
        finally:
            if oZsa is not None:
                oZsa.mSetRTS(self.bRTSAsserted)
            if oProgressIndicator:
                oProgressIndicator.mDestroy()
            if oFile is not None:
                oFile.close()

        return len(iErrors) == 0

    def bProgramJN615xMacAddress(self, oZsa, sMacAddress,
                                 oProgressIndicator=cFlashProgressIndicator('Programming MAC Address')):
        sFile = 'FlashProgrammerExtension_JN5168.bin'
        sTitle = 'Programming MAC Address'
        abRAMNewHeaderData = None
        try:
            iResetEntry = self.bProgramFileIntoRAM(oZsa, teHeaderProcessing.OVERWRITE, None, sFile, oProgressIndicator)
        except FlashUtilsError as e:
            raise FlashUtilsError('Error loading into RAM (%s)' % e.message)
        else:
            bSuccess = iResetEntry != 0
            if bSuccess == 0:
                self.logger.debug('Invalid entry point in extension image')
                raise FlashUtilsError('Error Programming MAC address')

        try:
            iRet, sSerRet = oZsa.RunProgramInRAM(iResetEntry)
            if iRet != ZedSerialEnum.OK:
                raise FlashUtilsError('Error runnning program in RAM. Please check cabling and power')
        except Exception as e:
            raise FlashUtilsError('Error runnning program in RAM. Please check cabling and power (%s)' % str(e))

        if oZsa is not None and oZsa.mCheckOpened() == ZedSerialEnum.OK:
            oZsa.mSetRxTimeOut(10000)
            WriteBytes = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
            for i in range(0, 8):
                WriteBytes[i] = ord(sMacAddress[i])

            try:
                self.logger.info('Program MAC in index sector: 0x%02x:%02x:%02x:%02x:%02x:%02x:%02x:%02x' % (
                 WriteBytes[0], WriteBytes[1], WriteBytes[2], WriteBytes[3],
                 WriteBytes[4], WriteBytes[5], WriteBytes[6], WriteBytes[7]))
                if oZsa.ZedProgramIndexSector(self.DeviceInfo.lMacAddressLocationInIndex[0], self.DeviceInfo.lMacAddressLocationInIndex[1], WriteBytes) != ZedSerialEnum.OK:
                    raise FlashUtilsError('Index sector programming failed')
            except FlashUtilsError as e:
                self.logger.debug('Error programming mac address (%s)' % e.message)
                raise FlashUtilsError('Error Programming MAC address')
            finally:
                oZsa.mSetRxTimeOut(ZedSerialApi.DEFAULT_READ_TIMEOUT)
                iRet, sSerRet = oZsa.RunProgramInRAM(self.DeviceInfo.iBootloaderEntryPoint)
                time.sleep(0.5)
                return True

        else:
            raise FlashUtilsError('Error Programming MAC address')
        return


if __name__ == '__main__':
    from optparse import OptionParser
    logging.basicConfig(format='%(asctime)-15s %(name)s:%(levelname)s:%(message)s')
    logging.getLogger().setLevel(logging.DEBUG)
    parser = OptionParser()
    parser.add_option('-s', '--serial', dest='serialDevice', type='string',
                      default=None, help='Use serial device', metavar='DEVICE')
    parser.add_option('-f', '--file', dest='fileName', type='string',
                      default=None, help='Binary file to program', metavar='FILE')
    options, args = parser.parse_args()
    if options.serialDevice is None:
        print('You must specify a serial device to connect to')
        sys.exit(1)
    if options.fileName is None:
        print('You must specify a file to program')
        sys.exit(1)
    sComPort = options.serialDevice
    print('Connecting to device on %s' % sComPort)
    oZsa = ZedSerialApi.cZedSerialApi(38400, sComPort)
    eHeaderDataProcessing = teHeaderProcessing.RETAIN_ALL
    abNewHeaderData = None
    sFlashFile = options.fileName
    oZsa.mSetRTS(True)
    oZsa.mSetDebug(0)
    print('Cycle power on the device (to enable connection to flash loader)\n\nPress <ENTER> when done')
    sys.stdin.readline()
    print('Verifying connection to flash')
    oZsa.mSetRTS(False)
    FlashUtilIF = cFlashUtilIF()
    FlashUtilIF.mRefreshDeviceInfo(oZsa)
    print(FlashUtilIF.DeviceInfo)
    oFirmwareImage = FirmwareImage.cFirmwareImage(FlashUtilIF.DeviceInfo, sFlashFile)
    if not FlashUtilIF.DeviceInfo.bInternalFlash:
        oFirmwareImage.UpdateMACAddress(FlashUtilIF.DeviceInfo.abMacAddress)
        oFirmwareImage.UpdateZBLicense(FlashUtilIF.DeviceInfo.abZBLicense)
        oFirmwareImage.UpdateUserData(FlashUtilIF.DeviceInfo.abUserData)
    try:
        print('Testing firmware image write')
        bSuccess = FlashUtilIF.bProgramImageIntoFlash(oZsa, oFirmwareImage)
        if bSuccess:
            print('Programming success')
        else:
            print('Programming failed')
    except FlashUtilsError as e:
        print('Flash program operation failed:', e.message)
        sys.exit(1)
    except Exception as e:
        raise e
        sys.exit(1)
    else:
        try:
            bSuccess = FlashUtilIF.bVerifyFlashFile(oZsa, eHeaderDataProcessing, abNewHeaderData, sFlashFile)
            if bSuccess:
                print('Verification success')
            else:
                print('Verification failed')
        except FlashUtilsError as e:
            print('Flash program operation failed:', e.message)
            sys.exit(1)
        except Exception as e:
            raise e
            sys.exit(1)
