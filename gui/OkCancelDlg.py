# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: OkCancelDlg.pyo
# Compiled at: 2005-05-24 16:39:48
import wx

class cOkCancelDlg(wx.Dialog):

    def __init__(self, parent, ID, sTitle):
        wx.Dialog.__init__(self, parent, ID, sTitle)

    def mAddOkCancelButtons(self, oOuterBoxSizer):
        oButtonBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        oOKButton = wx.Button(self, wx.ID_OK, ' OK ')
        oOKButton.SetDefault()
        oButtonBoxSizer.Add(oOKButton, 0, wx.ALL, 10)
        oButtonBoxSizer.Add(wx.Button(self, wx.ID_CANCEL, ' Cancel '), 0, wx.ALL, 10)
        oOuterBoxSizer.Add(oButtonBoxSizer, 0, wx.ALIGN_CENTER)
        self.SetAutoLayout(True)
        self.SetSizer(oOuterBoxSizer)
        oOuterBoxSizer.Fit(self)
        self.Centre()


def fMain():
    pass


if __name__ == '__main__':
    fMain()