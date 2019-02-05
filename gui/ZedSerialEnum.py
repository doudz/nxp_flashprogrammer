# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: ZedSerialEnum.pyo
# Compiled at: 2012-11-15 17:10:47
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
    else:
        if u8Status == NOT_SUPPORTED:
            return 'NOT_SUPPORTED'
        else:
            if u8Status == WRITE_FAIL:
                return 'WRITE_FAIL'
            else:
                if u8Status == INVALID_RESPONSE:
                    return 'INVALID_RESPONSE'
                else:
                    if u8Status == CRC_ERROR:
                        return 'CRC_ERROR'
                    else:
                        if u8Status == ASSERT_FAIL:
                            return 'ASSERT_FAIL'
                        else:
                            if u8Status == USER_INTERRUPT:
                                return 'USER_INTERRUPT'
                            else:
                                if u8Status == READ_FAIL:
                                    return 'READ_FAIL'
                                else:
                                    if u8Status == TST_ERR:
                                        return 'TST_ERR'
                                    else:
                                        if u8Status == AUTH_ERROR:
                                            return 'AUTH_ERROR'
                                        else:
                                            if u8Status == NO_RESPONSE:
                                                return 'NO_RESPONSE'


def SerProtCodeStr(u8SerProtCode):
    if u8SerProtCode == TYPE_ACKNOWLEDGE:
        return 'Ack'
    else:
        if u8SerProtCode == TYPE_READ_REQUEST:
            return 'RdReq'
        else:
            if u8SerProtCode == TYPE_READ_RESPONSE:
                return 'RdRsp'
            else:
                if u8SerProtCode == TYPE_WRITE_REQUEST:
                    return 'WrReq'
                else:
                    if u8SerProtCode == TYPE_WRITE_RESPONSE:
                        return 'WrRsp'
                    else:
                        if u8SerProtCode == TYPE_SET_CS_REQUEST:
                            return 'SetCSReq'
                        else:
                            if u8SerProtCode == TYPE_SET_CS_RESPONSE:
                                return 'SetCSRsp'
                            else:
                                if u8SerProtCode == TYPE_FL_ERASE_REQUEST:
                                    return 'FlEraseReq'
                                else:
                                    if u8SerProtCode == TYPE_FL_ERASE_RESPONSE:
                                        return 'FlEraseRsp'
                                    else:
                                        if u8SerProtCode == TYPE_FL_PROG_REQUEST:
                                            return 'FlPrgReq'
                                        else:
                                            if u8SerProtCode == TYPE_FL_PROG_RESPONSE:
                                                return 'FlPrgRsp'
                                            else:
                                                if u8SerProtCode == TYPE_FL_READ_REQUEST:
                                                    return 'FlReadReq'
                                                else:
                                                    if u8SerProtCode == TYPE_FL_READ_RESPONSE:
                                                        return 'FlReadRsp'
                                                    else:
                                                        if u8SerProtCode == TYPE_FL_SECTOR_ERASE_REQUEST:
                                                            return 'FlSectEraseReq'
                                                        else:
                                                            if u8SerProtCode == TYPE_FL_SECTOR_ERASE_RESPONSE:
                                                                return 'FlSectEraseRsp'
                                                            else:
                                                                if u8SerProtCode == TYPE_FL_WRITE_SR_REQUEST:
                                                                    return 'FlWrSRReq'
                                                                else:
                                                                    if u8SerProtCode == TYPE_FL_WRITE_SR_RESPONSE:
                                                                        return 'FlWrSRRsp'
                                                                    else:
                                                                        if u8SerProtCode == TYPE_SET_RESET_REQUEST:
                                                                            return 'SetRstReq'
                                                                        else:
                                                                            if u8SerProtCode == TYPE_SET_RESET_RESPONSE:
                                                                                return 'SetRstRsp'
                                                                            else:
                                                                                if u8SerProtCode == TYPE_SET_RATE_REQUEST:
                                                                                    return 'SetRateReq'
                                                                                else:
                                                                                    if u8SerProtCode == TYPE_SET_RATE_RESPONSE:
                                                                                        return 'SetRateRsp'
                                                                                    else:
                                                                                        if u8SerProtCode == TYPE_PACKET_TEST_REQUEST:
                                                                                            return 'PackTstReq'
                                                                                        else:
                                                                                            if u8SerProtCode == TYPE_PACKET_TEST_RESPONSE:
                                                                                                return 'PackTstRsp'
                                                                                            else:
                                                                                                if u8SerProtCode == TYPE_TRIG_PKT_TEST_REQUEST:
                                                                                                    return 'TrgPackTstReq'
                                                                                                else:
                                                                                                    if u8SerProtCode == TYPE_TRIG_PKT_TEST_RESPONSE:
                                                                                                        return 'TrgPackTstRsp'
                                                                                                    else:
                                                                                                        if u8SerProtCode == TYPE_TRIG_PKT_TEST_DATA:
                                                                                                            return 'TrgPackTstData'
                                                                                                        else:
                                                                                                            if u8SerProtCode == TYPE_RM_WRITE_REQUEST:
                                                                                                                return 'RmWrReq'
                                                                                                            else:
                                                                                                                if u8SerProtCode == TYPE_RM_WRITE_RESPONSE:
                                                                                                                    return 'RmWrRsp'
                                                                                                                else:
                                                                                                                    if u8SerProtCode == TYPE_RM_READ_REQUEST:
                                                                                                                        return 'RmRdReq'
                                                                                                                    else:
                                                                                                                        if u8SerProtCode == TYPE_RM_READ_RESPONSE:
                                                                                                                            return 'RmRdRsp'
                                                                                                                        else:
                                                                                                                            if u8SerProtCode == TYPE_FP_RUN_REQUEST:
                                                                                                                                return 'RunReq'
                                                                                                                            else:
                                                                                                                                if u8SerProtCode == TYPE_FP_RUN_RESPONSE:
                                                                                                                                    return 'RunRsp'
                                                                                                                                else:
                                                                                                                                    if u8SerProtCode == TYPE_FL_READ_SR_REQUEST:
                                                                                                                                        return 'RdSRReq'
                                                                                                                                    else:
                                                                                                                                        if u8SerProtCode == TYPE_FL_READ_SR_RESPONSE:
                                                                                                                                            return 'RdSRRsp'
                                                                                                                                        else:
                                                                                                                                            if u8SerProtCode == TYPE_FL_READ_ID_REQUEST:
                                                                                                                                                return 'RdIdReq'
                                                                                                                                            else:
                                                                                                                                                if u8SerProtCode == TYPE_FL_READ_ID_RESPONSE:
                                                                                                                                                    return 'RdIdRsp'
                                                                                                                                                else:
                                                                                                                                                    if u8SerProtCode == TYPE_FL_SET_BAUD_REQUEST:
                                                                                                                                                        return 'SetBaudReq'
                                                                                                                                                    else:
                                                                                                                                                        if u8SerProtCode == TYPE_FL_SET_BAUD_RESPONSE:
                                                                                                                                                            return 'SetBaudRsp'
                                                                                                                                                        else:
                                                                                                                                                            if u8SerProtCode == TYPE_AUTHENTICATE_REQ:
                                                                                                                                                                return 'AuthReq'
                                                                                                                                                            else:
                                                                                                                                                                if u8SerProtCode == TYPE_AUTHENTICATE_CHALLENGE:
                                                                                                                                                                    return 'AuthChal'
                                                                                                                                                                else:
                                                                                                                                                                    if u8SerProtCode == TYPE_AUTHENTICATE_RESP:
                                                                                                                                                                        return 'AuthRsp'
                                                                                                                                                                    else:
                                                                                                                                                                        if u8SerProtCode == TYPE_FL_SELECT_FLASH_TYPE_REQUEST:
                                                                                                                                                                            return 'SelFlTypReq'
                                                                                                                                                                        else:
                                                                                                                                                                            if u8SerProtCode == TYPE_FL_SELECT_FLASH_TYPE_RESPONSE:
                                                                                                                                                                                return 'SelFlTypRsp'
                                                                                                                                                                            else:
                                                                                                                                                                                if u8SerProtCode == TYPE_TST_SRV_REQUEST:
                                                                                                                                                                                    return 'TstSrvReq'
                                                                                                                                                                                else:
                                                                                                                                                                                    if u8SerProtCode == TYPE_TST_SRV_RESPONSE:
                                                                                                                                                                                        return 'TstSrvReq'
                                                                                                                                                                                    else:
                                                                                                                                                                                        if u8SerProtCode == TYPE_TST_SRV_POLL:
                                                                                                                                                                                            return 'TstSrvPollReq'
                                                                                                                                                                                        else:
                                                                                                                                                                                            if u8SerProtCode == TYPE_TST_SRV_POLL_RESPONSE:
                                                                                                                                                                                                return 'TstSrvPollRsp'