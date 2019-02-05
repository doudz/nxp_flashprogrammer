# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: FlashProgrammer.pyo
# Compiled at: 2013-01-30 12:38:01
import os, sys, time, warnings
# import d2xx
import wx.adv
warnings.filterwarnings('ignore', '.*The wxPython compatibility package is no longer*')
try:
    sys.path.append('..\\..\\CommonFiles\\Trunk\\python\\flash')
    from FlashUtils import *
except ImportError:
    print('Could not find FlashUtils.py, please update PYTHONPATH to include the path to FlashUtils.py')
    sys.exit(1)
else:
    try:
        sys.path.append('..\\..\\CommonFiles\\Trunk\\python\\AES')
        from EncryptUtils import *
    except ImportError:
        print('Could not find EncryptUtils.py, please update PYTHONPATH to include the path to FlashUtils.py')
        sys.exit(1)

    try:
        sys.path.append('..\\..\\CommonFiles\\Trunk\\python\\licence')
        import LicenceManager
    except ImportError:
        print('Could not find LicenceManager.py, please update PYTHONPATH to include the path to LicenceManager.py')
        sys.exit(1)

    from stat import *
    from optparse import OptionParser
    import pickle, wx, wx.adv, wx.lib.filebrowsebutton as filebrowse
#     from wxPython.wx import wxInitAllImageHandlers
    from wx.lib.expando import ExpandoTextCtrl, EVT_ETC_LAYOUT_NEEDED
    import ZedSerialApi, ZedSerialEnum, ComPortDlg, ComPortList, About, PrintData, Version, FlexValidator, Settings, binascii, tempfile, traceback, EncryptUtils
    SECTOR3_ERASE = 0
    SECTOR3_PRESERVE = 1
    SECTOR3_RESTORE = 2
    PRESERVE_SECTOR_NUM = 3
    SECTOR_LEN = 32768
    DefaultBaudRate = 38400
    USE_INTERNAL_FLASH = 0
    USE_EXTERNAL_FLASH = 1
    JN516x_BOOTLOADER_ENTRY = 102
    bTestMacInEFuse = 0

    class cNowhere():

        def write(self, s):
            pass


    JN51XX_REG_ID = 268435708
    JN51XX_ROM_ID_ADDR = 4
    MAC_AND_LICENSE_HEADER_SIZE = 32
    E_TARGET_INTERFACE_FLASH = 0
    E_TARGET_INTERFACE_RAM = 1
    S_EXT_FILE_TITLE = 'FlashProgrammerExtension_JN5168.bin'
    MAC_INDEX_SECTOR_PAGE = 5
    MAC_INDEX_SECTOR_WORD = 7

    class cProgrammingConfiguration():

        def __init__(self):
            self.DeviceInfo = None
            self.sCustomFlashProgrammerFile = ''
            self.Reset()
            return

        def Reset(self):
            self.eTargetInterface = E_TARGET_INTERFACE_FLASH
            self.eFlashChip = ZedSerialApi.E_FL_CHIP_ST_M25P10_A
            self.boCustomProgrammer = 0
            self.u32FlashFuncTableAddr = 0


    class EEPROMDialog(wx.Dialog):

        def __init__(self, parent, ident, title):
            wx.Dialog.__init__(self, parent, ident, 'Erase EEPROM', size=(250, 200), style=wx.DEFAULT_DIALOG_STYLE)
            self.parent = parent
            sizer = self.CreateTextSizer('\n\n  Erase Complete EEPROM or PDM only\n')
            oPDMButton = wx.Button(self, -1, 'PDM only')
            oAllButton = wx.Button(self, -1, 'Complete EEPROM')
            sizer.Add(oPDMButton, 0, wx.ALL | wx.EXPAND, 5)
            sizer.Add(oAllButton, 0, wx.ALL | wx.EXPAND, 5)
            self.SetSizer(sizer)
            self.Bind(wx.EVT_BUTTON, self.mOnReadPDMButton, oPDMButton)
            self.Bind(wx.EVT_BUTTON, self.mOnReadAllButton, oAllButton)

        def mOnReadPDMButton(self, evt):
            print('\nDo PDM')
            self.EraseEEPROM(0)
            self.Destroy()

        def mOnReadAllButton(self, evt):
            print('\nDo ALL')
            self.EraseEEPROM(1)
            self.Destroy()

        def EraseEEPROM(self, bForceAll):
            eRAMHeaderDataProcessing = teHeaderProcessing.OVERWRITE
            abRAMNewHeaderData = None
            sFile = S_EXT_FILE_TITLE
            sTitle = 'Erasing EEPROM'
            bSuccess = self.parent.bProgramFileIntoRAMAndRun(eRAMHeaderDataProcessing, abRAMNewHeaderData, sFile, sTitle)
            if bSuccess == True:
                print('program to ram successfull')
                print('erase eeprom')
                if self.parent.oZsa is not None:
                    if self.parent.oZsa.mCheckOpened() == ZedSerialEnum.OK:
                        self.parent.oZsa.mSetRxTimeOut(10000)
                        if self.parent.oZsa.ZedPDMErase(bForceAll) == ZedSerialEnum.OK:
                            print('PDM Erased')
                            iRet, sSerRet = self.parent.oZsa.RunProgramInRAM(JN516x_BOOTLOADER_ENTRY)
                            iRet != ZedSerialEnum.OK and wx.MessageBox('Error runnning program in RAM\n\nPlease check cabling and power', self.parent.ProgrammingConfiguration.sCustomFlashProgrammerFile, wx.ICON_INFORMATION)
                        else:
                            wx.MessageBox('EEPROM Erased', 'Success', wx.OK | wx.ICON_INFORMATION)
                    else:
                        print('PDM Erase Failed')
                        self.parent.oZsa.mSetRxTimeOut(ZedSerialApi.DEFAULT_READ_TIMEOUT)
                else:
                    raise UserWarning('Serial port not open', None)
            else:
                print('failed to program to ram')
            return


    sFwWildcard = 'JN51xx binary file (*.bin)|*.bin|All files (*.*)|*.*'
    sSector3Wildcard = 'JN51xx sector3 binary file (*.s3)|*.s3|All files (*.*)|*.*'
    sLicenceWildcard = 'JN51xx MAC address list file (*.txt)|*.txt|All files (*.*)|*.*'

    def ParseMacAddress(sMACAddress):
        sMACAddress = sMACAddress.strip(':')
        MacList = sMACAddress.split(':')
        if len(MacList) != 8:
            return
        abMacAddress = ''
        for i in range(8):
            AddrByte = int('0x' + MacList[i], 16)
            if AddrByte < 0 or AddrByte > 255:
                print('Invalid MAC address - please check part %d of the address string (%s)' % (i, MacList[i]))
                return
            abMacAddress = abMacAddress + binascii.a2b_hex(MacList[i])

        return abMacAddress


    class FlashProgrammerFrame(wx.Dialog):

        def __init__(self, parent, sTitle, sVersion, sComPort=None):
            self.sVersion = sVersion
            self.iBaudRate = 38400
            self.iDivisor = 26
            try:
                self.bInternalBuild = Settings.bInternalBuild
                self.iUse2Stage = Settings.iUse2Stage
                self.bUse16AddrCheckBox = Settings.bUse16AddrCheckBox
                self.bAllowEncryption = Settings.bAllowEncryption
                self.bAllowMACprogamming = Settings.bAllowMACprogamming
            except:
                self.bInternalBuild = False
                self.iUse2Stage = False
                self.bUse16AddrCheckBox = False
                self.bAllowEncryption = False
                self.bAllowMACprogamming = False
            else:
                if self.bInternalBuild:
                    dlgSize = (740, 740)
                else:
                    dlgSize = (740, 640)
                wx.Dialog.__init__(self, parent, -1, sTitle + ' ' + self.sVersion, pos=(150,
                                                                                        150), style=wx.DEFAULT_DIALOG_STYLE | wx.MINIMIZE_BOX, size=dlgSize)
                self.ComPortList = ComPortList.fGetComPortList()
                self.oZsa = None
                self.bAutoIncr = False
                self.DeviceInfo = cDeviceInfo()
                self.ProgrammingConfiguration = cProgrammingConfiguration()
                self.ProgrammingConfiguration.DeviceInfo = self.DeviceInfo
                try:
                    oCfgFile = open('config.txt', 'rb')
                    oUnpickler = pickle.Unpickler(oCfgFile)
                    self.aLHistory = oUnpickler.load()
                    self.aHistory = oUnpickler.load()
                    if sComPort is not None:
                        self.sComPort = sComPort
                        sIgnore = oUnpickler.load()
                    else:
                        self.sComPort = oUnpickler.load()
                    self.iSector3Programming = oUnpickler.load()
                    self.iBaudRateChoice = oUnpickler.load()
                    self.bDebug = oUnpickler.load()
                    self.aCHistory = oUnpickler.load()
                    self.bSkipVerification = oUnpickler.load()
                    self.bGenerateResetAndProgram = oUnpickler.load()
                    self.aS3History = oUnpickler.load()
                    self.sPassKey = oUnpickler.load()
                    
                    oCfgFile.close()
                except Exception as e:
                    print(e)
                    print('Error reading config file, using defaults')
                    self.aHistory = []
                    self.aLHistory = []
                    if sComPort is not None:
                        self.sComPort = sComPort
                    else:
                        self.sComPort = self.ComPortList[0]
                    self.iSector3Programming = 0
                    self.iBaudRateChoice = 0
                    self.bDebug = False
                    self.sFlashFile = ''
                    self.sLicenceFile = ''
                    self.aCHistory = []
                    self.bSkipVerification = False
                    self.bGenerateResetAndProgram = True
                    self.aS3History = []
                    self.sSector3File = ''
                    self.sPassKey = '0x00000000, 0x00000000, 0x00000000, 0x80000000'
                else:
#                 if True:
                    self.sDefaultKey = self.sPassKey
                    self.abEncryptKey = struct.pack('>LLLL', 0, 0, 0, 0)
                    self.abMACAddress = None
                    self.mSetPassKey()
                    self.FlashUtilIF = cFlashUtilIF(1, self.DeviceInfo)
                    if len(self.aHistory) > 0:
                        self.sFlashFile = self.aHistory[0]
                    else:
                        self.sFlashFile = ''
                    if len(self.aLHistory) > 0:
                        self.sLicenceFile = self.aLHistory[0]
                    else:
                        self.sLicenceFile = ''
                    if len(self.aCHistory) > 0:
                        self.ProgrammingConfiguration.sCustomFlashProgrammerFile = self.aCHistory[0]
                    else:
                        self.ProgrammingConfiguration.sCustomFlashProgrammerFile = '??'
                    if len(self.aS3History) > 0:
                        self.sSector3File = self.aS3History[0]
                    else:
                        self.sSector3FlashFile = ''
                    self.iUseRead = Settings.iUseRead
                    self.iExtras = Settings.iExtras
                    self.bRTSAsserted = 1
                    self.Bind(wx.EVT_CLOSE, self.mEvtClose)
                    self.panel = wx.Panel(self)
                    self.oFBBHFirmware = filebrowse.FileBrowseButtonWithHistory(self.panel, -1, fileMask=sFwWildcard, size=(565,
                                                                                                                            3), changeCallback=self.mOnFbbhCallback)
                    self.oFBBHFirmware.SetLabel('Program:')
                    oClrHistBtn = wx.Button(self.panel, -1, 'Clear History', size=(80,
                                                                                   24))
                    self.Bind(wx.EVT_BUTTON, self.mOnClearHistory, oClrHistBtn)
                    self.oCfgBox = wx.StaticBox(self.panel, -1, label='Configuration')
                    oCfgSizer = wx.StaticBoxSizer(self.oCfgBox, wx.VERTICAL)
                    oCfgSizerRowP = wx.BoxSizer(wx.HORIZONTAL)
                    oCfgSizerRow1 = wx.BoxSizer(wx.HORIZONTAL)
                    oCfgSizerRow2 = wx.BoxSizer(wx.HORIZONTAL)
                    oCfgSizerRow3 = wx.BoxSizer(wx.VERTICAL)
                    oCfgSizerRow4 = wx.BoxSizer(wx.HORIZONTAL)
                    oCfgSizerRow5 = wx.BoxSizer(wx.VERTICAL)
                    oCfgSizerRow6 = wx.BoxSizer(wx.HORIZONTAL)
                    self.oFTDIBox = wx.StaticBox(self.panel, -1, label='Carrier Board or USB Dongle')
                    oFTDISizer = wx.StaticBoxSizer(self.oFTDIBox, wx.VERTICAL)
                    oFTDISizerRow1 = wx.BoxSizer(wx.HORIZONTAL)
                    oFTDISizerRow2 = wx.BoxSizer(wx.HORIZONTAL)
                    self.ComportLabel = wx.StaticText(self.panel, -1, 'COM Port:', size=(50,
                                                                                         25))
                    self.oCOMPortChoice = wx.Choice(self.panel, -1, size=(95, 25), choices=self.ComPortList)
                    self.Bind(wx.EVT_CHOICE, self.mOnSelectComPort, self.oCOMPortChoice)
                    self.oZsa = ZedSerialApi.cZedSerialApi(DefaultBaudRate, self.sComPort)
                    if self.oZsa.mCheckOpened() == ZedSerialEnum.OK:
                        self.oZsa.oZsp.mSetDebug(bool(self.bDebug))
                        self.oCOMPortChoice.Select(self.ComPortList.index(self.sComPort))
                    self.oConnectCOMPortCheckBox = wx.CheckBox(self.panel, -1, 'Connect: ', style=wx.ALIGN_RIGHT)
                    self.oConnectCOMPortCheckBox.SetValue(True)
                    self.Bind(wx.EVT_CHECKBOX, self.mOnConnectCOMPort, self.oConnectCOMPortCheckBox)
                    oSkipVerificationCheckBox = wx.CheckBox(self.panel, -1, 'Skip Verification:', style=wx.ALIGN_RIGHT)
                    oSkipVerificationCheckBox.SetValue(self.bSkipVerification)
                    self.Bind(wx.EVT_CHECKBOX, self.OnSelectSkipVerification, oSkipVerificationCheckBox)
                    oToggleRPCheckBox = wx.CheckBox(self.panel, -1, 'Automatic Program and Reset', style=wx.ALIGN_RIGHT)
                    oToggleRPCheckBox.SetValue(self.bGenerateResetAndProgram)
                    self.Bind(wx.EVT_CHECKBOX, self.GenerateResetAndProgram, oToggleRPCheckBox)
                    oCOMRefeshBtn = wx.Button(self.panel, -1, 'Refresh', size=(80,
                                                                               24))
                    self.Bind(wx.EVT_BUTTON, self.mCOMPortRefresh, oCOMRefeshBtn)
                    self.oGenRSTBtn = wx.Button(self.panel, -1, 'RESET Dongle', size=(120,
                                                                                      30))
                    self.Bind(wx.EVT_BUTTON, self.mResetTarget, self.oGenRSTBtn)
                    self.TargetLabel = wx.StaticText(self.panel, -1, 'Target:', size=(50,
                                                                                      25))
                    self.TargetChoice = wx.Choice(self.panel, -1, size=(95, 25), choices=['Detect Flash', 'RAM Only', 'Custom Flash'])
                    self.Bind(wx.EVT_CHOICE, self.OnSelectTargetChoice, self.TargetChoice)
                    self.TargetChoice.Select(0)
                    self.oCustomFlashProgrammer = filebrowse.FileBrowseButtonWithHistory(self.panel, -1, fileMask=sFwWildcard, labelText='', dialogTitle='Choose 2nd stage programmer firmware image', toolTip='The custom flash programmer firmware image that\r\nimplements low level flash programming commands', size=(300,
                                                                                                                                                                                                                                                                                                                           -1), changeCallback=self.mOnCFbbhCallback)
                    if PRESERVE_SECTOR_NUM == 3:
                        self.SectorSaveNoStr = 'Sector 3:'
                    else:
                        self.SectorSaveNoStr = 'Sector 7:'
                    self.Sector3ChoiceLabel1 = wx.StaticText(self.panel, -1, self.SectorSaveNoStr, size=(50,
                                                                                                         18))
                    self.Sector3ChoiceLabel2 = wx.StaticText(self.panel, -1, 'Programming:')
                    self.oSector3Choice = wx.Choice(self.panel, -1, choices=['Erase', 'Preserve', 'Restore'])
                    self.Bind(wx.EVT_CHOICE, self.mOnSelectSector3Choice, self.oSector3Choice)
                    self.oSector3Choice.Select(self.iSector3Programming)
                    oSaveSector3Btn = wx.Button(self.panel, -1, 'Save', size=(50, 25))
                    self.Bind(wx.EVT_BUTTON, self.mOnSaveSector3, oSaveSector3Btn)
                    self.oFBBHSector3File = filebrowse.FileBrowseButtonWithHistory(self.panel, -1, fileMask=sSector3Wildcard, labelText='', dialogTitle='Choose sector ' + str(PRESERVE_SECTOR_NUM) + ' file name', toolTip='The file to use for saving/restoring sector ' + str(PRESERVE_SECTOR_NUM), size=(300,
                                                                                                                                                                                                                                                                                                             -1), changeCallback=self.mOnSector3fbbhCallback)
                    self.baudRateChoices = [
                     '38400', '57600', '115200', '250000', '500000', '1000000']
                    self.oBaudRateChoiceLabel = wx.StaticText(self.panel, -1, 'Baud Rate:')
                    self.oBaudRateChoice = wx.Choice(self.panel, -1, (100, 50), choices=self.baudRateChoices)
                    self.Bind(wx.EVT_CHOICE, self.mOnSelectBaudRate, self.oBaudRateChoice)
                    self.oBaudRateChoice.Select(self.iBaudRateChoice)
                    self.flashChoices = [
                     'Internal', 'External']
                    self.oFlashChoiceLabel = wx.StaticText(self.panel, -1, 'Flash Select:')
                    self.oFlashChoices = wx.Choice(self.panel, -1, choices=self.flashChoices)
                    self.Bind(wx.EVT_CHOICE, self.mOnSelectFlash, self.oFlashChoices)
                    self.oFlashChoices.Select(USE_INTERNAL_FLASH)
                    if self.bUse16AddrCheckBox:
                        self.o16BitAddrCheckBox = wx.CheckBox(self.panel, -1, '16 bit: ', style=wx.ALIGN_RIGHT)
                        self.o16BitAddrCheckBox.SetValue(True)
                        self.o16BitAddrCheckBox.Enable(self.bInternalBuild)
                        self.Bind(wx.EVT_CHECKBOX, self.mOn16BitAddr, self.o16BitAddrCheckBox)
                    if self.bInternalBuild:
                        self.chipSelectChoices = [
                         '1', '2', '3', '4', '5']
                        self.oChipSelectChoice = wx.Choice(self.panel, -1, (100, 50), choices=self.chipSelectChoices)
                        self.Bind(wx.EVT_CHOICE, self.mOnSelectChipSelect, self.oChipSelectChoice)
                        self.oChipSelectChoice.Select(0)
                    if self.bAllowEncryption:
                        oPasskeyBtn = wx.Button(self.panel, -1, 'Set Passkey', size=(80,
                                                                                     20))
                        self.Bind(wx.EVT_BUTTON, self.mOnPasskey, oPasskeyBtn)
                    oFTDISizerRow1.Add(oToggleRPCheckBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oFTDISizerRow2.Add(self.oGenRSTBtn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 25)
                    oFTDISizer.Add(oFTDISizerRow1, proportion=0, flag=wx.ALL, border=0)
                    oFTDISizer.Add(oFTDISizerRow2, proportion=0, flag=wx.ALL, border=0)
                    oCfgSizerRowP.Add(self.oFBBHFirmware, 0, wx.EXPAND | wx.ALL, 5)
                    oCfgSizerRowP.Add(oClrHistBtn, 0, wx.ALL, 5)
                    oCfgSizerRow1.Add(self.ComportLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow1.Add(self.oCOMPortChoice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow1.Add(oCOMRefeshBtn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow1.Add(self.oConnectCOMPortCheckBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow1.Add(oSkipVerificationCheckBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow2.Add(self.TargetLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow2.Add(self.TargetChoice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow3.Add(self.oCustomFlashProgrammer, 0, wx.EXPAND | wx.ALL, 5)
                    oCfgSizerRow4.Add(self.Sector3ChoiceLabel1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow4.Add(oSaveSector3Btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow4.Add(self.Sector3ChoiceLabel2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow4.Add(self.oSector3Choice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow4.Add(self.oFlashChoiceLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow4.Add(self.oFlashChoices, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow2.Add(self.oBaudRateChoiceLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow2.Add(self.oBaudRateChoice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    oCfgSizerRow5.Add(self.oFBBHSector3File, 0, wx.EXPAND | wx.ALL, 5)
                    if self.bUse16AddrCheckBox:
                        oCfgSizerRow2.Add(self.o16BitAddrCheckBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    if self.bAllowEncryption:
                        oCfgSizerRow2.Add(oPasskeyBtn, 0, wx.ALL, 5)
                    if self.bInternalBuild:
                        oCfgSizerRow2.Add(self.oChipSelectChoice, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                    if self.bInternalBuild:
                        if self.iExtras:
                            oRTSAssertedCheckBox = wx.CheckBox(self.panel, 1, 'RTS Asserted')
                            oRTSAssertedCheckBox.SetValue(self.bRTSAsserted)
                            self.Bind(wx.EVT_CHECKBOX, self.mOnSelectRTS, oRTSAssertedCheckBox)
                            oCfgSizerRow6.Add(oRTSAssertedCheckBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                            oDebugCheckBox = wx.CheckBox(self.panel, 1, 'Debug')
                            oDebugCheckBox.SetValue(self.bDebug)
                            self.Bind(wx.EVT_CHECKBOX, self.mOnSelectDebug, oDebugCheckBox)
                            oCfgSizerRow6.Add(oDebugCheckBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                        oCfgSizer.Add(oCfgSizerRowP, proportion=0, flag=wx.ALL, border=0)
                        oCfgSizer.Add(oCfgSizerRow1, proportion=0, flag=wx.ALL, border=0)
                        oCfgSizer.Add(oCfgSizerRow2, proportion=0, flag=wx.ALL, border=0)
                        oCfgSizer.Add(oCfgSizerRow3, proportion=0, flag=wx.EXPAND | wx.ALL, border=0)
                        oCfgSizer.Add(oCfgSizerRow4, proportion=0, flag=wx.ALL, border=0)
                        oCfgSizer.Add(oCfgSizerRow5, proportion=0, flag=wx.EXPAND | wx.ALL, border=0)
                        oCfgSizer.Add(oCfgSizerRow6, proportion=0, flag=wx.EXPAND | wx.ALL, border=0)
                        self.oMacAddressOptionBox = wx.StaticBox(self.panel, -1, label='Device')
                        oMacAddressOptionSBSizer = wx.StaticBoxSizer(self.oMacAddressOptionBox, wx.VERTICAL)
                        oDeviceInfoSizer = wx.BoxSizer(wx.HORIZONTAL)
                        self.DeviceLabel1 = wx.StaticText(self.panel, -1, 'Device:', size=(40,
                                                                                           18))
                        self.DeviceLabel2 = wx.StaticText(self.panel, -1, '..........', size=(150,
                                                                                              18))
                        oDeviceInfoSizer.Add(self.DeviceLabel1, 0, wx.ALL, 5)
                        oDeviceInfoSizer.Add(self.DeviceLabel2, 0, wx.ALL, 5)
                        self.FlashLabel1 = wx.StaticText(self.panel, -1, 'Flash:', size=(30,
                                                                                         18))
                        self.FlashLabel2 = wx.StaticText(self.panel, -1, '..........', size=(150,
                                                                                             18))
                        oDeviceInfoSizer.Add(self.FlashLabel1, 0, wx.ALL, 5)
                        oDeviceInfoSizer.Add(self.FlashLabel2, 0, wx.ALL, 5)
                        oMacAddressOptionSBSizer.Add(oDeviceInfoSizer, proportion=0, flag=wx.ALL, border=0)
                        if self.bAllowMACprogamming:
                            self.radioList = ['Use MAC address embedded in application binary',
                             'Reuse existing MAC address in target device (shown in MAC Address field below)',
                             'Use next available MAC address from MAC address list file',
                             'Type new MAC address (in MAC Address field below)']
                            self.FlashProcessingRadioBox = wx.RadioBox(self.panel, 1, 'Choose how you want to assign the MAC address', choices=self.radioList, majorDimension=4, style=wx.RA_SPECIFY_ROWS)
                            self.FlashProcessingRadioBox.SetStringSelection('Reuse existing MAC address in target device (shown in MAC Address field below)')
                            wx.EVT_RADIOBOX(self.FlashProcessingRadioBox, 1, self.FlashProcessingRadioClick)
                            self.oLicenceFileBox = wx.StaticBox(self.panel, -1, label='MAC Address List File')
                            oLicenceFileSizer = wx.StaticBoxSizer(self.oLicenceFileBox, wx.VERTICAL)
                            self.oFBBHLicence = filebrowse.FileBrowseButtonWithHistory(self.panel, -1, fileMask=sLicenceWildcard, changeCallback=self.mOnLFbbhCallback)
                            self.oFBBHLicence.SetLabel('')
                            self.oFBBHLicence.Enable(False)
                            self.LicMgr = None
                            oLicenceFileSizer.Add(self.oFBBHLicence, 0, wx.EXPAND | wx.ALL, 5)
                        self.oMacAddressBox = wx.StaticBox(self.panel, -1, label='MAC Address (Hex)')
                        oMacAddressSBSizer = wx.StaticBoxSizer(self.oMacAddressBox, wx.HORIZONTAL)
                        self.macAddr = [None, None, None, None, None, None, None, None]
                        for i in range(8):
                            self.macAddr[i] = wx.TextCtrl(self.panel, -1, '00', size=(30,
                                                                                      -1), validator=FlexValidator.cFlexValidator(2, 2, '0123456789ABCDEFabcdef'))
                            self.macAddr[i].Enable(False)

                        self.oMacAddressBox.Enable(False)
                        oReadMACBtn = wx.Button(self.panel, -1, 'Refresh', size=(100,
                                                                                 30))
                        self.Bind(wx.EVT_BUTTON, self.mOnReadMACAddrFromDevice, oReadMACBtn)
                        self.oAutoIncrCheckBox = wx.CheckBox(self.panel, 0, 'Auto-increment Address')
                        self.oAutoIncrCheckBox.SetValue(False)
                        self.Bind(wx.EVT_CHECKBOX, self.mOnSelectAutoIncr, self.oAutoIncrCheckBox)
                        self.oAutoIncrCheckBox.Enable(False)
                        for i in range(8):
                            oMacAddressSBSizer.Add(self.macAddr[i], 0, wx.EXPAND | wx.ALL, 5)

                        oMacAddressSBSizer.Add(oReadMACBtn, 0, wx.EXPAND | wx.ALL, 5)
                        if self.bAllowMACprogamming:
                            oMacAddressOptionSBSizer.Add(self.FlashProcessingRadioBox, 0, wx.EXPAND | wx.ALL, 5)
                            oMacAddressOptionSBSizer.Add(oLicenceFileSizer, 0, wx.EXPAND | wx.ALL, 5)
                        oMacAddressOptionSBSizer.Add(oMacAddressSBSizer, 0, wx.EXPAND | wx.ALL, 5)
                        oMacAddressOptionSBSizer.Add(self.oAutoIncrCheckBox, 0, wx.ALL, 5)
                        self.oButtonBox = wx.StaticBox(self.panel, -1, label='Control')
                        oButtonSizer = wx.StaticBoxSizer(self.oButtonBox, wx.VERTICAL)
                        self.oActionBox = wx.StaticBox(self.panel, -1, label='Action')
                        oActionSizer = wx.StaticBoxSizer(self.oActionBox, wx.VERTICAL)
                        if (self.bInternalBuild and self).iUseRead:
                            oReadBtn = wx.Button(self.panel, -1, 'Read', size=(120,
                                                                               30))
                            self.Bind(wx.EVT_BUTTON, self.mOnReadFlash, oReadBtn)
                            oReadRAMBtn = wx.Button(self.panel, -1, 'RdRAM', size=(120,
                                                                                   30))
                            self.Bind(wx.EVT_BUTTON, self.mOnReadRAM, oReadRAMBtn)
                        self.oAboutBtn = wx.Button(self.panel, -1, 'About', size=(120,
                                                                                  30))
                        self.Bind(wx.EVT_BUTTON, self.mOnAbout, self.oAboutBtn)
                        self.oProgBtn = wx.Button(self.panel, -1, 'Program', size=(120,
                                                                                   30))
                        self.Bind(wx.EVT_BUTTON, self.mOnProgramFlash, self.oProgBtn)
                        if (self.bInternalBuild and self).bAllowMACprogamming:
                            oInstallLicBtn = wx.Button(self.panel, -1, 'Install Lic', size=(100,
                                                                                            30))
                            self.Bind(wx.EVT_BUTTON, self.mOnInstallLicense, oInstallLicBtn)
                        self.oEraseEEPROMBtn = wx.Button(self.panel, -1, 'Erase EEPROM', size=(120,
                                                                                               30))
                        self.Bind(wx.EVT_BUTTON, self.mOnEraseEEPROM, self.oEraseEEPROMBtn)
                        self.oEraseEEPROMBtn.Enable(0)
                        if (self.bInternalBuild and self).iUseRead:
                            oActionSizer.Add(oReadBtn, 0, wx.EXPAND | wx.ALL, 5)
                            oActionSizer.Add(oReadRAMBtn, 0, wx.EXPAND | wx.ALL, 5)
                        if (self.bInternalBuild and self).bAllowMACprogamming:
                            oActionSizer.Add(oInstallLicBtn, 0, wx.EXPAND | wx.ALL, 5)
                        oActionSizer.Add(self.oProgBtn, 0, wx.EXPAND | wx.ALL, 5)
                        oActionSizer.Add(self.oEraseEEPROMBtn, 0, wx.EXPAND | wx.ALL, 5)
                        oActionSizer.Add(self.oAboutBtn, 0, wx.EXPAND | wx.ALL, 5)
                        oButtonSizer.Add(oFTDISizer, 0, wx.EXPAND | wx.ALL, 5)
                        oButtonSizer.Add(oActionSizer, 0, wx.EXPAND | wx.ALL, 5)
                        oVMainSizer = wx.BoxSizer(wx.VERTICAL)
                        oVMainSizer.Add(oCfgSizer, 0, wx.EXPAND | wx.ALL, 5)
                        oVMain2Sizer = wx.BoxSizer(wx.HORIZONTAL)
                        oVMain2Sizer.Add(oMacAddressOptionSBSizer, 1, wx.EXPAND | wx.ALL, 5)
                        oVMain2Sizer.Add(oButtonSizer, 0, wx.EXPAND | wx.ALL, 5)
                        oVMainSizer.Add(oVMain2Sizer, 0, wx.EXPAND | wx.ALL, 5)
                        self.panel.SetSizer(oVMainSizer)
                        self.panel.SetAutoLayout(True)
                        self.panel.Layout()
                        oVMainSizer.Fit(self.panel)
                        self.oFBBHFirmware.SetHistory(self.aHistory)
                        try:
                            self.oFBBHFirmware.SetValue(self.aHistory[0])
                        except:
                            pass
                        else:
                            self.oFBBHFirmware.Enable(True)
                            if self.bAllowMACprogamming:
                                self.oFBBHLicence.SetHistory(self.aLHistory)
                                try:
                                    self.oFBBHLicence.SetValue(self.aLHistory[0])
                                except:
                                    pass

                            self.oFBBHSector3File.SetHistory(self.aS3History)
                            try:
                                self.oFBBHSector3File.SetValue(self.aS3History[0])
                            except:
                                pass
                            else:
                                self.oFBBHSector3File.Enable(True)
                                if self.iUse2Stage:
                                    self.oCustomFlashProgrammer.SetHistory(self.aCHistory)
                                    try:
                                        self.oCustomFlashProgrammer.SetValue(self.aCHistory[0])
                                    except:
                                        pass

                                self.lstCOMConnectEnableWidgets = [
                                 self.oCOMPortChoice,
                                 oReadMACBtn,
                                 self.oProgBtn,
                                 self.oCustomFlashProgrammer,
                                 self.oGenRSTBtn]
                                if self.bUse16AddrCheckBox:
                                    if self.bInternalBuild:
                                        self.lstCOMConnectEnableWidgets.append(self.o16BitAddrCheckBox)
                                    (not self.bUse16AddrCheckBox or self.bInternalBuild) and self.lstCOMConnectEnableWidgets.append(self.TargetChoice)
                                else:
                                    self.TargetChoice.Enable(False)
                                if self.bInternalBuild:
                                    self.lstCOMConnectEnableWidgets.append(oInstallLicBtn)
                                if self.bAllowEncryption:
                                    self.lstCOMConnectEnableWidgets.append(oPasskeyBtn)
                                if (self.iUseRead and self).bInternalBuild:
                                    self.lstCOMConnectEnableWidgets.append(oReadBtn)
                                    self.lstCOMConnectEnableWidgets.append(oReadRAMBtn)
                                if (self.iExtras and self).bInternalBuild:
                                    self.lstCOMConnectEnableWidgets.append(oDebugCheckBox)
                                self.bUse16AddrCheckBox and self.mSelectTargetInterface('Custom Flash')
                                self.oCustomFlashProgrammer.Enable(1)
                    self.oCustomFlashProgrammer.Enable(False)

                if self.iBaudRateChoice != 0:
                    sBaudRate = self.baudRateChoices[self.iBaudRateChoice]
                    self.iBaudRate = int(sBaudRate)
                    self.mCalcIdivisor(self.iBaudRate)

            return

        def mSaveData(self):
            oCfgFile = open('config.txt', 'wb')
            oPickler = pickle.Pickler(oCfgFile)
            oPickler.dump(self.aLHistory)
            oPickler.dump(self.aHistory)
            if self.sComPort == None:
                oPickler.dump(self.oCOMPortChoice.GetStringSelection())
            else:
                oPickler.dump(self.sComPort)
            oPickler.dump(self.iSector3Programming)
            oPickler.dump(self.oBaudRateChoice.GetSelection())
            oPickler.dump(self.bDebug)
            oPickler.dump(self.aCHistory)
            oPickler.dump(self.bSkipVerification)
            oPickler.dump(self.bGenerateResetAndProgram)
            oPickler.dump(self.aS3History)
            oPickler.dump(self.sDefaultKey)
            oCfgFile.close()
            return

        def OnRefit(self, evt):
            self.Fit()

        def mRefreshDeviceInfo(self):
            if self.bGenerateResetAndProgram == True:
                self.mControlRandP(False)
            self.DeviceInfo.Reset()
            if self.bAllowMACprogamming:
                bUpdateMacAddress = self.FlashProcessingRadioBox.GetSelection() == 1
            else:
                bUpdateMacAddress = 1
            if bUpdateMacAddress:
                for i in range(8):
                    self.macAddr[i].SetValue('00')

            self.DeviceLabel2.SetLabel('..........')
            self.FlashLabel2.SetLabel('..........')
            try:
                self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
                eReadResult = self.DeviceInfo.mRefreshDeviceInfo(self.oZsa, self.abEncryptKey, self.oFlashChoices.GetSelection(), self.bUse16AddrCheckBox and self.o16BitAddrCheckBox.GetValue())
                if eReadResult == ZedSerialEnum.AUTH_ERROR:
                    self.oZsa.oZsp.oHandle.mDisableRTS()
                    bLoginOk = self.mLogin()
                    self.oZsa.oZsp.oHandle.mEnableRTS()
                    if not bLoginOk:
                        eReadResult = ZedSerialEnum.AUTH_ERROR
                        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
                        self.oZsa.oZsp.oHandle.mEnableRTS()
                        return eReadResult
                    else:
                        eReadResult = self.DeviceInfo.mRefreshDeviceInfo(self.oZsa, self.abEncryptKey, self.oFlashChoices.GetSelection(), self.bUse16AddrCheckBox and self.o16BitAddrCheckBox.GetValue())
            except AssertionError:
                eReadResult = ZedSerialEnum.NO_RESPONSE
            else:
                self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
                self.oZsa.oZsp.oHandle.mEnableRTS()
                if eReadResult != ZedSerialEnum.OK:
                    wx.MessageBox(self.DeviceInfo.sErrorMsg, 'Flash Programmer - verifying connectivity', wx.ICON_EXCLAMATION)
                    return eReadResult
                if self.DeviceInfo.iProcessorPartNo == 0:
                    self.oBaudRateChoice.Enable(0)
                else:
                    self.oBaudRateChoice.Enable(1)
                if self.DeviceInfo.iProcessorPartNo != 8:
                    self.oFlashChoices.Enable(0)
                    self.oFlashChoices.Select(USE_EXTERNAL_FLASH)
                    self.oEraseEEPROMBtn.Enable(0)
                    self.FlashProcessingRadioBox.EnableItem(0, True)
                    self.FlashProcessingRadioBox.EnableItem(2, True)
                    self.FlashProcessingRadioBox.EnableItem(3, True)
                else:
                    self.oFlashChoices.Enable(1)
                    self.oEraseEEPROMBtn.Enable(1)
                    if self.DeviceInfo.bCustomerProgrammedMac:
                        self.FlashProcessingRadioBox.SetSelection(1)
                        self.FlashProcessingRadioClick(None)
                        self.FlashProcessingRadioBox.EnableItem(2, False)
                        self.FlashProcessingRadioBox.EnableItem(3, False)
                    else:
                        self.FlashProcessingRadioBox.EnableItem(3, True)
                        self.FlashProcessingRadioBox.EnableItem(2, True)
                    self.FlashProcessingRadioBox.EnableItem(0, False)
                self.DeviceLabel2.SetLabel(self.DeviceInfo.sDevicelabel)
                if bUpdateMacAddress:
                    for i in range(8):
                        self.macAddr[i].SetValue(binascii.b2a_hex(self.DeviceInfo.abMacAddress[i]))

                if self.DeviceInfo.bFlashIsEncrypted == False:
                    self.FlashLabel2.SetLabel(self.DeviceInfo.sFlashLabel)
                self.FlashLabel2.SetLabel(self.DeviceInfo.sFlashLabel + ' (Encrypted)')

            return ZedSerialEnum.OK

        def mEvtClose(self, evt):
            self.mSaveData()
            if self.oZsa is not None:
                del self.oZsa
#             self.MakeModal(False)
            self.Destroy()
            return

        def mOnConnectCOMPort(self, evt):
            self.bConnectCOMPort = evt.IsChecked()
            if self.bConnectCOMPort:
                self.mSelectComPort(self.oCOMPortChoice.GetStringSelection(), not self.bInternalBuild)
                if self.TargetChoice.GetStringSelection() == 'Custom Flash':
                    self.mSelectTargetInterface('Custom Flash')
            if self.oZsa is not None:
                del self.oZsa
                self.oZsa = None
            self.sComPort = None
            for widget in self.lstCOMConnectEnableWidgets:
                widget.Disable()

            return

        def mOnSelectDebug(self, evt):
            self.bDebug = evt.IsChecked()
            if self.oZsa is not None:
                self.oZsa.oZsp.mSetDebug(int(self.bDebug))
                self.oZsa.mSetDebug(int(self.bDebug))
            return

        def mOnSelectAutoIncr(self, evt):
            self.bAutoIncr = evt.IsChecked()

        def mOnSelectRTS(self, evt):
            self.bRTSAsserted = evt.IsChecked()
            if self.oZsa is not None:
                self.oZsa.oZsp.oHandle.mSetRTS(self.bRTSAsserted)
            if self.FlashUtilIF is not None:
                self.FlashUtilIF.SetRTSAsserted(self.bRTSAsserted)
            return

        def OnSelectSkipVerification(self, evt):
            self.bSkipVerification = evt.IsChecked()

        def GenerateResetAndProgram(self, evt):
            self.bGenerateResetAndProgram = evt.IsChecked()

        def mResetTarget(self, evt):
            self.mControlRandP(True)

        def mCOMPortRefresh(self, evt):
            if self.oZsa is not None:
                del self.oZsa
                self.oZsa = None
            self.ComPortList = ComPortList.fGetComPortList()
            if self.oConnectCOMPortCheckBox.IsChecked():
                self.oZsa = ZedSerialApi.cZedSerialApi(DefaultBaudRate, self.sComPort)
                if self.oZsa.mCheckOpened() == ZedSerialEnum.OK:
                    self.oZsa.oZsp.mSetDebug(bool(self.bDebug))
            self.oCOMPortChoice.Clear()
            for line in self.ComPortList:
                self.oCOMPortChoice.Append(line)

            self.oCOMPortChoice.Select(self.ComPortList.index(self.sComPort))
            return

        def mControlRandP(self, Mode):
            if self.oZsa is not None:
                del self.oZsa
                self.oZsa = None
            d = d2xx.listDevices()
            comindex = -1
            counter = 0
            if d != 0:
                for j in d:
                    try:
                        hl = d2xx.open(counter)
                        a = hl.getComPortNumber()
                        a = 'COM' + str(a)
                        if self.sComPort == a:
                            comindex = counter
                        hl.close()
                    except:
                        print('.')
                    else:
                        counter += 1

            if comindex != -1:
                h = d2xx.open(comindex)
                h.purge()
                if Mode == True:
                    h.setBitMode(64, 32)
                else:
                    h.setBitMode(192, 32)
                    time.sleep(0.2)
                    h.setBitMode(196, 32)
                    time.sleep(0.2)
                    h.setBitMode(204, 32)
                time.sleep(0.2)
                h.setBitMode(0, 32)
                time.sleep(0.2)
                h.close()
            if self.oConnectCOMPortCheckBox.IsChecked():
                self.oZsa = ZedSerialApi.cZedSerialApi(DefaultBaudRate, self.sComPort)
                if self.oZsa.mCheckOpened() == ZedSerialEnum.OK:
                    self.oZsa.oZsp.mSetDebug(bool(self.bDebug))
            return

        def mOnAbout(self, evt):
            if self.bInternalBuild:
                oDlg = About.FlashProgrammerAboutBox(None, self.sVersion + '<br><font color="#FF0000">Internal NXP Use Only</font>')
            else:
                oDlg = About.FlashProgrammerAboutBox(None, self.sVersion)
            oDlg.ShowModal()
            oDlg.Destroy()
            return

        def mSelectComPort(self, sComPort, boRefreshDeviceInfo=1):
            if self.sComPort != sComPort:
                if self.oZsa is not None:
                    del self.oZsa
                self.sComPort = sComPort
                self.oZsa = ZedSerialApi.cZedSerialApi(DefaultBaudRate, self.sComPort)
                if self.oZsa.mCheckOpened() == ZedSerialEnum.OK:
                    self.oConnectCOMPortCheckBox.SetValue(True)
                    self.oZsa.oZsp.mSetDebug(bool(self.bDebug))
                    for widget in self.lstCOMConnectEnableWidgets:
                        widget.Enable(1)

                    if boRefreshDeviceInfo:
                        self.mRefreshDeviceInfo()
                else:
                    print('No connection to COM port')
                    wx.MessageBox('COM port not open', 'Communication Error', wx.ICON_EXCLAMATION)
                    self.oConnectCOMPortCheckBox.SetValue(False)
                    self.oCOMPortChoice.Enable(1)
                    if self.oZsa is not None:
                        del self.oZsa
                        self.oZsa = None
                    self.sComPort = None
                    return
            return

        def mOnSelectComPort(self, event):
            if event == None:
                sComPort = self.ComPortList[0]
            else:
                sComPort = event.GetString()
            self.mSelectComPort(sComPort)
            return

        def GetCustomProgFileAndAddr(self):
            if self.ProgrammingConfiguration.sCustomFlashProgrammerFile == '':
                self.oCustomFlashProgrammer.OnBrowse(None)
                self.ProgrammingConfiguration.sCustomFlashProgrammerFile = self.oCustomFlashProgrammer.GetValue()
                if not os.path.exists(self.ProgrammingConfiguration.sCustomFlashProgrammerFile):
                    wx.MessageBox('Could not find bootloader file', self.ProgrammingConfiguration.sCustomFlashProgrammerFile, wx.ICON_EXCLAMATION)
                    self.ProgrammingConfiguration.sCustomFlashProgrammerFile = ''
                    self.oProgBtn.Enable(0)
                else:
                    self.oProgBtn.Enable(self.oConnectCOMPortCheckBox.GetValue())
            return (self.ProgrammingConfiguration.sCustomFlashProgrammerFile, None)

        def mOn16BitAddr(self, evt):
            evt.Skip()

        def mOnSelectChipSelect(self, event):
            iChipSelect = int(event.GetString())
            self.oZsa.ZedFlashSetChipSelect(iChipSelect)

        def mOnSelectBaudRate(self, event):
            sBaudRate = event.GetString()
            eReadResult, abData = self.oZsa.ZedFlashReadId()
            self.iBaudRate = int(sBaudRate)
            self.mCalcIdivisor(self.iBaudRate)

        def mOnSelectFlash(self, event):
            sFlash = event.GetString()
            if sFlash == 'External':
                eResult = self.oZsa.ZedFlashSelectType(ZedSerialApi.E_FL_CHIP_ST_M25P10_A)
            else:
                eResult = self.oZsa.ZedFlashSelectType(ZedSerialApi.E_FL_CHIP_INTERNAL)

        def mCalcIdivisor(self, iBaudRate):
            Remainder = 1000000 % self.iBaudRate
            self.iDivisor = int(1000000 / self.iBaudRate)
            if Remainder > 0.5:
                self.iDivisor += 1

        def mOnFbbhCallback(self, event):
            if hasattr(self, 'oFBBHFirmware'):
                self.sFlashFile = event.GetString()
                if self.sFlashFile != '':
                    self.aHistory = self.oFBBHFirmware.GetHistory()
                    if self.sFlashFile not in self.aHistory:
                        self.aHistory.insert(0, self.sFlashFile)
                    else:
                        self.aHistory.remove(self.sFlashFile)
                        self.aHistory.insert(0, self.sFlashFile)
                    self.oFBBHFirmware.SetHistory(self.aHistory, 0)
                self.oFBBHFirmware.toolTip = self.sFlashFile

        def mOnLFbbhCallback(self, event):
            if hasattr(self, 'oFBBHLicence'):
                self.sLicenceFile = event.GetString()
                if self.sLicenceFile != '':
                    self.aLHistory = self.oFBBHLicence.GetHistory()
                    if self.sLicenceFile not in self.aLHistory:
                        self.aLHistory.insert(0, self.sLicenceFile)
                    else:
                        self.aLHistory.remove(self.sLicenceFile)
                        self.aLHistory.insert(0, self.sLicenceFile)
                    self.oFBBHLicence.SetHistory(self.aLHistory, 0)

        def mOnCFbbhCallback(self, event):
            if hasattr(self, 'oCustomFlashProgrammer'):
                self.ProgrammingConfiguration.sCustomFlashProgrammerFile = event.GetString()
                if self.ProgrammingConfiguration.sCustomFlashProgrammerFile != '':
                    self.aCHistory = self.oCustomFlashProgrammer.GetHistory()
                    if self.ProgrammingConfiguration.sCustomFlashProgrammerFile not in self.aCHistory:
                        self.aCHistory.insert(0, self.ProgrammingConfiguration.sCustomFlashProgrammerFile)
                    else:
                        self.aCHistory.remove(self.ProgrammingConfiguration.sCustomFlashProgrammerFile)
                        self.aCHistory.insert(0, self.ProgrammingConfiguration.sCustomFlashProgrammerFile)
                    self.oCustomFlashProgrammer.SetHistory(self.aCHistory, 0)

        def mOnSector3fbbhCallback(self, event):
            if hasattr(self, 'oFBBHSector3File'):
                self.sSector3File = event.GetString()
                if self.sSector3File != '':
                    self.aS3History = self.oFBBHSector3File.GetHistory()
                    if self.sSector3File not in self.aS3History:
                        self.aS3History.insert(0, self.sSector3File)
                    else:
                        self.aS3History.remove(self.sSector3File)
                        self.aS3History.insert(0, self.sSector3File)
                    self.oFBBHSector3File.SetHistory(self.aS3History, 0)

        def FlashProcessingRadioClick(self, event):
            radioIndex = self.FlashProcessingRadioBox.GetSelection()
            self.oMacAddressBox.Enable(False)
            for i in range(8):
                self.macAddr[i].Enable(False)

            if self.bAllowMACprogamming:
                self.oFBBHLicence.Enable(False)
                self.oAutoIncrCheckBox.Enable(False)
            if radioIndex == 2:
                self.bAllowMACprogamming and self.oFBBHLicence.Enable(True)
            else:
                if radioIndex == 3:
                    self.oMacAddressBox.Enable(True)
                    for i in range(8):
                        self.macAddr[i].Enable(True)

                    self.oAutoIncrCheckBox.Enable(True)

        def mSelectTargetInterface(self, sSelection):
            self.TargetChoice.SetStringSelection(sSelection)
            self.ProgrammingConfiguration.Reset()
            self.oProgBtn.Enable(self.oConnectCOMPortCheckBox.GetValue())
            if self.bUse16AddrCheckBox:
                self.o16BitAddrCheckBox.Enable(0)
            if sSelection == 'Detect Flash':
                self.oCustomFlashProgrammer.Enable(0)
                self.oSector3Choice.Enable(1)
                self.mRefreshDeviceInfo()
            else:
                if sSelection == 'RAM Only':
                    self.oCustomFlashProgrammer.Enable(0)
                    self.oSector3Choice.Enable(0)
                    self.ProgrammingConfiguration.eTargetInterface = E_TARGET_INTERFACE_RAM
                else:
                    if sSelection == 'Custom Flash':
                        self.oSector3Choice.Enable(0)
                        self.oSector3Choice.Select(0)
                        self.iSector3Programming = SECTOR3_ERASE
                        self.ProgrammingConfiguration.boCustomProgrammer = 1
                        self.oCustomFlashProgrammer.Enable(1)
                        if (self.bUse16AddrCheckBox and self).bInternalBuild:
                            self.o16BitAddrCheckBox.Enable(1)
                        if not os.path.exists(self.ProgrammingConfiguration.sCustomFlashProgrammerFile):
                            self.GetCustomProgFileAndAddr()

        def mOnSelectSector3Choice(self, event):
            sSelection = event.GetString()
            if sSelection == 'Restore':
                self.iSector3Programming = SECTOR3_RESTORE
            else:
                if sSelection == 'Preserve':
                    self.iSector3Programming = SECTOR3_PRESERVE
                else:
                    self.iSector3Programming = SECTOR3_ERASE

        def mOnSaveSector3(self, evt):
            if self.oZsa is not None:
                if self.mRefreshDeviceInfo() != ZedSerialEnum.OK:
                    if not self.bInternalBuild:
                        return
                if len(self.sSector3File) == 0:
                    wx.MessageBox('Please specify a file name for the sector 3 data', 'Sector 3 file name', wx.ICON_EXCLAMATION)
                    return
                sMACAddress = binascii.b2a_hex(self.DeviceInfo.abMacAddress)
                if self.DeviceInfo.Sector_Len != 32768:
                    SECTOR_LEN = self.DeviceInfo.Sector_Len
                else:
                    SECTOR_LEN = self.DeviceInfo.Sector_Len
                bytesToRead = SECTOR_LEN
                if PRESERVE_SECTOR_NUM == 7:
                    startAddr = PRESERVE_SECTOR_NUM / 2 * SECTOR_LEN
                else:
                    startAddr = PRESERVE_SECTOR_NUM * SECTOR_LEN
                if self.bUse16AddrCheckBox and self.o16BitAddrCheckBox.GetValue():
                    startAddr = startAddr - 1
                iEndAddr, abBlockData = self.FlashUtilIF.ReadBlock(self, self.oZsa, startAddr, bytesToRead, 'Reading Flash from %s' % sMACAddress)
                outFile = open(self.sSector3File, 'wb')
                outFile.write(abBlockData)
                outFile.close()
            else:
                wx.MessageBox('Serial port not open', 'Communication error', wx.ICON_EXCLAMATION)
            return

        def OnSelectTargetChoice(self, event):
            self.mSelectTargetInterface(self.TargetChoice.GetStringSelection())
            if event == None:
                sComPort = 'Detect Flash'
            else:
                sSelection = event.GetString()
            return

        def mOnClearHistory(self, event):
            self.oFBBHFirmware.SetValue('')
            self.aHistory = []
            self.oFBBHFirmware.SetHistory(self.aHistory)
            self.oFBBHLicence.SetValue('')
            self.aLHistory = []
            self.oFBBHLicence.SetHistory(self.aLHistory)

        def mOnEraseEEPROM(self, evt):
            print('EraseEEProm')
            bSuccess = self.bEraseEEPROM(self, self.oZsa)
            return bSuccess

        def mOnReadFlash(self, evt):
            if self.oZsa is not None:
                if self.mRefreshDeviceInfo() != ZedSerialEnum.OK:
                    if not self.bInternalBuild:
                        return
                sMACAddress = binascii.b2a_hex(self.DeviceInfo.abMacAddress)
                dlg = wx.FileDialog(self, 'Select a file to write flash contents to', '.', '', '*.bin', wx.SAVE)
                dlg.SetFilename(sMACAddress + '.bin')
                if dlg.ShowModal() == wx.ID_OK:
                    sFileName = dlg.GetPaths()[0]
                else:
                    sFileName = ''
                dlg.Destroy()
                if sFileName == '':
                    return
                if self.DeviceInfo.Sector_Len != 32768:
                    SECTOR_LEN = self.DeviceInfo.Sector_Len
                else:
                    SECTOR_LEN = self.DeviceInfo.Sector_Len
                if self.DeviceInfo.FlashMID == FlashIdManufacturerInternal:
                    bytesToRead = self.DeviceInfo.FlashDID == FlashIdDeviceInternalJN516x and (self.DeviceInfo.FlashSize * 32 + 32) * 1024
                else:
                    bytesToRead = 4 * SECTOR_LEN
                print('bytesToRead %d' % bytesToRead)
                startAddr = 0
                iEndAddr, abBlockData = self.FlashUtilIF.ReadBlock(self, self.oZsa, startAddr, bytesToRead, 'Reading Flash from %s' % sMACAddress)
                outFile = open(sFileName, 'wb')
                if self.bUse16AddrCheckBox and self.o16BitAddrCheckBox.GetValue():
                    outFile.write(chr(255))
                outFile.write(abBlockData)
                outFile.close()
            else:
                wx.MessageBox('Serial port not open', 'Communication error', wx.ICON_EXCLAMATION)
            return

        def mOnReadRAM(self, evt):
            if self.oZsa is not None:
                if self.mRefreshDeviceInfo() != ZedSerialEnum.OK:
                    if not self.bInternalBuild:
                        return
                sMACAddress = binascii.b2a_hex(self.DeviceInfo.abMacAddress)
                dlg = wx.FileDialog(self, 'Select a file to write RAM contents to', '.', '', '*.bin', wx.SAVE)
                dlg.SetFilename(sMACAddress + '_RAM.bin')
                if dlg.ShowModal() == wx.ID_OK:
                    sFileName = dlg.GetPaths()[0]
                else:
                    sFileName = ''
                dlg.Destroy()
                if sFileName == '':
                    return
                if self.DeviceInfo.Sector_Len != 32768:
                    SECTOR_LEN = self.DeviceInfo.Sector_Len
                abBlockData = ''
                bytesToRead = 3 * SECTOR_LEN
                iRAMBase = 4026531840
                bytesPrLine = 100
                for iOffset in range(0, bytesToRead, bytesPrLine):
                    print('Reading from offset %d' % iOffset)
                    iRet, sData = self.oZsa.ZedRAMRead(iRAMBase + iOffset, bytesPrLine)
                    abBlockData += sData

                print('Writing file')
                outFile = open(sFileName, 'wb')
                outFile.write(abBlockData)
                outFile.close()
            else:
                wx.MessageBox('Serial port not open', 'Communication error', wx.ICON_EXCLAMATION)
            return

        def mOnPasskey(self, event):
            boRetry = 1
            while boRetry:
                boRetry = 0
                dlg = wx.TextEntryDialog(self, '', 'Please enter passkey', 'Login')
                dlg.SetValue(self.sPassKey)
                if dlg.ShowModal() == wx.ID_OK:
                    if self.bDebug == True:
                        print('You entered: %s\n' % dlg.GetValue())
                    self.sPassKey = dlg.GetValue()
                    if wx.MessageBox('Do you want to make this the default passKey?\nWarning: This will make it visable when you next start the program.', 'Default Passkey', wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                        self.sDefaultKey = self.sPassKey
                    self.mSetPassKey()
                    bLogin = self.mLogin()
                    if bLogin == True:
                        wx.MessageBox('Authentication succeeded', 'Login', wx.ICON_EXCLAMATION)
                        self.mRefreshDeviceInfo()
                else:
                    dlg.Destroy()
                    return
                dlg.Destroy()

        def mSetPassKey(self):
            self.abEncryptKey = EncryptUtils.aParsePassKeyString(self.sPassKey)

        def mOnLogin(self, event):
            bLogin = self.mLogin()
            if bLogin == True:
                wx.MessageBox('Authentication succeeded', 'Login', wx.ICON_EXCLAMATION)

        def mLogin(self):
            print('ProcPartNo = %d' % self.DeviceInfo.iProcessorPartNo)
            print('ProcRevNo  = %d' % self.DeviceInfo.iProcessorRevNo)
            print('ProcMaskNo  = %d' % self.DeviceInfo.iMaskNo)
            if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo > 2:
                return True
            if not self.bAllowEncryption:
                wx.MessageBox('The device seems to require authentication which is\nnot supported by this version of the Flash programmer application', 'Device authentication error', wx.ICON_EXCLAMATION)
                return False
            status = self.oZsa.ZedLoginIn(self.abEncryptKey)
            if status == ZedSerialApi.LOGIN_FAILED_MAC_ADDRESS:
                wx.MessageBox('Authentication failed - could not read MAC address', 'Login', wx.ICON_EXCLAMATION)
                return False
            if status == ZedSerialApi.LOGIN_FAILED_NO_RESPONSE:
                wx.MessageBox('Could not log in to device', 'Device did not respond to authentication request', wx.ICON_EXCLAMATION)
                return False
            if status == ZedSerialApi.LOGIN_FAILED_PASSKEY_FAIL:
                wx.MessageBox('Authentication failed - please check the passkey', 'Login', wx.ICON_EXCLAMATION)
                return False
            return True

        def mOnReadMACAddrFromDevice(self, evt):
            self.mRefreshDeviceInfo()

        def ReadFlashFileHeaders(self, sFlashFile):
            try:
                oFile = open(sFlashFile, 'rb')
            except:
                raise UserWarning('Could not find file "' + sFlashFile + '" for programming', None)
            else:
                if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                    lMacOffset = self.DeviceInfo.lMacAddressLocationInFlash + 4
                lMacOffset = self.DeviceInfo.lMacAddressLocationInFlash

            abFlashFileHeader = oFile.read(lMacOffset)
            abMACHeader = oFile.read(MAC_AND_LICENSE_HEADER_SIZE)
            oFile.close()
            return (
             abFlashFileHeader, abMACHeader)

        def VerifyFlashFileMACHeaderAllocated(self):
            bWarn = 0
            abFlashFileHeader, abMACHeader = self.ReadFlashFileHeaders(self.sFlashFile)
            if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                u8MacHeaderSize = 8
            else:
                u8MacHeaderSize = MAC_AND_LICENSE_HEADER_SIZE
            sFmt = '<' + str(MAC_AND_LICENSE_HEADER_SIZE) + 'B'
            lstMacHeader = struct.unpack(sFmt, abMACHeader)
            for i in range(u8MacHeaderSize):
                if lstMacHeader[i] != 255:
                    bWarn = 1

            if bWarn:
                iAnswer = wx.MessageBox('Your program file:\r\n\r\n' + self.sFlashFile + '\r\n\r\ndoes not appear to have space allocated for the MAC address.\r\n\r\n' + 'The MAC address and Licence key will be restored by\r\n' + 'the Flash Programmer and invalidate your program.\r\n\r\n' + 'Are you sure you want to continue?', 'Warning', wx.YES_NO | wx.ICON_EXCLAMATION)
                return iAnswer == wx.YES
            else:
                return 1

        def AutoIncrAddress(self):
            for i in range(7, -1, -1):
                iCurVal = int('0x' + self.macAddr[i].GetValue(), 16) + 1
                if iCurVal <= 255:
                    self.macAddr[i].SetValue(binascii.b2a_hex(chr(iCurVal)))
                    break
                else:
                    self.macAddr[i].SetValue('00')

        def bProgramFileIntoFlash(self, eHeaderDataProcessing, abNewHeaderData):
            sFilename = self.sFlashFile
            if self.DeviceInfo.sDevicelabel == 'JN5148-Z-ID5':
                raise UserWarning('JN5148-Z01 Sample device - Programming not supported', None)
                return bSuccess
            if self.bUse16AddrCheckBox:
                bPatchSpiCfg = self.o16BitAddrCheckBox.GetValue() and 1
            else:
                bPatchSpiCfg = 0
            if self.DeviceInfo.bFlashIsEncrypted == True and (self.DeviceInfo.sDevicelabel == 'JN5148-001' or self.DeviceInfo.sDevicelabel == 'JN5139'):
                encryptFile(self.sFlashFile, 'encryptedTemp.bin', [16, 286397204, 353769240, 0], self.abEncryptKey, self.DeviceInfo.iProcessorPartNo)
                self.sFlashFile = 'encryptedTemp.bin'
            bSuccess = self.FlashUtilIF.bProgramFileIntoFlash(self, self.oZsa, eHeaderDataProcessing, abNewHeaderData, self.sFlashFile, 'Programming %s into flash' % self.sFlashFile, bPatchSpiCfg)
            if bSuccess and not self.bSkipVerification:
                bSuccess = self.FlashUtilIF.bVerifyFlashFile(self, self.oZsa, eHeaderDataProcessing, abNewHeaderData, self.sFlashFile, bPatchSpiCfg)
            self.sFlashFile = sFilename
            if self.oBaudRateChoice != 0:
                self.oZsa.ZedSelectBaudRate(26)
                self.oZsa.SetBaudrate(DefaultBaudRate)
                self.oZsa.oZsp.mClose()
                del self.oZsa
                self.oZsa = ZedSerialApi.cZedSerialApi(DefaultBaudRate, self.sComPort)
            return bSuccess

        def bEraseEEPROM(self, parentFrame, oZsa, sTitle='Erasing EEPROM'):
            count = 0
            max = 10
            if parentFrame is not None:
                dia = EEPROMDialog(self, -1, 'buttons')
                dia.ShowModal()
                dia.Destroy()
            else:
                raise UserWarning('Erasing EEPROM cancelled', None)
            return 1

        def bProgramFileIntoRAMAndRun(self, eHeaderDataProcessing, abNewHeaderData, sFlashFile, sTitle):
            print("bProgramFileIntoRAMAndRun('%s','%s',...)" % (str(eHeaderDataProcessing), str(abNewHeaderData)))
            if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                iResetEntry = self.FlashUtilIF.bProgramNewHeaderFileIntoRAM(self, self.oZsa, eHeaderDataProcessing, abNewHeaderData, sFlashFile, sTitle)
            else:
                iResetEntry = self.FlashUtilIF.bProgramFileIntoRAM(self, self.oZsa, eHeaderDataProcessing, abNewHeaderData, sFlashFile, sTitle)
            bSuccess = iResetEntry != 0
            if bSuccess:
                try:
                    iRet, sSerRet = self.oZsa.RunProgramInRAM(iResetEntry)
                    if iRet != ZedSerialEnum.OK:
                        wx.MessageBox('Error runnning program in RAM\n\nPlease check cabling and power', self.ProgrammingConfiguration.sCustomFlashProgrammerFile, wx.ICON_INFORMATION)
                        bSuccess = 0
                except:
                    bSuccess = 0

            if self.oBaudRateChoice != 0:
                self.oZsa.ZedSelectBaudRate(26)
                self.oZsa.SetBaudrate(DefaultBaudRate)
                self.oZsa.oZsp.mClose()
                del self.oZsa
                self.oZsa = ZedSerialApi.cZedSerialApi(DefaultBaudRate, self.sComPort)
            return bSuccess

        def bProgramCustomFlash(self, eHeaderDataProcessing, abNewHeaderData):
            eRAMHeaderDataProcessing = teHeaderProcessing.OVERWRITE
            abRAMNewHeaderData = None
            if not self.Assert_FW_Chip_Compatibility(self.ProgrammingConfiguration.sCustomFlashProgrammerFile):
                return
            bSuccess = self.bProgramFileIntoRAMAndRun(eRAMHeaderDataProcessing, abRAMNewHeaderData, self.ProgrammingConfiguration.sCustomFlashProgrammerFile, 'Loading boot loader ' + self.ProgrammingConfiguration.sCustomFlashProgrammerFile)
            if not bSuccess:
                return bSuccess
            self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            time.sleep(0.5)
            try:
                bSuccess = self.bProgramFileIntoFlash(eHeaderDataProcessing, abNewHeaderData)
            except AssertionError:
                bSuccess = 0
            else:
                if not bSuccess:
                    self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
                    wx.MessageBox('Error communicating with Custom Flash Programmer\n\nPlease ensure that it was compiled for %s' % self.DeviceLabel2.GetLabel(), self.ProgrammingConfiguration.sCustomFlashProgrammerFile, wx.ICON_INFORMATION)
                self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
                if self.oBaudRateChoice != 0:
                    self.oZsa.ZedSelectBaudRate(26)
                    self.oZsa.SetBaudrate(DefaultBaudRate)
                    self.oZsa.oZsp.mClose()
                    del self.oZsa
                    self.oZsa = ZedSerialApi.cZedSerialApi(DefaultBaudRate, self.sComPort)

            return bSuccess

        def mOnInstallLicense(self, evt):
            try:
                if self.oZsa is not None:
                    if self.oZsa.mCheckOpened() == ZedSerialEnum.OK:
                        self.oZsa.oZsp.oHandle.mDisableRTS()
                        eReadResult, abHeaderData = self.oZsa.ZedFlashRead(self.DeviceInfo.lMacAddressLocationInFlash, 32)
                        if eReadResult != ZedSerialEnum.OK:
                            sWarning = eReadResult == ZedSerialEnum.AUTH_ERROR and 'Authentication error - please check the pass key'
                        else:
                            sWarning = 'Failed to read from flash;\n check cabling and power'
                        raise UserWarning(sWarning, None)
                self.sFlashFilePrev = self.sFlashFile
                self.sFlashFile = 'LicenceGenerator.bin'
                if not os.path.exists(self.sFlashFile):
                    raise UserWarning('License generator file ' + self.sFlashFile + ' not found', None)
                abNewHeaderData = abHeaderData[0:8] + ''
                bSuccess = self.bProgramFileIntoFlash(teHeaderProcessing.CHANGE_MAC_AND_LICENCE, abNewHeaderData)
                if bSuccess:
                    wx.MessageBox(self.sFlashFile, 'License installer successfully written to flash', wx.ICON_INFORMATION)
                self.sFlashFile = self.sFlashFilePrev
            except UserWarning as w:
                if w[0] is not None:
                    print(w[0])
                    wx.MessageBox(w[0], 'Flash Programmer', wx.ICON_EXCLAMATION)
            except:
                traceback.print_exc(file=sys.stdout)
            else:
                try:
                    self.oZsa.oZsp.oHandle.mSetRTS(self.bRTSAsserted)
                except:
                    pass

            return

        def Assert_FW_Chip_Compatibility(self, sFlashFile):
            abFlashFileHeader, abMACHeader = self.ReadFlashFileHeaders(sFlashFile)
            if self.DeviceInfo.iProcessorPartNo > 4 or self.DeviceInfo.iProcessorPartNo == 4 and self.DeviceInfo.iProcessorRevNo == 1 and self.DeviceInfo.iMaskNo == 3:
                u32FwBuildVersion = struct.unpack('>L', abFlashFileHeader[:4])
            else:
                u32FwBuildVersion = struct.unpack('>L', abFlashFileHeader[12:16])
            if self.DeviceInfo.iProcessorPartNo == 8:
                print('FlashHeaderVer 0x%X' % u32FwBuildVersion)
                FwFlashSize = (u32FwBuildVersion[0] & 4278190080) >> 24
                FwRamSize = (u32FwBuildVersion[0] & 16711680) >> 16
                FwProcessorPartNo = u32FwBuildVersion[0] & 255
                if self.DeviceInfo.FlashSize == FwFlashSize:
                    u32ChipRomBuildVersion = self.DeviceInfo.RamSize == FwRamSize and FwProcessorPartNo == self.DeviceInfo.iProcessorPartNo and u32FwBuildVersion
                else:
                    u32ChipRomBuildVersion = 4294967295
            else:
                eReadResult, abRead = self.oZsa.ZedRAMRead(JN51XX_ROM_ID_ADDR, 4)
                if eReadResult != ZedSerialEnum.OK:
                    raise UserWarning('Could not read Processor ROM build ID', None)
                u32ChipRomBuildVersion = struct.unpack('>L', abRead)
            if u32FwBuildVersion != u32ChipRomBuildVersion:
                iAnswer = wx.MessageBox('The firmware file\n\n%s\n\n' % sFlashFile + 'was built for another processor version and might not run on the connected device.\n\n' + 'Are you sure you want to continue?', 'Incompatible Firmware Image', wx.YES_NO | wx.ICON_EXCLAMATION)
                if iAnswer != wx.YES:
                    return False
            return True

        def mOnProgramFlash(self, evt):
            try:
                if not os.path.exists(self.sFlashFile):
                    raise UserWarning('Input file ' + self.sFlashFile + ' not found', None)
                iFileLength = os.stat(self.sFlashFile)[ST_SIZE]
                if self.bUse16AddrCheckBox:
                    iMaxSz = self.o16BitAddrCheckBox.GetValue() and 65536
                else:
                    iMaxSz = 131072
                if self.mRefreshDeviceInfo() != ZedSerialEnum.OK:
                    return
                if not self.Assert_FW_Chip_Compatibility(self.sFlashFile):
                    return
                radioIndex = self.FlashProcessingRadioBox.GetSelection()
                if self.DeviceInfo.bInternalFlash == False:
                    if self.oZsa is not None:
                        if self.oZsa.mCheckOpened() == ZedSerialEnum.OK:
                            eReadResult, abHeaderData = self.oZsa.ZedFlashRead(self.DeviceInfo.lMacAddressLocationInFlash, 32)
                            if eReadResult != ZedSerialEnum.OK:
                                if eReadResult == ZedSerialEnum.AUTH_ERROR:
                                    sWarning = 'Authentication error - please check the pass key'
                                else:
                                    sWarning = 'Failed to read from flash;\n check cabling and power'
                                raise UserWarning(sWarning, None)
                    self.saveMacAndLicense()
                    if self.DeviceInfo.bInternalFlash == True:
                        if radioIndex > 1:
                            iAnswer = wx.MessageBox('The MAC address is one time programmable and is not reversible \nAre you sure you want to write a new MAC address?', 'Flash Programmer', wx.YES_NO | wx.ICON_EXCLAMATION)
                            if iAnswer == wx.YES:
                                sFile = S_EXT_FILE_TITLE
                                sTitle = 'Programming MAC Address'
                                eRAMHeaderDataProcessing = teHeaderProcessing.OVERWRITE
                                abRAMNewHeaderData = None
                                bSuccess = self.bProgramFileIntoRAMAndRun(eRAMHeaderDataProcessing, abRAMNewHeaderData, sFile, sTitle)
                                if bSuccess == True:
                                    print('program to RAM successfull')
                                    print('program MAC in index sector')
                                    if self.oZsa is not None:
                                        if self.oZsa.mCheckOpened() == ZedSerialEnum.OK:
                                            self.oZsa.mSetRxTimeOut(10000)
                                            WriteBytes = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
                                            NewMac = ''
                                            if radioIndex == 2:
                                                if not os.path.exists(self.sLicenceFile):
                                                    raise UserWarning('Licence file ' + self.sLicenceFile + ' not found', None)
                                                self.LicMgr = LicenceManager.CLicenceManager(self.sLicenceFile)
                                                sRetValue, abNewHeaderData = self.LicMgr.ParseLicenceFile()
                                                if sRetValue != 'OK':
                                                    sWarning = 'Licence file bad:' + sRetValue
                                                    del self.LicMgr
                                                    self.LicMgr = None
                                                    raise UserWarning(sWarning, None)
                                                NewMac = abNewHeaderData
                                            for i in range(0, 8):
                                                NewMac += binascii.a2b_hex(('00' + self.macAddr[i].GetValue())[-2:])

                                            for i in range(0, 8):
                                                WriteBytes[i] = ord(NewMac[i])

                                            print('writebytes ')
                                        for i in range(0, 16):
                                            print('%x' % WriteBytes[i])

                                        if self.oZsa.ZedProgramIndexSector(MAC_INDEX_SECTOR_PAGE, MAC_INDEX_SECTOR_WORD, WriteBytes) == ZedSerialEnum.OK:
                                            print('Mac programmed')
                                        else:
                                            print('Program Mac Failed')
                                            self.oZsa.mSetRxTimeOut(ZedSerialApi.DEFAULT_READ_TIMEOUT)
                                        iRet, sSerRet = self.oZsa.RunProgramInRAM(JN516x_BOOTLOADER_ENTRY)
                                        time.sleep(0.5)
                                        self.mRefreshDeviceInfo()
                                    else:
                                        raise UserWarning('Serial port not open', None)
                                else:
                                    print('failed to program mac address')
                                    raise UserWarning(None, None)
                            else:
                                if radioIndex != 1 and self.DeviceInfo.bInternalFlash == False:
                                    if self.DeviceInfo.bGetMacAddrFromFlash == False:
                                        raise UserWarning('Unable to program MAC address as it is in Efuse', 'MAC address in Efuse', None)
                            if self.DeviceInfo.bFlashIsEncrypted == True:
                                if radioIndex > 1:
                                    raise UserWarning('Mac Address cannot be edited when using encrypted flash', None)
                                abNewHeaderData = self.DeviceInfo.bInternalFlash == True and None
                                eHeaderDataProcessing = teHeaderProcessing.OVERWRITE
                            abNewHeaderData = radioIndex == 0 and None
                            eHeaderDataProcessing = teHeaderProcessing.OVERWRITE
                        abNewHeaderData = radioIndex == 1 and None
                        eHeaderDataProcessing = teHeaderProcessing.RETAIN_ALL
                    if radioIndex == 2:
                        if abHeaderData[0:8] != '':
                            iAnswer = wx.MessageBox('It looks like a MAC address is already there\nAre you sure you want to overwrite it?', 'Flash Programmer', wx.YES_NO | wx.ICON_EXCLAMATION)
                            if iAnswer != wx.YES:
                                raise UserWarning(None, None)
                        eHeaderDataProcessing = teHeaderProcessing.CHANGE_MAC_AND_LICENCE
                        if not os.path.exists(self.sLicenceFile):
                            raise UserWarning('Licence file ' + self.sLicenceFile + ' not found', None)
                        self.LicMgr = LicenceManager.CLicenceManager(self.sLicenceFile)
                        sRetValue, abNewHeaderData = self.LicMgr.ParseLicenceFile()
                        sWarning = sRetValue != 'OK' and 'Licence file bad:' + sRetValue
                        del self.LicMgr
                        self.LicMgr = None
                        raise UserWarning(sWarning, None)
                else:
                    if abHeaderData[0:8] != '':
                        iAnswer = wx.MessageBox('It looks like a MAC address is already there\nAre you sure you want to overwrite it?', 'Flash Programmer', wx.YES_NO | wx.ICON_EXCLAMATION)
                        if iAnswer != wx.YES:
                            raise UserWarning(None, None)
                    eHeaderDataProcessing = teHeaderProcessing.CHANGE_MAC
                    abNewHeaderData = ''
                    for i in range(8):
                        abNewHeaderData += binascii.a2b_hex(('00' + self.macAddr[i].GetValue())[-2:])

                    if radioIndex != 0:
                        if self.DeviceInfo.bInternalFlash == False:
                            if self.VerifyFlashFileMACHeaderAllocated() == 0:
                                raise UserWarning('Cancelled', None)
                        abBlockData = None
                        if self.iSector3Programming == SECTOR3_PRESERVE:
                            if PRESERVE_SECTOR_NUM == 7:
                                print('SECTOR7_PRESERVE')
                                iEndAddr, abBlockData = self.FlashUtilIF.ReadBlock(self, self.oZsa, PRESERVE_SECTOR_NUM * SECTOR_LEN, SECTOR_LEN, 'Backing up sector ' + str(PRESERVE_SECTOR_NUM))
                                if iEndAddr != PRESERVE_SECTOR_NUM * SECTOR_LEN + SECTOR_LEN:
                                    raise UserWarning('Could not backup sector ' + str(PRESERVE_SECTOR_NUM), None)
                            else:
                                print('SECTOR3_PRESERVE')
                                iEndAddr, abBlockData = self.FlashUtilIF.ReadBlock(self, self.oZsa, PRESERVE_SECTOR_NUM * SECTOR_LEN, SECTOR_LEN, 'Backing up sector ' + str(PRESERVE_SECTOR_NUM))
                                if iEndAddr != PRESERVE_SECTOR_NUM * SECTOR_LEN + SECTOR_LEN:
                                    raise UserWarning('Could not backup sector ' + str(PRESERVE_SECTOR_NUM), None)
                        else:
                            if self.iSector3Programming == SECTOR3_RESTORE:
                                try:
                                    bytesToRead = SECTOR_LEN
                                    inFile = open(self.sSector3File, 'rb')
                                    abBlockData = inFile.read(SECTOR_LEN)
                                    inFile.close()
                                except:
                                    raise UserWarning('Error reading sector %d file %s' % PRESERVE_SECTOR_NUM, self.sSector3File, None)

                        if self.DeviceInfo.bInternalFlash == False:
                            if self.bAllowMACprogamming:
                                if abHeaderData[0:8] == '':
                                    if radioIndex < 2:
                                        iAnswer = wx.MessageBox('WARNING: Invalid MAC address: FF:FF:FF:FF:FF:FF:FF:FF do you want to continue?', 'Flash Programmer', wx.YES_NO | wx.ICON_EXCLAMATION)
                                        return iAnswer == wx.NO and None
                            if self.oBaudRateChoice != 0 and self.DeviceInfo.iProcessorPartNo != 0:
                                self.oZsa.ZedSelectBaudRate(self.iDivisor)
                                self.oZsa.SetBaudrate(self.iBaudRate)
                                self.oZsa.oZsp.mClose()
                                del self.oZsa
                                self.oZsa = ZedSerialApi.cZedSerialApi(self.iBaudRate, self.sComPort)
                            bSuccess = self.ProgrammingConfiguration.eTargetInterface == E_TARGET_INTERFACE_RAM and self.bProgramFileIntoRAMAndRun(teHeaderProcessing.OVERWRITE, abNewHeaderData, self.sFlashFile, 'Copying file to RAM')
                        else:
                            if self.ProgrammingConfiguration.boCustomProgrammer:
                                bSuccess = self.bProgramCustomFlash(eHeaderDataProcessing, abNewHeaderData)
                            else:
                                bSuccess = self.bProgramFileIntoFlash(eHeaderDataProcessing, abNewHeaderData)
                        if self.ProgrammingConfiguration.eTargetInterface != E_TARGET_INTERFACE_RAM:
                            if self.iSector3Programming == SECTOR3_PRESERVE or self.iSector3Programming == SECTOR3_RESTORE:
                                bSuccess = self.FlashUtilIF.WriteBlock(self, self.oZsa, PRESERVE_SECTOR_NUM * SECTOR_LEN, abBlockData, 'Restoring sector ' + str(PRESERVE_SECTOR_NUM))
                                raise bSuccess or UserWarning('Could not restore sector ' + str(PRESERVE_SECTOR_NUM), None)
                if not self.bInternalBuild and bSuccess:
                    wx.MessageBox(self.sFlashFile, 'Program successfully written to flash', wx.ICON_INFORMATION)
                if radioIndex == 2 and bSuccess:
                    if eHeaderDataProcessing == teHeaderProcessing.CHANGE_MAC_AND_LICENCE or self.DeviceInfo.bInternalFlash == True:
                        self.LicMgr.UpdateLicenceFile(self)
                if (radioIndex == 3 and bSuccess and self).bAutoIncr:
                    self.AutoIncrAddress()
            except UserWarning as w:
                if w[0] is None:
                    wx.MessageBox('Failed to communicate with flash;\n Please check cabling and power', 'Flash Programmer', wx.ICON_EXCLAMATION)
                else:
                    wx.MessageBox(w[0], 'Flash Programmer', wx.ICON_EXCLAMATION)
            except AssertionError as w:
                if w[0] is None:
                    wx.MessageBox('Failed to communicate with flash;\n Please check cabling and power', 'Flash Programmer', wx.ICON_EXCLAMATION)
                else:
                    wx.MessageBox(w[0] + '\n Please check cabling and power', 'Flash Programmer', wx.ICON_EXCLAMATION)
            except:
                traceback.print_exc(file=sys.stdout)
            else:
                try:
                    if self.LicMgr is not None:
                        del self.LicMgr
                        self.LicMgr = None
                    if self.DeviceInfo.iProcessorPartNo == 0:
                        self.oBaudRateChoice.Enable(1)
                    self.oZsa.oZsp.oHandle.mSetRTS(self.bRTSAsserted)
                except:
                    pass

                if self.bGenerateResetAndProgram == True:
                    self.mControlRandP(True)

            return

        def saveMacAndLicense(self):
            sFilename = 'MAC_Address_Log.lic'
            try:
                try:
                    oFile = open(sFilename, 'r')
                except:
                    oFile = open(sFilename, 'w')
                    oFile.write('# Mac Addresses and License Keys Programmed')

                oFile.close()
                sMac = '0x%02X%02X%02X%02X%02X%02X%02X%02X' % struct.unpack('<BBBBBBBB', self.DeviceInfo.abMacAddress)
            except Exception as w:
                wx.MessageBox(w[0], 'Flash Programmer', wx.ICON_EXCLAMATION)


    class CFlashSplashScreen(wx.adv.SplashScreen):

        def __init__(self, Application):
            self.Application = Application
            logo = wx.Image('nxplogo.gif', wx.BITMAP_TYPE_GIF)
            logo = logo.Scale(600, 300)
            aBitmap = logo.ConvertToBitmap()
            splashStyle = wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT
            if Settings.bInternalBuild:
                splashDuration = 1
            else:
                splashDuration = 1000
            splashCallback = None
            wx.adv.SplashScreen.__init__(self, aBitmap, splashStyle, splashDuration, splashCallback)
            self.Bind(wx.EVT_CLOSE, self.OnExit)
            wx.Yield()
            return

        def OnExit(self, evt):
            self.Hide()
            wx.InitAllImageHandlers()
            if Settings.bInternalBuild:
                sVersion = Version.sFlashProgrammerVersion
            else:
                sVersion = Version.sFlashProgrammerVersion
            if Settings.bUse16AddrCheckBox:
                sVersion = sVersion + ' (16 bit)'
            oFlashFrame = FlashProgrammerFrame(None, 'NXP JN51xx Flash Programmer', sVersion)
            self.Application.SetTopWindow(oFlashFrame)
            oFlashFrame.Show(1)
            evt.Skip()
            return

    class FlashProgrammerApp(wx.App):

        def OnInit(self):
            SplashScreen = CFlashSplashScreen(self)
            SplashScreen.Show()
            return True

    def GUIMain(debug=0):
        if Settings.bInternalBuild and Settings.iExtras:
            debug = 1
        oApp = FlashProgrammerApp(debug)
        oApp.MainLoop()

    if __name__ == '__main__':
        GUIMain(len(sys.argv) > 1)
