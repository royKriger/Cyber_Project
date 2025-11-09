import wx
from socket import socket
from hashlib import sha1


class RegisterPage(wx.Panel):
    def __init__(self, parent, size):
        super(RegisterPage, self).__init__(parent, size=size)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self, label="Registerrrrr!")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL, 20)

        input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.username = wx.TextCtrl(self, size=(250, 25))
        self.email = wx.TextCtrl(self, size=(250, 25))
        self.password = wx.TextCtrl(self, size=(250, 25), style=wx.TE_PASSWORD)
        input_sizer.Add(wx.StaticText(self, label="Username"), 0, wx.Left | wx.Right, 20)
        input_sizer.Add(self.username, 0, wx.Left | wx.Right, 20)
        self.error1 = wx.StaticText(self)
        input_sizer.Add(self.error1, 0, wx.ALIGN_CENTER)
        input_sizer.Add(wx.StaticText(self, label="Email"), 0, wx.Left | wx.Right, 20)
        input_sizer.Add(self.email, 0, wx.Left | wx.Right, 20)
        self.error2 = wx.StaticText(self)
        input_sizer.Add(self.error2, 0, wx.ALIGN_CENTER)
        input_sizer.Add(wx.StaticText(self, label="Password"), 0, wx.Left | wx.Right, 20)
        input_sizer.Add(self.password, 0, wx.Left | wx.Right, 20)
        self.error3 = wx.StaticText(self)
        input_sizer.Add(self.error3, 0, wx.ALIGN_CENTER)
        self.error = wx.StaticText(self)
        input_sizer.Add(self.error, 0, wx.ALIGN_CENTER)

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sign = wx.Button(self, label="Sign In", size=(120, 40))
        self.home = wx.Button(self, label="Home Page", size=(120, 40))
        self.Bind(wx.EVT_BUTTON, lambda event: parent.show_frame(cur=self), self.home)
        self.Bind(wx.EVT_BUTTON, lambda event, x=parent: self.on_sign_in(event, parent=x), self.sign)
        buttons_sizer.Add(self.sign, 0, wx.ALL, 20)
        buttons_sizer.Add(self.home, 0, wx.ALL, 20)

        self.sizer.Add(input_sizer, 0, wx.ALIGN_CENTER, 50)
        self.sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER, 50)
        self.SetSizer(self.sizer)
        self.Layout()


    def on_sign_in(self, event, parent):
        client = socket()
        client.connect(("192.168.1.206", 8200))
        client.send("register".encode())
        print(client.recv(1024).decode())

        user = self.username.GetLineText(lineNo=0)
        email = self.email.GetLineText(lineNo=0)
        password = self.password.GetLineText(lineNo=0)
        password = sha1(password.encode()).hexdigest()

        data = f"{user},{email},{password}"

        client.send(data.encode())

        data = client.recv(1024).decode()
        if data == "200":
            print("Data input in database completed succesfully! ")
            self.username.SetLabel("")
            self.email.SetLabel("")
            self.password.SetLabel("")
            parent.show_frame(cur=self)

        elif data == "500":
            print("Operation was not succesful!")
            self.error.Label = "Try Again! "
            self.error.SetForegroundColour(wx.RED)
            self.Layout()
        client.close()
