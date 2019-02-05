# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: ComPortDlg.pyo
# Compiled at: 2005-08-08 11:43:51
import sys, wx
from OkCancelDlg import *
import ComPortList

class cComPortDlg(cOkCancelDlg):

    def __init__(self, parent, iWxID, sComPort, iRate):
        cOkCancelDlg.__init__(self, parent, iWxID, 'Serial port')
        self.sComPort = sComPort
        self.iRate = iRate
        oOuterBoxSizer = wx.BoxSizer(wx.VERTICAL)
        aComPort = ComPortList.fGetComPortList()
        aRate = [
         '9600',
         '19200',
         '38400',
         '57600',
         '115200']
        oGridBox = wx.FlexGridSizer(2, 2, 2, 2)
        self.oComPortComboBox = wx.ComboBox(self, -1, aComPort[0], choices=aComPort, style=wx.CB_READONLY)
        oGridBox.AddMany([(wx.StaticText(self, -1, 'Serial Port'), 0, wx.EXPAND | wx.ALL, 5),
         (
          self.oComPortComboBox, 0, wx.EXPAND | wx.ALL, 5)])
        oOuterBoxSizer.Add(oGridBox, 0, wx.ALIGN_CENTRE)
        self.mAddOkCancelButtons(oOuterBoxSizer)

    def mUpdateData(self):
        self.sComPort = self.oComPortComboBox.GetValue()

    def mRateToSel(self, iRate):
        try:
            return {9600: 0, 19200: 1, 38400: 2, 57600: 3, 115200: 4}[iRate]
        except:
            return 0

    def mSelToRate(self, iSel):
        try:
            return {0: 9600, 1: 19200, 2: 38400, 3: 57600, 4: 115200}[iSel]
        except:
            return 0


def fMain():
    pass


if __name__ == '__main__':
    fMain()