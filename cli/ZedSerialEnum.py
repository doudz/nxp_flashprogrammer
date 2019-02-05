# uncompyle6 version 3.2.5
# Python bytecode 2.6 (62161)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: ZedSerialEnum.pyo
# Compiled at: 2013-01-18 15:13:56
TYPE_ACKNOWLEDGE = 0
TYPE_READ_REQUEST = 1
TYPE_READ_RESPONSE = 2
TYPE_WRITE_REQUEST = 3
TYPE_WRITE_RESPONSE = 4
TYPE_SET_CS_REQUEST = 5
TYPE_SET_CS_RESPONSE = 6
TYPE_FL_ERASE_REQUEST = 7
TYPE_FL_ERASE_RESPONSE = 8
TYPE_FL_PROG_REQUEST = 9
TYPE_FL_PROG_RESPONSE = 10
TYPE_FL_READ_REQUEST = 11
TYPE_FL_READ_RESPONSE = 12
TYPE_FL_SECTOR_ERASE_REQUEST = 13
TYPE_FL_SECTOR_ERASE_RESPONSE = 14
TYPE_FL_WRITE_SR_REQUEST = 15
TYPE_FL_WRITE_SR_RESPONSE = 16
TYPE_SET_RESET_REQUEST = 20
TYPE_SET_RESET_RESPONSE = 21
TYPE_SET_RATE_REQUEST = 22
TYPE_SET_RATE_RESPONSE = 23
TYPE_PACKET_TEST_REQUEST = 24
TYPE_PACKET_TEST_RESPONSE = 25
TYPE_TRIG_PKT_TEST_REQUEST = 26
TYPE_TRIG_PKT_TEST_RESPONSE = 27
TYPE_TRIG_PKT_TEST_DATA = 28
TYPE_RM_WRITE_REQUEST = 29
TYPE_RM_WRITE_RESPONSE = 30
TYPE_RM_READ_REQUEST = 31
TYPE_RM_READ_RESPONSE = 32
TYPE_FP_RUN_REQUEST = 33
TYPE_FP_RUN_RESPONSE = 34
TYPE_FL_READ_SR_REQUEST = 35
TYPE_FL_READ_SR_RESPONSE = 36
TYPE_FL_READ_ID_REQUEST = 37
TYPE_FL_READ_ID_RESPONSE = 38
TYPE_FL_SET_BAUD_REQUEST = 39
TYPE_FL_SET_BAUD_RESPONSE = 40
TYPE_AUTHENTICATE_REQ = 41
TYPE_AUTHENTICATE_CHALLENGE = 42
TYPE_AUTHENTICATE_RESP = 43
TYPE_FL_SELECT_FLASH_REQUEST = 44
TYPE_FL_SELECT_FLASH_RESPONSE = 45
TYPE_REG_READ_REQUEST = 46
TYPE_REG_READ_RESPONSE = 47
TYPE_REG_WRITE_REQUEST = 48
TYPE_REG_WRITE_RESPONSE = 49
TYPE_GET_CHIP_ID_REQUEST = 50
TYPE_GET_CHIP_ID_RESPONSE = 51
TYPE_GET_FUSE_SECURED_REQUEST = 52
TYPE_GET_FUSE_SECURED_RESPONSE = 53
TYPE_PDM_ERASE_REQUEST = 54
TYPE_PDM_ERASE_RESPONSE = 55
TYPE_PROGRAM_INDEX_SECTOR_REQUEST = 56
TYPE_PROGRAM_INDEX_SECTOR_RESPONSE = 57
TYPE_TST_SRV_REQUEST = 100
TYPE_TST_SRV_RESPONSE = 101
TYPE_TST_SRV_POLL = 102
TYPE_TST_SRV_POLL_RESPONSE = 103
OK = 0
NOT_SUPPORTED = 255
WRITE_FAIL = 254
INVALID_RESPONSE = 253
CRC_ERROR = 252
ASSERT_FAIL = 251
USER_INTERRUPT = 250
READ_FAIL = 249
TST_ERR = 248
AUTH_ERROR = 247
NO_RESPONSE = 246
FUSE_NOT_SECURED = 0
FUSE_SECURED_NOT_LOGGEDIN = -1
FUSE_SECURED_LOGGEDIN = -2

def StatusStr(u8Status):
    if u8Status == OK:
        return 'OK'
    if u8Status == NOT_SUPPORTED:
        return 'NOT_SUPPORTED'
    if u8Status == WRITE_FAIL:
        return 'WRITE_FAIL'
    if u8Status == INVALID_RESPONSE:
        return 'INVALID_RESPONSE'
    if u8Status == CRC_ERROR:
        return 'CRC_ERROR'
    if u8Status == ASSERT_FAIL:
        return 'ASSERT_FAIL'
    if u8Status == USER_INTERRUPT:
        return 'USER_INTERRUPT'
    if u8Status == READ_FAIL:
        return 'READ_FAIL'
    if u8Status == TST_ERR:
        return 'TST_ERR'
    if u8Status == AUTH_ERROR:
        return 'AUTH_ERROR'
    if u8Status == NO_RESPONSE:
        return 'NO_RESPONSE'


def SerProtCodeStr(u8SerProtCode):
    if u8SerProtCode == TYPE_ACKNOWLEDGE:
        return 'Ack'
    if u8SerProtCode == TYPE_READ_REQUEST:
        return 'RdReq'
    if u8SerProtCode == TYPE_READ_RESPONSE:
        return 'RdRsp'
    if u8SerProtCode == TYPE_WRITE_REQUEST:
        return 'WrReq'
    if u8SerProtCode == TYPE_WRITE_RESPONSE:
        return 'WrRsp'
    if u8SerProtCode == TYPE_SET_CS_REQUEST:
        return 'SetCSReq'
    if u8SerProtCode == TYPE_SET_CS_RESPONSE:
        return 'SetCSRsp'
    if u8SerProtCode == TYPE_FL_ERASE_REQUEST:
        return 'FlEraseReq'
    if u8SerProtCode == TYPE_FL_ERASE_RESPONSE:
        return 'FlEraseRsp'
    if u8SerProtCode == TYPE_FL_PROG_REQUEST:
        return 'FlPrgReq'
    if u8SerProtCode == TYPE_FL_PROG_RESPONSE:
        return 'FlPrgRsp'
    if u8SerProtCode == TYPE_FL_READ_REQUEST:
        return 'FlReadReq'
    if u8SerProtCode == TYPE_FL_READ_RESPONSE:
        return 'FlReadRsp'
    if u8SerProtCode == TYPE_FL_SECTOR_ERASE_REQUEST:
        return 'FlSectEraseReq'
    if u8SerProtCode == TYPE_FL_SECTOR_ERASE_RESPONSE:
        return 'FlSectEraseRsp'
    if u8SerProtCode == TYPE_FL_WRITE_SR_REQUEST:
        return 'FlWrSRReq'
    if u8SerProtCode == TYPE_FL_WRITE_SR_RESPONSE:
        return 'FlWrSRRsp'
    if u8SerProtCode == TYPE_SET_RESET_REQUEST:
        return 'SetRstReq'
    if u8SerProtCode == TYPE_SET_RESET_RESPONSE:
        return 'SetRstRsp'
    if u8SerProtCode == TYPE_SET_RATE_REQUEST:
        return 'SetRateReq'
    if u8SerProtCode == TYPE_SET_RATE_RESPONSE:
        return 'SetRateRsp'
    if u8SerProtCode == TYPE_PACKET_TEST_REQUEST:
        return 'PackTstReq'
    if u8SerProtCode == TYPE_PACKET_TEST_RESPONSE:
        return 'PackTstRsp'
    if u8SerProtCode == TYPE_TRIG_PKT_TEST_REQUEST:
        return 'TrgPackTstReq'
    if u8SerProtCode == TYPE_TRIG_PKT_TEST_RESPONSE:
        return 'TrgPackTstRsp'
    if u8SerProtCode == TYPE_TRIG_PKT_TEST_DATA:
        return 'TrgPackTstData'
    if u8SerProtCode == TYPE_RM_WRITE_REQUEST:
        return 'RmWrReq'
    if u8SerProtCode == TYPE_RM_WRITE_RESPONSE:
        return 'RmWrRsp'
    if u8SerProtCode == TYPE_RM_READ_REQUEST:
        return 'RmRdReq'
    if u8SerProtCode == TYPE_RM_READ_RESPONSE:
        return 'RmRdRsp'
    if u8SerProtCode == TYPE_FP_RUN_REQUEST:
        return 'RunReq'
    if u8SerProtCode == TYPE_FP_RUN_RESPONSE:
        return 'RunRsp'
    if u8SerProtCode == TYPE_FL_READ_SR_REQUEST:
        return 'RdSRReq'
    if u8SerProtCode == TYPE_FL_READ_SR_RESPONSE:
        return 'RdSRRsp'
    if u8SerProtCode == TYPE_FL_READ_ID_REQUEST:
        return 'RdIdReq'
    if u8SerProtCode == TYPE_FL_READ_ID_RESPONSE:
        return 'RdIdRsp'
    if u8SerProtCode == TYPE_FL_SET_BAUD_REQUEST:
        return 'SetBaudReq'
    if u8SerProtCode == TYPE_FL_SET_BAUD_RESPONSE:
        return 'SetBaudRsp'
    if u8SerProtCode == TYPE_AUTHENTICATE_REQ:
        return 'AuthReq'
    if u8SerProtCode == TYPE_AUTHENTICATE_CHALLENGE:
        return 'AuthChal'
    if u8SerProtCode == TYPE_AUTHENTICATE_RESP:
        return 'AuthRsp'
    if u8SerProtCode == TYPE_FL_SELECT_FLASH_TYPE_REQUEST:
        return 'SelFlTypReq'
    if u8SerProtCode == TYPE_FL_SELECT_FLASH_TYPE_RESPONSE:
        return 'SelFlTypRsp'
    if u8SerProtCode == TYPE_TST_SRV_REQUEST:
        return 'TstSrvReq'
    if u8SerProtCode == TYPE_TST_SRV_RESPONSE:
        return 'TstSrvReq'
    if u8SerProtCode == TYPE_TST_SRV_POLL:
        return 'TstSrvPollReq'
    if u8SerProtCode == TYPE_TST_SRV_POLL_RESPONSE:
        return 'TstSrvPollRsp'