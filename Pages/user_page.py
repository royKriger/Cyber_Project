import wx
import socket
from utilities import Utilities
from cryptography.hazmat.primitives import serialization


class UserPage(wx.Panel):
    def __init__(self, parent : wx.Window, size, username : str):
        super(UserPage, self).__init__(parent, size=size)
        self.parent = parent
        self.username = username

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
        self.Bind(wx.EVT_BUTTON, lambda event: parent.show_frame(cur=self), self.disconnect)
        self.sizer.Add(self.disconnect, 0, wx.ALIGN_RIGHT | wx.BOTTOM)

        self.SetSizer(self.sizer)
        self.Layout()


    def open_dir_dialoge(self, event):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Logged in".encode())

        public_key_pem = client.recv(2048)
        public_key = serialization.load_pem_public_key(public_key_pem)

        data = self.username
        encrypted_data = Utilities.encrypt(data.encode(), public_key)

        client.sendall(encrypted_data)
        
        file_dialog = wx.FileDialog(self, "Select a file or folder")
        if file_dialog.ShowModal() != wx.ID_OK:
            return
        
        file_path = file_dialog.GetPath()
        file_name = file_path.split("\\")[-1]
        client.recv(1024)
        encrypted_data = Utilities.encrypt(file_name.encode(), public_key)
        client.sendall(encrypted_data)
        client.recv(1024)

        if self.is_txt(file_name):
            with open(file_path, "r") as file:
                lines = file.readlines()
                content = ""
                for line in lines:
                    content += line

                length = len(content) // 190 + 1
                client.send(str(length).encode())
                client.recv(1024)

                encrypted_file = b''
                for i in range(0, len(content), 190):
                    chunk = content[i: i + 190]
                    encrypted_file += Utilities.encrypt(chunk.encode(), public_key)

                client.sendall(encrypted_file)

        elif self.is_image(file_name):
            with open(file_path, "rb") as file:
                image_bytes = file.read()

                length = len(image_bytes) // 190 + 1
                client.send(str(length).encode())
                client.recv(1024)

                encrypted_image = b''
                for i in range(0, len(image_bytes), 190):
                    chunk = image_bytes[i:i + 190]
                    encrypted_image += Utilities.encrypt(chunk, public_key)

                client.sendall(encrypted_image)


    @staticmethod
    def is_image(file_name):
        return file_name.endswith("jpeg") or file_name.endswith("jpg") or file_name.endswith("png") or file_name.endswith("gif")
    

    @staticmethod
    def is_txt(file_name):
        return file_name.endswith("TXT") or file_name.endswith("txt") or file_name.endswith("py")


class DropTarget(wx.FileDropTarget):
    def __init__(self, window):
        super(DropTarget, self).__init__(self)
        self.window = window


        def OnDropFiles(self, x, y, filenames):
            for file in filenames:
                self.path += file

            return True
