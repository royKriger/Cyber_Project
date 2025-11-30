import wx
from socket import socket
import bcrypt
import base64
from utilities import Utilities
from cryptography.hazmat.primitives import serialization


class RegisterPage(wx.Panel):
    def __init__(self, parent, size):
        super(RegisterPage, self).__init__(parent, size=size)
        self.parent = parent
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
        self.show_password = wx.CheckBox(self, label="Show Password")
        self.Bind(wx.EVT_CHECKBOX, lambda event: self.check_helper(event), self.show_password)
        input_sizer.Add(self.show_password, 0, wx.UP | wx.RIGHT, 5)
        self.error3 = wx.StaticText(self)
        input_sizer.Add(self.error3, 0, wx.ALIGN_CENTER)
        self.error = wx.StaticText(self)
        input_sizer.Add(self.error, 0, wx.ALIGN_CENTER)

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sign = wx.Button(self, label="Sign In", size=(120, 40))
        self.home = wx.Button(self, label="Home Page", size=(120, 40))
        self.Bind(wx.EVT_BUTTON, lambda event: self.parent.show_frame(cur=self), self.home)
        self.Bind(wx.EVT_BUTTON, lambda event: self.on_sign_in(event), self.sign)
        buttons_sizer.Add(self.sign, 0, wx.ALL, 20)
        buttons_sizer.Add(self.home, 0, wx.ALL, 20)

        self.sizer.Add(input_sizer, 0, wx.ALIGN_CENTER, 50)
        self.sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER, 50)
        self.SetSizer(self.sizer)
        self.Layout()


    def on_sign_in(self, event):
        username = self.username.GetLineText(lineNo=0)
        email = self.email.GetLineText(lineNo=0)
        password = self.password.GetLineText(lineNo=0)

        flag = self.check_if_all_input_good(username, email, password)

        if flag:
            user = self.username.GetLineText(lineNo=0)
            email = self.email.GetLineText(lineNo=0)
            password = self.password.GetLineText(lineNo=0)

            client = socket()
            client.connect((Utilities.get_pc_ip(), 8200))
            client.send("register".encode())
            data = client.recv(1024).decode()
            print(data)
            public_key_pem = client.recv(2048)
            public_key = serialization.load_pem_public_key(public_key_pem)  

            secure_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            data = f"{user},{email},{base64.b64encode(secure_pass).decode()}"
            encrypted_data = Utilities.encrypt(data.encode(), public_key)

            client.sendall(encrypted_data)

            data = client.recv(1024).decode()
            if data == "200":
                print("Data input in database completed succesfully! ")
                self.username.SetLabel("")
                self.email.SetLabel("")
                self.password.SetLabel("")
                data = f"logged in,{email}"
                encrypted_data = Utilities.encrypt(data.encode(), public_key)
                client.sendall(encrypted_data)
                username = client.recv(1024).decode()
                self.parent.show_user_frame(self, username)

            elif data == "500":
                print("Operation was not succesful!")
                self.error.Label = data[3:]
                self.error.SetForegroundColour(wx.RED)
                self.Layout()
            client.close()


    def check_if_all_input_good(self, username, email, password):
        flag = Utilities.check_user_input(self, self.error1, username)
        flag = Utilities.check_email_input(self, self.error2, email) and flag
        flag = Utilities.check_password_input(self, self.error3, password) and flag
        username = self.username.GetLineText(lineNo=0)
        email = self.email.GetLineText(lineNo=0)
        password = self.password.GetLineText(lineNo=0)
        return flag


    def check_helper(self, event):
        self.password = Utilities.on_check(self, self.password, self.show_password)
