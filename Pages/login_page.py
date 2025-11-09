import wx
from socket import socket
from hashlib import sha1


class LoginPage(wx.Panel):
    def __init__(self, parent, size):
        super(LoginPage, self).__init__(parent, size=size)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self, label="Loginnnnnn!")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL, 20)

        input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.email = wx.TextCtrl(self, size=(250, 25))
        self.password = wx.TextCtrl(self, size=(250, 25), style=wx.TE_PASSWORD)
        input_sizer.Add(wx.StaticText(self, label="Email"), 0, wx.Left | wx.Right, 20)
        input_sizer.Add(self.email, 0, wx.Left | wx.Right, 20)
        input_sizer.Add(wx.StaticText(self, label="Password"), 0, wx.Left | wx.Right, 20)
        input_sizer.Add(self.password, 0, wx.Left | wx.Right, 20)

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        self.log = wx.Button(self, label="Log In", size=(120, 40))
        self.home = wx.Button(self, label="Home Page", size=(120, 40))
        self.Bind(wx.EVT_BUTTON, lambda event: parent.show_frame(cur=self), self.home)
        self.Bind(wx.EVT_BUTTON, self.on_log_in, self.log)
        buttons_sizer.Add(self.log, 0, wx.ALL, 20)
        buttons_sizer.Add(self.home, 0, wx.ALL, 20)

        self.sizer.Add(input_sizer, 0, wx.ALIGN_CENTER, 50)
        self.sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER, 50)
        self.SetSizer(self.sizer)
        self.Layout()


    def on_log_in(self, event):
        client = socket()
        client.connect(("192.168.1.206", 8200))
        client.send("login".encode())
        print(client.recv(1024).decode())

        email = self.email.GetLineText(lineNo=0)
        password = self.password.GetLineText(lineNo=0)
        password = sha1(password).hexdigest()

        data = f"{email},{password}"

        client.send(data.encode())

        data = client.recv(1024).decode()
        if data == "200":
            print("Data input in database completed succesfully! ")
        
        else:
            print("Try Again! ")
            self.sizer.Add(wx.StaticText(self, label="Try Again"), 0, wx.ALIGN_BOTTOM, 100)
        client.close()
