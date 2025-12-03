import wx
import socket
from utilities import Utilities

class UserPage(wx.Panel):
    def __init__(self, parent, size, username):
        super(UserPage, self).__init__(parent, size=size)
        
        #self.client = socket.socket()
        #self.client.connect((Utilities.get_pc_ip(), 8200))
        #self.client.send("In".encode())

        self.path = ""

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self, label=f"Welcome {username}!")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 20)

        self.add = wx.Button(self, label="+ Add", size=(100, 60))
        self.Bind(wx.EVT_BUTTON, lambda event: self.open_dir_dialog(event), self.add)
        self.sizer.Add(self.add, 0, wx.ALIGN_LEFT | wx.TOP, 20)

        self.sizer.AddStretchSpacer(1)

        self.disconnect = wx.Button(self, label="Disconnect", size=(150, 80))
        self.Bind(wx.EVT_BUTTON, lambda event: parent.show_frame(cur=self), self.disconnect)
        self.sizer.Add(self.disconnect, 0, wx.ALIGN_RIGHT | wx.BOTTOM)

        self.SetSizer(self.sizer)
        self.Layout()


class DropTarget(wx.FileDropTarget):
    def __init__(self, window):
        super(DropTarget, self).__init__(self)
        self.window = window


        def OnDropFiles(self, x, y, filenames):
            for file in filenames:
                self.path += file

            return True
