# uncompyle6 version 3.2.5
# Python bytecode 2.6 (62161)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: ZedSerialApi.pyo
# Compiled at: 2013-01-18 15:16:13
import sys, struct, time, logging, ZedSerialProtocol, ZedSerialEnum, EncryptUtils
JN51XX_REG_ID = 268435708
JN5121_CHIP_ID = 32
JN5139v0_CHIP_ID = 2097152
E_FL_CHIP_ST_M25P10_A = 0
E_FL_CHIP_SST_25VF010 = 1
E_FL_CHIP_ATMEL_AT25F512 = 2
E_FL_CHIP_ST_M25P40 = 3
E_FL_CHIP_ST_M25P05_A = 4
E_FL_CHIP_ST_M25P20_A = 5
E_FL_CHIP_CUSTOM = 6
E_FL_CHIP_AUTO = 7
E_FL_CHIP_INTERNAL = 8
PROC_PARTNO_NONE = -1
PROC_PARTNO_JN5121 = 0
PROC_PARTNO_JN5139 = 2
PROC_REV_NONE = -1
PROC_MASK_NONE = -1
LOGIN_OK = 0
LOGIN_FAILED_MAC_ADDRESS = 1
LOGIN_FAILED_NO_RESPONSE = 2
LOGIN_FAILED_PASSKEY_FAIL = 3
DEFAULT_READ_TIMEOUT = 1000
bHdkTest = False
if bHdkTest == False:
    JAGUAR_EFUSE_LOCATION = 33558624
else:
    JAGUAR_EFUSE_LOCATION = 128

class cZedSerialApi():

    def __init__(self, iBaudrate, sComPort):
        self.logger = logging.getLogger('ZedSerialApi(%s)' % sComPort)
        self.logger.info('Open device, baudrate %d' % iBaudrate)
        self.sComPort = sComPort
        self.iBaudrate = iBaudrate
        self.RxTimeOut = 1
        self.bDeviceControlEnabled = True
        self.oZsp = ZedSerialProtocol.cZedSerialProtocol(self.sComPort, self.iBaudrate, self.RxTimeOut)
        self.oZdc = ZedSerialProtocol.cDeviceControl(self.sComPort)
        self.bDebug = False
        self.iProcessorPartNo = PROC_PARTNO_NONE
        self.iProcessorRevNo = PROC_REV_NONE
        self.iMaskNo = PROC_MASK_NONE
        if self.oZsp.mCheckOpened() == ZedSerialEnum.OK:
            self.mSetRxTimeOut(DEFAULT_READ_TIMEOUT)

    def __del__(self):
        self.logger.debug('Delete')
        self.mClose()

    def mEnterProgrammingMode(self):
        if self.bDeviceControlEnabled:
            self.oZsp.mClose()
            self.oZdc.mEnterProgrammingMode()
            self.oZsp = ZedSerialProtocol.cZedSerialProtocol(self.sComPort, self.iBaudrate, self.RxTimeOut)

    def mReset(self):
        if self.bDeviceControlEnabled:
            self.oZsp.mClose()
            self.oZdc.mReset()
            self.oZsp = ZedSerialProtocol.cZedSerialProtocol(self.sComPort, self.iBaudrate, self.RxTimeOut)

    def mCheckOpened(self):
        zspStatus = self.oZsp.mCheckOpened()
        self.logger.debug('Is open: %s' % str(zspStatus))
        return zspStatus

    def mSetDebug(self, bDebug):
        self.bDebug = bDebug

    def mClose(self):
        self.logger.debug('Close')
        self.oZsp.mClose()

    def mSetRxTimeOut(self, RxTimeOut):
        self.logger.debug('Set Timeout %d' % RxTimeOut)
        self.RxTimeOut = RxTimeOut
        self.oZsp.mSetRxTimeOut(RxTimeOut)

    def SetBaudrate(self, Baudrate):
        self.logger.debug('Set Baudrate %d' % Baudrate)
        self.iBaudrate = Baudrate
        self.oZsp.SetBaudrate(Baudrate)

    def mSetRTS(self, RTSstate):
        self.oZsp.mSetRTS(RTSstate)

    def mSendMsg(self, sOutMsg, sName):
        self.logger.debug('mSendMsg')
        if self.bDebug:
            iReqType = struct.unpack('<B', sOutMsg[0])[0]
            self.logger.debug('%s.%s' % (sName, ZedSerialEnum.SerProtCodeStr(iReqType)))
        if self.oZsp.mWrite(sOutMsg) != ZedSerialEnum.OK:
            self.logger.info('Write failed')
            return ZedSerialEnum.WRITE_FAIL
        return ZedSerialEnum.OK

    def mReceiveMsg(self, sName):
        self.logger.debug('mReceiveMsg')
        iRet, sInMsg = self.oZsp.mRead()
        if self.bDebug:
            iRspType, iStatus = struct.unpack('<BB', sInMsg[0:2])
            if iStatus == ZedSerialEnum.OK:
                self.logger.debug('%s.%s' % (sName, ZedSerialEnum.SerProtCodeStr(iRspType)))
            else:
                self.logger.debug('%s.Rcv => %s' % (sName, ZedSerialEnum.StatusStr(iStatus)))
        return (iRet, sInMsg)

    def mCheckData(self, sData, iResponse, sName):
        if len(sData) >= 2:
            iFrameType, iStatus = struct.unpack('<BB', sData[0:2])
            if iFrameType != iResponse:
                if self.bDebug:
                    self.logger.debug('%s invalid response' % sName)
                return ZedSerialEnum.INVALID_RESPONSE
            if iStatus != 0:
                if self.bDebug:
                    self.logger.debug('%s response error %s(%d)' % (sName, ZedSerialEnum.StatusStr(iStatus), iStatus))
                return iStatus
            return ZedSerialEnum.OK
        else:
            if self.bDebug:
                self.logger.debug('%s invalid length (%d)' % (sName, len(sData)))
            return ZedSerialEnum.INVALID_RESPONSE

    def ZedFlashSetChipSelect(self, iChipSelect, iDivisor=None):
        sName = 'ZedFlashSetChipSelect'
        self.logger.debug(sName)
        if iDivisor is None:
            iRet = self.mSendMsg(struct.pack('<BB', ZedSerialEnum.TYPE_SET_CS_REQUEST, iChipSelect), sName)
        else:
            iRet = self.mSendMsg(struct.pack('<BBB', ZedSerialEnum.TYPE_SET_CS_REQUEST, iChipSelect, iDivisor), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_SET_CS_RESPONSE, sName)
        return iRet

    def ZedReset(self):
        sName = 'ZedFlashReset'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<B', ZedSerialEnum.TYPE_SET_RESET_REQUEST), sName)
        return iRet

    def ZedFlashBulkErase(self):
        sName = 'ZedFlashBulkErase'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<B', ZedSerialEnum.TYPE_FL_ERASE_REQUEST), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_ERASE_RESPONSE, sName)
        return iRet

    def ZedPDMErase(self, bForceErase):
        sName = 'ZedPDMErase'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BB', ZedSerialEnum.TYPE_PDM_ERASE_REQUEST, bForceErase), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_PDM_ERASE_RESPONSE, sName)
        return iRet

    def ZedFlashSectorErase(self, iSector):
        sName = 'ZedFlashSectorErase'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BB', ZedSerialEnum.TYPE_FL_SECTOR_ERASE_REQUEST, iSector), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_SECTOR_ERASE_RESPONSE, sName)
        return iRet

    def ZedFlashWriteSr(self, iSr):
        sName = 'ZedFlashWriteSr'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BB', ZedSerialEnum.TYPE_FL_WRITE_SR_REQUEST, iSr), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_WRITE_SR_RESPONSE, sName)
        return iRet

    def ZedFlashReadSR(self):
        sName = 'ZedFlashReadSR'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<B', ZedSerialEnum.TYPE_FL_READ_SR_REQUEST), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                iRet = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_READ_SR_RESPONSE, sName)
                if iRet == ZedSerialEnum.OK:
                    return (ZedSerialEnum.OK, sInMsg[2:])
        return (
         iRet, 0)

    def ZedFlashReadId(self):
        sName = 'ZedFlashReadId'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<B', ZedSerialEnum.TYPE_FL_READ_ID_REQUEST), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                iRet = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_READ_ID_RESPONSE, sName)
                if iRet == ZedSerialEnum.OK:
                    return (ZedSerialEnum.OK, sInMsg[2:])
        return (
         iRet, 0)

    def ZedFlashSelect(self, eFlash):
        sName = 'ZedFlashSelect'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BB', ZedSerialEnum.TYPE_FL_SELECT_FLASH_REQUEST, eFlash), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_SELECT_FLASH_RESPONSE, sName)
        return iRet

    def ZedFlashProg(self, iFlashAddr, sData):
        sName = 'ZedFlashProg'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BL', ZedSerialEnum.TYPE_FL_PROG_REQUEST, iFlashAddr) + sData, sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_PROG_RESPONSE, sName)
        return iRet

    def ZedFlashRead(self, iFlashAddr, iLen):
        sName = 'ZedFlashRead'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BLH', ZedSerialEnum.TYPE_FL_READ_REQUEST, iFlashAddr, iLen), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                iRet = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_READ_RESPONSE, sName)
                if iRet == ZedSerialEnum.OK:
                    return (ZedSerialEnum.OK, sInMsg[2:])
        return (
         iRet, 0)

    def ZedRAMwrite(self, iRAMAddr, sData):
        sName = 'ZedRAMwrite'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BL', ZedSerialEnum.TYPE_RM_WRITE_REQUEST, iRAMAddr) + sData, sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_RM_WRITE_RESPONSE, sName)
        return iRet

    def ZedRAMRead(self, iRAMAddr, iLen):
        sName = 'ZedRAMRead'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BLH', ZedSerialEnum.TYPE_RM_READ_REQUEST, iRAMAddr, iLen), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                iRet = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_RM_READ_RESPONSE, sName)
                if iRet == ZedSerialEnum.OK:
                    return (ZedSerialEnum.OK, sInMsg[2:])
        return (
         iRet, 0)

    def ZedDetectFushSecured(self):
        sName = 'ZedGetFuseSecured'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<B', ZedSerialEnum.TYPE_GET_FUSE_SECURED_REQUEST), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                iRet = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_GET_FUSE_SECURED_RESPONSE, sName)
                if iRet == ZedSerialEnum.OK:
                    if struct.unpack('<B', sInMsg[2])[0] == 1:
                        if struct.unpack('<B', sInMsg[3])[0] == 1:
                            return ZedSerialEnum.FUSE_SECURED_LOGGEDIN
                        return ZedSerialEnum.FUSE_SECURED_NOT_LOGGEDIN
        return ZedSerialEnum.FUSE_NOT_SECURED

    def ZedDetectProcessorVersion(self):
        bDoRamRead = True
        sName = 'ZedGetChipID'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<B', ZedSerialEnum.TYPE_GET_CHIP_ID_REQUEST), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                iRet = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_GET_CHIP_ID_RESPONSE, sName)
                if iRet == ZedSerialEnum.OK:
                    abProcVer = sInMsg[2:]
                    bDoRamRead = False
                    self.logger.debug('Processor version = %s' % abProcVer)
        if bDoRamRead == True:
            eReadResult, abProcVer = self.ZedRAMRead(JN51XX_REG_ID, 4)
            if eReadResult != ZedSerialEnum.OK:
                self.iProcessorPartNo == PROC_PARTNO_NONE
                return eReadResult
        u32ChipId = struct.unpack('>L', abProcVer)[0]
        if u32ChipId == JN5139v0_CHIP_ID:
            self.iProcessorPartNo = PROC_PARTNO_JN5139
            self.iProcessorRevNo = 0
        else:
            self.iProcessorRevNo = u32ChipId >> 28 & 15
            self.iProcessorPartNo = u32ChipId >> 12 & 1023
            self.iMaskNo = u32ChipId >> 22 & 63
            if self.iProcessorPartNo == 4 and self.iProcessorRevNo == 1 and self.iMaskNo == 1:
                eReadResult, abProcVer = self.ZedRAMRead(4, 4)
                if eReadResult == ZedSerialEnum.OK:
                    u32RomId = struct.unpack('>L', abProcVer)[0]
                    if u32RomId == 33947702:
                        self.iMaskNo = 3
        self.logger.debug('ProcPartNo = %d' % self.iProcessorPartNo)
        self.logger.debug('ProcRevNo  = %d' % self.iProcessorRevNo)
        self.logger.debug('ProcMaskNo = %d' % self.iMaskNo)
        return ZedSerialEnum.OK

    def ZedRegisterRead(self, iRegAddr):
        sName = 'ZedRegisterRead'
        self.logger.debug(sName)
        if self.iProcessorPartNo == PROC_PARTNO_NONE:
            iRet = self.ZedDetectProcessorVersion()
            if iRet != ZedSerialEnum.OK:
                return (iRet, 0)
        if self.iProcessorPartNo == PROC_PARTNO_JN5121:
            iRet, abReadValue = self.ZedRAMRead(iRegAddr, 4)
            if iRet == ZedSerialEnum.OK:
                u32RegVal = struct.unpack('>L', abReadValue)[0]
                return (
                 iRet, u32RegVal)
            return (iRet, 0)
        if self.iProcessorPartNo == PROC_PARTNO_JN5139 and self.iProcessorRevNo == 0:
            iRet, abReadValue = self.ZedRAMRead(iRegAddr, 4)
            if iRet == ZedSerialEnum.OK:
                u32RegVal = struct.unpack('<L', abReadValue)[0]
                return (
                 iRet, u32RegVal)
            return (iRet, 0)
        iRet = self.mSendMsg(struct.pack('<BLH', ZedSerialEnum.TYPE_REG_READ_REQUEST, iRegAddr, 4), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                iRet = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_REG_READ_RESPONSE, sName)
                if iRet == ZedSerialEnum.OK:
                    u32RegVal = struct.unpack('>L', sInMsg[2:])[0]
                    return (
                     ZedSerialEnum.OK, u32RegVal)
        return (
         iRet, 0)

    def ZedRegisterWrite(self, iRegAddr, sData, retry):
        sName = 'ZedRegisterWrite'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BL', ZedSerialEnum.TYPE_REG_WRITE_REQUEST, iRegAddr) + sData, sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                ret1 = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_RM_WRITE_RESPONSE, sName)
                return ret1
        else:
            self.logger.warning('Write Failed')
        return iRet

    def RunProgramInRAM(self, iRAMAddr):
        sName = 'RunProgramInRAM'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BL', ZedSerialEnum.TYPE_FP_RUN_REQUEST, iRAMAddr), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                iRet = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FP_RUN_RESPONSE, sName)
                if iRet == ZedSerialEnum.OK:
                    return (ZedSerialEnum.OK, sInMsg[2:])
        return (
         iRet, 0)

    def ZedCRAAuthenticationReq(self):
        sName = 'ZedCRAAuthenticationReq'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<B', ZedSerialEnum.TYPE_AUTHENTICATE_REQ), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                iRet = self.mCheckData(sInMsg, ZedSerialEnum.TYPE_AUTHENTICATE_CHALLENGE, sName)
                if iRet == ZedSerialEnum.OK:
                    au8Challenge = sInMsg[2:18]
                    return (
                     ZedSerialEnum.OK, au8Challenge)
        return (
         iRet, 0)

    def ZedCRASendChallengeResponse(self, au8Response):
        sName = 'ZedCRASendChallengeResponse'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('>B', ZedSerialEnum.TYPE_AUTHENTICATE_RESP) + au8Response, sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_AUTHENTICATE_RESP, sName)
        return iRet

    def ZedFlashSelectType(self, eFlashType, u32Address=None):
        sName = 'ZedFlashSelect'
        self.logger.debug(sName)
        if eFlashType < 0 or eFlashType > E_FL_CHIP_INTERNAL:
            return ZedSerialEnum.NOT_SUPPORTED
            if eFlashType == E_FL_CHIP_CUSTOM and u32Address is None:
                return ZedSerialEnum.NOT_SUPPORTED
        else:
            u32Address = 0
        iRet = self.mSendMsg(struct.pack('<BBL', ZedSerialEnum.TYPE_FL_SELECT_FLASH_REQUEST, eFlashType, u32Address), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_SELECT_FLASH_RESPONSE, sName)
        return iRet

    def ZedSelectBaudRate(self, iDivisor):
        sName = 'ZedSelectBaudRate'
        self.logger.debug(sName)
        iRet = self.mSendMsg(struct.pack('<BB', ZedSerialEnum.TYPE_FL_SET_BAUD_REQUEST, iDivisor), sName)
        if iRet == ZedSerialEnum.OK:
            try:
                iRet, sInMsg = self.mReceiveMsg(sName)
                if iRet == ZedSerialEnum.OK:
                    return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_FL_SET_BAUD_RESPONSE, sName)
            except AssertionError:
                return ZedSerialEnum.OK

        return iRet

    def ZedProgramIndexSector(self, bPageNumber, bWordNumber, bBytestoWrite):
        sName = 'ZedProgramIndexSector'
        self.logger.debug('%s: Page:%d,Word:%d. Data:0x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x' % (
         sName, bPageNumber, bWordNumber,
         bBytestoWrite[0], bBytestoWrite[1], bBytestoWrite[2], bBytestoWrite[3],
         bBytestoWrite[4], bBytestoWrite[5], bBytestoWrite[6], bBytestoWrite[7], bBytestoWrite[8],
         bBytestoWrite[9], bBytestoWrite[10], bBytestoWrite[11], bBytestoWrite[12], bBytestoWrite[13],
         bBytestoWrite[14], bBytestoWrite[15]))
        iRet = self.mSendMsg(struct.pack('<BBBBBBBBBBBBBBBBBBB', ZedSerialEnum.TYPE_PROGRAM_INDEX_SECTOR_REQUEST, bPageNumber, bWordNumber, bBytestoWrite[0], bBytestoWrite[1], bBytestoWrite[2], bBytestoWrite[3], bBytestoWrite[4], bBytestoWrite[5], bBytestoWrite[6], bBytestoWrite[7], bBytestoWrite[8], bBytestoWrite[9], bBytestoWrite[10], bBytestoWrite[11], bBytestoWrite[12], bBytestoWrite[13], bBytestoWrite[14], bBytestoWrite[15]), sName)
        if iRet == ZedSerialEnum.OK:
            iRet, sInMsg = self.mReceiveMsg(sName)
            if iRet == ZedSerialEnum.OK:
                return self.mCheckData(sInMsg, ZedSerialEnum.TYPE_PROGRAM_INDEX_SECTOR_RESPONSE, sName)
        return iRet

    def ZedLoginIn(self, aPassKey):
        sName = 'ZedLoginIn'
        self.logger.debug(sName)
        if self.iProcessorPartNo == 4 and self.iProcessorRevNo == 0:
            eReadResult, abMACAddress = self.ZedFlashRead(48, 8)
        else:
            if self.iProcessorPartNo == 4 and self.iProcessorRevNo == 1:
                eReadResult, abMACAddress = self.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
                if abMACAddress == struct.pack('LL', 0, 0):
                    bGetMacAddrFromFlash = True
                    eReadResult, abMACAddress = self.ZedFlashRead(48, 8)
                else:
                    bGetMacAddrFromFlash = False
                    eReadResult, abMACAddress = self.ZedRAMRead(JAGUAR_EFUSE_LOCATION, 8)
            else:
                eReadResult, abMACAddress = self.ZedRAMRead(268435552, 8)
        if eReadResult != ZedSerialEnum.OK:
            return LOGIN_FAILED_MAC_ADDRESS
        eReadResult, au8ChallengeEncrypted = self.ZedCRAAuthenticationReq()
        if eReadResult != ZedSerialEnum.OK:
            return LOGIN_FAILED_NO_RESPONSE
        u32Challenge = EncryptUtils.u32CRAChallenge(au8ChallengeEncrypted, aPassKey, abMACAddress)
        au8Response = EncryptUtils.au8CRAResponse(u32Challenge + 1, aPassKey, abMACAddress)
        status = self.ZedCRASendChallengeResponse(au8Response)
        if status != ZedSerialEnum.OK:
            return LOGIN_FAILED_PASSKEY_FAIL
        self.logger.info('abMACAddress = 0x%02X.%02X.%02X.%02X:%02X.%02X.%02X.%02X' % struct.unpack('<BBBBBBBB', self.abMacAddress))
        return LOGIN_OK


class cZedSerialApiRemote(cZedSerialApi):

    def __init__(self, iBaudrate, sComPort, sRemoteServer=''):
        aMode = [iBaudrate, 'N', 8, 1]
        print('Port = %s, sRemoteServer = %s' % (sComPort, sRemoteServer))
        self.oZsp = ZedSerialProtocol.cZedSerialProtocolRemote(sComPort, aMode, sRemoteServer)
        print('cZedSerialApiRemote - mCheckOpened() = %d' % self.mCheckOpened())
        print('cZedSerialApiRemote - self.oZsp.mCheckOpened() = %d' % self.oZsp.mCheckOpened())


def test(sComPort='COM2', iMaxOffset=92160):
    import struct, sys
    iErrCnt = 0
    iRAMBase = 4026531840
    iFlashBase = 0
    SerAPI = cZedSerialApi(38400, sComPort)
    tCommTimeouts = (
     sys.maxsize, 0, 5000, 0, 5000)
    SerAPI.oZsp.oHandle.mSetCommTimeouts(tCommTimeouts)
    SerAPI.oZsp.mSetDebug(0)
    SerAPI.oZsp.oHandle.mSetRTS(1)
    bReadFlashId = 0
    bGetCRAChallenge = 0
    bReadMAC = 0
    bWalkRAM = 0
    bEraseFlash = 0
    bDumpFlash = 1
    bDumpRam = 0
    bDumpMirrorRam = 0
    bSetBaudRate = 0
    bWalkFlash = 1
    if bReadFlashId:
        status, abId = SerAPI.ZedFlashReadId()
        print(status, abId)
        iManId, iDevId = tuple(struct.unpack('<BB', abId))
        print('0x%02X 0x%02X' % (iManId, iDevId))
        if iManId == 31 and iDevId == 96:
            print('Atmel AT25F512')
            SerAPI.ZedFlashSelectType(E_FL_CHIP_ATMEL_AT25F512)
        elif iManId == 16 and iDevId == 16:
            print('ST M25P10A')
            SerAPI.ZedFlashSelectType(E_FL_CHIP_ST_M25P10_A)
        elif iManId == 191 and iDevId == 73:
            print('SST 25VF010')
            SerAPI.ZedFlashSelectType(E_FL_CHIP_SST_25VF010)
    if bGetCRAChallenge:
        status, abChallenge = SerAPI.ZedCRAAuthenticationReq()
        print(len(abChallenge))
        lstChallenge = struct.unpack('<BBBBBBBBBBBBBBBB', abChallenge)
        sChallengeStr = ''
        for c in lstChallenge:
            sChallengeStr += '%02X' % c

        print('Challenge: ' + sChallengeStr)
    if bReadMAC:
        iRet, sData = SerAPI.ZedRAMRead(128, 8)
        MacAddr = struct.unpack('>LL', sData)
        print('0x%08X.%08X' % (MacAddr[0], MacAddr[1]))
    if bWalkRAM:
        print('Writing to memory range [0x%08X..0x%08X]' % (iRAMBase, iRAMBase + iMaxOffset - 1))
        for iOffset in range(0, iMaxOffset, 1):
            sys.stdout.write(hex(iOffset) + '\r')
            sData = struct.pack('<B', iOffset % 255)
            SerAPI.ZedRAMwrite(iRAMBase + iOffset, sData)

        lstErrors = []
        iErrCnt = 0
        print('Verifying memory range  [0x%08X..0x%08X]' % (iRAMBase, iRAMBase + iMaxOffset - 1))
        for iOffset in range(0, iMaxOffset, 1):
            iRet, sData = SerAPI.ZedRAMRead(iRAMBase + iOffset, 1)
            iVal = struct.unpack('<B', sData)[0]
            sys.stdout.write(hex(iOffset) + '\r')
            if iOffset % 255 != iVal:
                print('0x%02x' % iVal)
                sCurrErr = ''
                for i in range(5):
                    sCurrErr = sCurrErr + '0x%02X, ' % iVal
                    iRet, sData = SerAPI.ZedRAMRead(iRAMBase + iOffset, 1)
                    iVal = struct.unpack('<B', sData)[0]

                lstErrors.append('0x%08X: Expected 0x%02X, read [%s]' % (iRAMBase + iOffset, iOffset % 255, sCurrErr))
                iErrCnt += 1

        if iErrCnt:
            print('Detected %d mismatches' % iErrCnt)
            for sErr in lstErrors:
                print(sErr)

        else:
            print('OK               ')
    if bDumpRam:
        if bDumpMirrorRam:
            iRAMBase = 67108864
        for i in range(1):
            bytesPrLine = 4
            BytesToRead = iMaxOffset
            sPrintFmt = '[%08X]'
            for i in range(bytesPrLine):
                sPrintFmt += ' %02X'

            for iOffset in range(0, BytesToRead, bytesPrLine):
                iRet, sData = SerAPI.ZedRAMRead(iRAMBase + iOffset, bytesPrLine)
                sUnpackFmt = '<' + str(bytesPrLine) + 'B'
                ValLst = struct.unpack(sUnpackFmt, sData)
                printArgs = (iRAMBase + iOffset,) + ValLst
                print(sPrintFmt % printArgs)

    if bEraseFlash:
        print('Erasing flash')
        print(SerAPI.ZedFlashBulkErase())
        print('Sleeping')
        time.sleep(10.0)
    if bDumpFlash:
        for i in range(1):
            bytesPrLine = 16
            BytesToRead = iMaxOffset
            sPrintFmt = '[%08X]'
            for i in range(bytesPrLine):
                sPrintFmt += ' %02X'

            for iOffset in range(0, BytesToRead, bytesPrLine):
                iRet, sData = SerAPI.ZedFlashRead(iFlashBase + iOffset, bytesPrLine)
                sUnpackFmt = '<' + str(bytesPrLine) + 'B'
                ValLst = struct.unpack(sUnpackFmt, sData)
                printArgs = (iFlashBase + iOffset,) + ValLst
                print(sPrintFmt % printArgs)

    if bSetBaudRate:
        iDivisor = int(1000000 / 38400)
        print(hex(SerAPI.ZedSelectBaudRate(iDivisor)))
    if bWalkFlash:
        print('Erasing flash')
        print(SerAPI.ZedFlashBulkErase())
        iRet, bSR = SerAPI.ZedFlashReadSR()
        print(iRet, bSR)
        iSR = struct.unpack('B', bSR)[0]
        print(iSR)
        if iSR & 1:
            print('sleeping')
            time.sleep(1.0)
        print('Verifying flash erasure')
        bytesPrLine = 128
        sUnpackFmt = '<' + str(bytesPrLine) + 'B'
        sPrintFmt = '[%08X]'
        for i in range(bytesPrLine):
            sPrintFmt += ' %02X'

        for iOffset in range(0, iMaxOffset, bytesPrLine):
            sys.stdout.write('%d    \r' % iOffset)
            iRet, sData = SerAPI.ZedFlashRead(iOffset, bytesPrLine)
            ValLst = struct.unpack(sUnpackFmt, sData)
            for i in range(len(ValLst)):
                if ValLst[i] != 255:
                    printArgs = (
                     iFlashBase + iOffset,) + ValLst
                    print("Flash wasn't properly erased")
                    print(sPrintFmt % printArgs)
                    break
                elif i == len(ValLst) - 1:
                    print('[%08X] OK' % (iFlashBase + iOffset))

        print('Writing pattern to flash')
        sPattern = ''
        for i in range(bytesPrLine):
            sPattern = sPattern + chr(i)

        print('Pattern')
        print(sPrintFmt % ((0, ) + struct.unpack(sUnpackFmt, sPattern)))
        for iOffset in range(0, iMaxOffset, bytesPrLine):
            sys.stdout.write('%d    \r' % iOffset)
            iRet = SerAPI.ZedFlashProg(iOffset, sPattern)
            if iRet != 0:
                print('Error writing to flash @ 0x%08X (%d): iRet = 0x%02X (%d)' % (iOffset, iOffset, iRet, iRet))

        print('Verifying flash write')
        for iOffset in range(0, iMaxOffset, bytesPrLine):
            sys.stdout.write('%d    \r' % iOffset)
            iRet, sData = SerAPI.ZedFlashRead(iOffset, bytesPrLine)
            if sData != sPattern:
                ValLst = struct.unpack(sUnpackFmt, sData)
                printArgs = (iOffset,) + ValLst
                print('Verification error')
                print(sPrintFmt % printArgs)


if __name__ == '__main__':
    test('COM12', 1000)