import wx
from socket import socket
from utilities import Utilities


class LoginPage(wx.Panel):
    def __init__(self, parent, size):
        super(LoginPage, self).__init__(parent, size=size)
        self.parent = parent
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
        self.error1 = wx.StaticText(self)
        input_sizer.Add(self.error1, 0, wx.ALIGN_CENTER)
        input_sizer.Add(wx.StaticText(self, label="Password"), 0, wx.Left | wx.Right, 20)
        input_sizer.Add(self.password, 0, wx.Left | wx.Right, 20)
        self.show_password = wx.CheckBox(self, label="Show Password")
        self.Bind(wx.EVT_CHECKBOX,lambda event: Utilities.on_check(self.password, self.show_password), self.show_password)
        input_sizer.Add(self.show_password, 0, wx.UP | wx.RIGHT, 5)
        self.error2 = wx.StaticText(self)
        input_sizer.Add(self.error2, 0, wx.ALIGN_CENTER)
        self.error = wx.StaticText(self)
        input_sizer.Add(self.error, 0, wx.ALIGN_CENTER)

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        self.log = wx.Button(self, label="Log In", size=(120, 40))
        self.home = wx.Button(self, label="Home Page", size=(120, 40))
        self.Bind(wx.EVT_BUTTON, lambda event: self.parent.show_frame(cur=self), self.home)
        self.Bind(wx.EVT_BUTTON, lambda event: self.on_log_in(event), self.log)
        buttons_sizer.Add(self.log, 0, wx.ALL, 20)
        buttons_sizer.Add(self.home, 0, wx.ALL, 20)

        self.sizer.Add(input_sizer, 0, wx.ALIGN_CENTER, 50)
        self.sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER, 50)
        self.SetSizer(self.sizer)
        self.Layout()


    def on_log_in(self, event):
        email = self.email.GetLineText(lineNo=0)
        password = self.password.GetLineText(lineNo=0)

        flag = self.check_if_all_input_good(email, password)

        if flag:
            client = socket()
            client.connect((Utilities.get_pc_ip(), 8200))
            client.send("login".encode())
            print(client.recv(1024).decode())

            email = self.email.GetLineText(lineNo=0)
            password = self.password.GetLineText(lineNo=0)

            data = f"{email},{password}"

            client.send(data.encode())

            data = client.recv(1024).decode()
            print(data)
            if data == "200":
                print("Login completed succesfully! ")
                self.email.SetLabel("")
                self.password.SetLabel("")
                """
                self.error.Label = "You're logged in! "
                self.error.SetForegroundColour(wx.GREEN)
                self.Layout()
                """
                client.send(f"logged in,{email}".encode())
                username = client.recv(1024).decode()
                self.parent.show_user_frame(self, username)

            else:
                self.error.Label = "Try Again! "
                self.error.SetForegroundColour(wx.RED)
                self.Layout()

            client.close()


    def check_if_all_input_good(self, email, password):
        flag = Utilities.check_email_input(self, self.error1, email)
        flag = Utilities.check_password_input(self, self.error2, password) and flag
        email = self.email.GetLineText(lineNo=0)
        password = self.password.GetLineText(lineNo=0)
        return flag