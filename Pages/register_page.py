import wx
from socket import socket


class RegisterPage(wx.Panel):
    def __init__(self, parent, size):
        super(RegisterPage, self).__init__(parent, size=size)
        client = socket()
        client.connect(("192.168.2.68", 8200))

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self, label="Registerrrrr!")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL, 20)

        input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.username = wx.TextCtrl(self, value="Username", size=(250, 25))
        self.email = wx.TextCtrl(self, value="Email", size=(250, 25))
        self.password = wx.TextCtrl(self, value="Pass", size=(250, 25))
        input_sizer.Add(self.username, 0, wx.ALL, 20)
        input_sizer.Add(self.email, 0, wx.ALL, 20)
        input_sizer.Add(self.password, 0, wx.ALL, 20)

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sign = wx.Button(self, label="Sign In", size=(120, 40))
        self.home = wx.Button(self, label="Home Page", size=(120, 40))
        self.Bind(wx.EVT_BUTTON, lambda event: parent.show_frame(cur=self), self.home)
        self.Bind(wx.EVT_BUTTON, self.on_sign_in, self.sign)
        buttons_sizer.Add(self.sign, 0, wx.ALL, 20)
        buttons_sizer.Add(self.home, 0, wx.ALL, 20)

        self.sizer.Add(input_sizer, 0, wx.ALIGN_CENTER, 50)
        self.sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER, 50)
        self.SetSizer(self.sizer)
        self.Layout()


    def on_sign_in(self, event):
        client = socket()
        client.connect(("192.168.2.68", 8200))

        user = self.username.GetLineText(lineNo=0)
        email = self.email.GetLineText(lineNo=0)
        password = self.password.GetLineText(lineNo=0)
        
        data = f"{user},{email},{password}"

        client.send(data.encode())

        data = client.recv(1024).decode()
        if data == "200":
            print("Data input in database completed succesfully! ")
        
        else:
            print("Try Again! ")
            self.sizer.Add(wx.StaticText(self, label="Try Again"), 0, wx.ALIGN_BOTTOM, 100)
        client.close()
