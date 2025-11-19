import wx
import socket
from utilities import Utilities 


class UserPage(wx.Panel):
    def __init__(self, parent, size, username):
        super(UserPage, self).__init__(parent, size=size)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self, label=f"Welcome {username}!")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL, 20)

        self.SetSizer(self.sizer)
        self.Layout()
