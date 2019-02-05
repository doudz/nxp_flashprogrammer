# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: FlexValidator.pyo
# Compiled at: 2008-09-29 15:51:18
import wx

class cFlexValidator(wx.PyValidator):

    def __init__(self, iInitCount, iMaxCount, sChars):
        wx.PyValidator.__init__(self)
        self.iCount = iInitCount
        self.iMaxCount = iMaxCount
        self.sChars = sChars
        EVT_CHAR(self, self.mEvHChar)

    def Clone(self):
        return cFlexValidator(self.iCount, self.iMaxCount, self.sChars)

    def Validate(self, win):
        return true

    def TransferFromWindow(self):
        return true

    def TransferToWindow(self):
        return true

    def mEvHChar(self, event):
        oTextCtrl = wxPyTypeCast(event.GetEventObject(), 'wxTextCtrl')
        tSel = oTextCtrl.GetSelection()
        iDiff = abs(tSel[1] - tSel[0])
        bValidKey = false
        iKey = event.GetKeyCode()
        if iKey == WXK_BACK:
            self.iCount = self.iCount - iDiff - 1
            if self.iCount < 0:
                self.iCount = 0
            else:
                bValidKey = true
        else:
            if iKey == WXK_DELETE:
                pass
            else:
                if iKey < WXK_SPACE or iKey > 255:
                    bValidKey = true
                else:
                    if chr(iKey) in self.sChars:
                        self.iCount = self.iCount - iDiff + 1
                        if self.iCount > self.iMaxCount:
                            self.iCount = self.iMaxCount
                        else:
                            bValidKey = true
        if bValidKey:
            event.Skip()
        else:
            if not wxValidator_IsSilent():
                wxBell()


def fMain():
    pass


if __name__ == '__main__':
    fMain()