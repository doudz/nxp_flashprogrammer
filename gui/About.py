# uncompyle6 version 3.2.5
# Python bytecode 2.5 (62131)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
# [GCC 8.2.0]
# Embedded file name: About.pyo
# Compiled at: 2012-10-23 15:53:28
import sys, wx, wx.html, wx.lib.wxpTag

class FlashProgrammerAboutBox(wx.Dialog):
    text = '\n<html>\n<body bgcolor="#5090FF">\n<center><table bgcolor="#FFFFFF" width="100%%" cellspacing="0"\ncellpadding="0" border="0">\n<tr>\n    <td>\n    <p></p>\n    </td>\n</tr>\n<tr>\n    <td align="center">\n    <p><A><img src="nxplogo.gif" width="600" height="350"></A></p>\n    </td>\n</tr>\n<tr>\n    <td align="center">\n    <font color="#000090"><h2>Flash Programmer<br>%s</h2></font>\n    </td>\n</tr>\n</table>\n\n\n<p><b>NXP B.V.<b> Copyright (c) 2012</p>\n\n<p><wxp module="wx" class="Button">\n    <param name="label" value="Close">\n    <param name="id"    value="ID_OK">\n</wxp></p>\n</center>\n</body>\n</html>\n'

    def __init__(self, parent, sInitText):
        wx.Dialog.__init__(self, parent, -1, 'About NXP Flash Programmer')
        html = wx.html.HtmlWindow(self, -1, size=(320, -1))
        html.SetPage(self.text % sInitText)
        btn = html.FindWindowById(wx.ID_OK)
        ir = html.GetInternalRepresentation()
        html.SetSize((ir.GetWidth() + 25, ir.GetHeight() + 25))
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)


class JenTermAboutBox(wx.Dialog):
    text = '\n<html>\n<body bgcolor="#5090FF">\n<center><table bgcolor="#FFFFFF" width="100%%" cellspacing="0"\ncellpadding="0" border="0">\n<tr>\n    <td>\n    <p></p>\n    </td>\n</tr>\n<tr>\n    <td align="center">\n    <p><A><img src="nxplogo.gif"></A></p>\n    </td>\n</tr>\n<tr>\n    <td align="center">\n    <font color="#000090"><h2>NXP Terminal - beta<br>%s</h2></font>\n    </td>\n</tr>\n</table>\n\n\n<p><b>NXP B.V.<b> Copyright (c)2012</p>\n\n<p><wxp module="wx" class="Button">\n    <param name="label" value="Close">\n    <param name="id"    value="ID_OK">\n</wxp></p>\n</center>\n</body>\n</html>\n'

    def __init__(self, parent, sInitText):
        wx.Dialog.__init__(self, parent, -1, 'About NXP Terminal')
        html = wx.html.HtmlWindow(self, -1, size=(320, -1))
        html.SetPage(self.text % sInitText)
        btn = html.FindWindowById(wx.ID_OK)
        ir = html.GetInternalRepresentation()
        html.SetSize((ir.GetWidth() + 25, ir.GetHeight() + 25))
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)


class FlashZigbeeLicenseAboutBox(wx.Dialog):
    text = '\n<html>\n<body bgcolor="#5090FF">\n<center><table bgcolor="#FFFFFF" width="100%%" cellspacing="0"\ncellpadding="0" border="0">\n<tr>\n    <td>\n    <p></p>\n    </td>\n</tr>\n<tr>\n    <td align="center">\n    <p><A><img src="nxplogo.gif"></A></p>\n    </td>\n</tr>\n<tr>\n    <td align="center">\n    <font color="#000090"><h2>NXP MAC address / Zigbee License Installer<br>%s</h2></font>\n    </td>\n</tr>\n</table>\n\n\n<p><b>NXP B.V.<b> Copyright (c) 2012</p>\n\n<p><wxp module="wx" class="Button">\n    <param name="label" value="Close">\n    <param name="id"    value="ID_OK">\n</wxp></p>\n</center>\n</body>\n</html>\n'

    def __init__(self, parent, sInitText):
        wx.Dialog.__init__(self, parent, -1, 'About NXP Zigbee License Installer')
        html = wx.html.HtmlWindow(self, -1, size=(320, -1))
        html.SetPage(self.text % sInitText)
        btn = html.FindWindowById(wx.ID_OK)
        ir = html.GetInternalRepresentation()
        html.SetSize((ir.GetWidth() + 25, ir.GetHeight() + 25))
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = MyAboutBox(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()