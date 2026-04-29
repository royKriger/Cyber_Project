import wx
import os
import json
from socket import socket
from utilities import Utilities
from cryptography.hazmat.primitives import serialization


class LoginPage(wx.Panel):
    def __init__(self, parent, size):
        super(LoginPage, self).__init__(parent, size=size)
        self.color = wx.Colour(110, 110, 110, 1)
        self.error_color = wx.Colour(175, 175, 175, 1)
        self.parent = parent

        self.bg_bitmap = wx.Bitmap(r"Assets\backgournd_image.jpg")
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, lambda e: self.on_paint(e))
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.main_sizer.AddStretchSpacer(1)

        self.content_sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self, label="Loginnnnnn!")
        self.label.SetBackgroundColour(self.color)
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.content_sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL, 20)

        self.inputs = []
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.email = wx.TextCtrl(self, size=(250, 25))
        self.password = wx.TextCtrl(self, size=(250, 25), style=wx.TE_PASSWORD)
        self.inputs.append(self.email)
        self.inputs.append(self.password)

        email_label = wx.StaticText(self, label="Email")
        input_sizer.Add(email_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.Left | wx.Right, 20)
        email_label.SetBackgroundColour(self.color)

        input_sizer.Add(self.email, 0, wx.Left | wx.Right, 20)
        self.error1 = wx.StaticText(self)
        self.error1.SetBackgroundColour(self.error_color)
        self.inputs.append(self.error1)
        input_sizer.Add(self.error1, 0, wx.ALIGN_CENTER)
        
        password_label = wx.StaticText(self, label="Password")
        input_sizer.Add(password_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.Left | wx.Right, 20)
        password_label.SetBackgroundColour(self.color)

        input_sizer.Add(self.password, 0, wx.Left | wx.Right, 20)
        self.error2 = wx.StaticText(self)
        self.error2.SetBackgroundColour(self.error_color)
        self.inputs.append(self.error2)
        input_sizer.Add(self.error2, 0, wx.ALIGN_CENTER)

        self.show_password = wx.CheckBox(self, label="Show Password")
        self.show_password.SetBackgroundColour(self.color)
        self.Bind(wx.EVT_CHECKBOX, lambda event: self.check_helper(event), self.show_password)
        input_sizer.Add(self.show_password, 0, wx.UP | wx.RIGHT, 5)

        self.remember_me = wx.CheckBox(self, label="Remember Me")
        self.remember_me.SetBackgroundColour(self.color)
        input_sizer.Add(self.remember_me, 0, wx.UP | wx.RIGHT, 5)
        
        self.error = wx.StaticText(self)
        self.error.SetBackgroundColour(self.error_color)
        self.inputs.append(self.error)
        input_sizer.Add(self.error, 0, wx.ALIGN_CENTER)

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        self.log = wx.Button(self, label="Log In", size=(120, 40))
        self.home = wx.Button(self, label="Home Page", size=(120, 40))
        self.Bind(wx.EVT_BUTTON, lambda event: Utilities.go_home(self, self.parent, self.inputs), self.home)
        self.Bind(wx.EVT_BUTTON, self.on_log_in, self.log)
        buttons_sizer.Add(self.log, 0, wx.ALL, 20)
        buttons_sizer.Add(self.home, 0, wx.ALL, 20)

        self.content_sizer.Add(input_sizer, 0, wx.ALIGN_CENTER, 50)
        self.content_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER, 50)

        self.main_sizer.Add(self.content_sizer, 0, wx.ALIGN_CENTER)
        self.main_sizer.AddStretchSpacer(1)

        self.SetSizer(self.main_sizer)        
        self.Layout()


    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self.bg_bitmap, 0, 0)
        
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            rect = self.content_sizer.GetChildren()[0].GetWindow().GetParent().GetSizer().GetItem(1).GetRect() #Gets the bounds of the container

            rect.Inflate(140, 100)
            
            gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0, 0, 0, 150))))
            gc.DrawRoundedRectangle(rect.x, rect.y, rect.width, rect.height, 15)


    def on_log_in(self, e):
        email = self.email.GetLineText(lineNo=0)
        password = self.password.GetLineText(lineNo=0)

        flag = self.check_if_all_input_good(email, password)

        if flag:
            client = socket()
            client.connect((Utilities.get_pc_ip(), 8200))
            client.send("Log in".encode())
            client.recv(1024)
            client.send("login".encode())
            print(client.recv(1024).decode())
            public_key_pem = client.recv(2048)
            public_key = serialization.load_pem_public_key(public_key_pem)

            data = f"{email},{password}"
            if self.remember_me.IsChecked():
                data += ',remember'
            encrypted_data = Utilities.encrypt(data.encode(), public_key)

            client.sendall(encrypted_data)

            data = client.recv(1024).decode()
            if data.startswith('200'):
                print("Login completed succesfully! ")
                self.email.SetLabel("")
                self.password.SetLabel("")
                if len(data.split('|')) > 1:
                    exists = os.path.isfile('authToken.json')
                    json_dump = {}
                    if exists:
                        with open('authToken.json', 'r') as file:
                            json_dump = json.load(file)
                            
                    with open('authToken.json', 'w') as file:
                        json_dump[email] = data.split("|")[-1]
                        json.dump(json_dump, file)
                        
                data = f"logged in,{email}"
                encrypted_data = Utilities.encrypt(data.encode(), public_key)
                client.sendall(encrypted_data)
                username = client.recv(1024).decode()
                for input in self.inputs:
                    input.SetLabel("")

                self.parent.show_user_frame(username, self)

            else:
                print("Operation was not succesful!")
                self.error.Label = data.split("|")[-1]
                self.error.SetForegroundColour(wx.RED)
                self.Layout()

            client.close()


    def check_if_all_input_good(self, email, password):
        flag = Utilities.check_email_input(self, self.error1, email)
        flag = Utilities.check_password_input(self, self.error2, password) and flag
        return flag
    
    
    def check_helper(self, event):
        index = self.inputs.index(self.password)
        self.password = Utilities.on_check(self, self.password, self.show_password)
        self.inputs[index] = self.password
        