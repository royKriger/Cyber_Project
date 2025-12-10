import wx
import socket
from utilities import Utilities


class UserPage(wx.Panel):
    def __init__(self, parent : wx.Window, size, username : str):
        super(UserPage, self).__init__(parent, size=size)
        self.parent = parent
        self.username = username

        self.client = socket.socket()
        self.client.connect((Utilities.get_pc_ip(), 8200))
        self.client.send("Logged in".encode())
        self.client.recv(1024)
        self.client.send(username.encode())

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self, label=f"Welcome {username}!")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 20)

        self.add = wx.Button(self, label="+ Add", size=(100, 60))
        self.Bind(wx.EVT_BUTTON, lambda event: self.open_dir_dialoge(event), self.add)
        self.sizer.Add(self.add, 0, wx.ALIGN_LEFT | wx.TOP, 20)

        self.sizer.AddStretchSpacer(1)

        self.disconnect = wx.Button(self, label="Disconnect", size=(150, 80))
        self.Bind(wx.EVT_BUTTON, lambda event: self.disconnect_client(), self.disconnect)
        self.sizer.Add(self.disconnect, 0, wx.ALIGN_RIGHT | wx.BOTTOM)

        self.SetSizer(self.sizer)
        self.Layout()


    def open_dir_dialoge(self, event):
        file_dialog = wx.FileDialog(None, "Select a file or folder")
        if file_dialog.ShowModal() == wx.ID_OK:
            file_path = file_dialog.GetPath()
            print(file_path)
            file_name = file_path.split("\\")[-1]
            print(file_name)
            print("waisbhd")
        try:
            with open(file_path, "r") as file:
                lines = file.readline
                content = ""
                for line in lines:
                    content += line
                print(content)
                self.client.send(content.encode())
        except Exception as e:
            print(e)

    
    def disconnect_client(self):
        self.client.send("Log out".encode())
        self.client.close()
        self.parent.show_frame()


class DropTarget(wx.FileDropTarget):
    def __init__(self, window):
        super(DropTarget, self).__init__(self)
        self.window = window


        def OnDropFiles(self, x, y, filenames):
            for file in filenames:
                self.path += file

            return True
