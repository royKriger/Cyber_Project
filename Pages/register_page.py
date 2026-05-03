import wx
import os
import json
import bcrypt
from socket import socket
from utilities import Utilities
from cryptography.hazmat.primitives import serialization


class RegisterPage(wx.Panel):
    def __init__(self, parent, size):
        super(RegisterPage, self).__init__(parent, size=size)
        self.parent = parent

        self.PURPLE_DARK = wx.Colour(40,  20,  70,  255)
        self.PURPLE_MID = wx.Colour(80,  40, 130,  200)
        self.PURPLE_LIGHT = wx.Colour(160, 100, 220, 255)
        self.TEXT_WHITE = wx.Colour(230, 220, 255, 255)
        self.TEXT_DIM = wx.Colour(160, 140, 200, 255)
        self.ERROR_COLOR = wx.Colour(255, 100, 120, 255)
        self.TRANSPARENT_PANEL = wx.Colour(30, 15, 60, 180)
        
        self.bg_bitmap = wx.Bitmap(r"Assets\background_image.jpg")
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, lambda e: self.on_paint(e, self.content_sizer))
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.AddStretchSpacer(1)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.label = wx.StaticText(self, label="Registerrrrr!")
        font_title = wx.Font(32, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label.SetFont(font_title)
        self.label.SetForegroundColour(self.TEXT_WHITE)
        self.label.SetBackgroundColour(wx.Colour(0, 0, 0, 0))   # fully transparent
        self.content_sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)

        input_sizer = wx.BoxSizer(wx.VERTICAL)

        input_sizer.Add(Utilities.make_label(self, "Username", self.TEXT_DIM), 0, wx.LEFT, 5)
        self.username = Utilities.make_input(self, self.TEXT_WHITE)
        input_sizer.Add(self.username, 0, wx.EXPAND | wx.BOTTOM, 2)
        self.error1 = Utilities.make_error(self, self.ERROR_COLOR)
        input_sizer.Add(self.error1, 0, wx.LEFT | wx.BOTTOM, 4)

        input_sizer.Add(Utilities.make_label(self, "Email", self.TEXT_DIM), 0, wx.LEFT, 5)
        self.email = Utilities.make_input(self, self.TEXT_WHITE)
        input_sizer.Add(self.email, 0, wx.EXPAND | wx.BOTTOM, 2)
        self.error2 = Utilities.make_error(self, self.ERROR_COLOR)
        input_sizer.Add(self.error2, 0, wx.LEFT | wx.BOTTOM, 4)

        input_sizer.Add(Utilities.make_label(self, "Password", self.TEXT_DIM), 0, wx.LEFT, 5)
        self.password = Utilities.make_input(self, self.TEXT_WHITE, password=True)
        input_sizer.Add(self.password, 0, wx.EXPAND | wx.BOTTOM, 2)
        self.error3 = Utilities.make_error(self, self.ERROR_COLOR)
        input_sizer.Add(self.error3, 0, wx.LEFT | wx.BOTTOM, 4)

        self.inputs = [self.email, self.password, self.username]

        font_check = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        self.show_password = wx.CheckBox(self, label="Show Password")
        self.show_password.SetFont(font_check)
        self.show_password.SetForegroundColour(self.TEXT_DIM)
        self.show_password.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        self.Bind(wx.EVT_CHECKBOX, lambda event: self.check_helper(event), self.show_password)
        input_sizer.Add(self.show_password, 0, wx.LEFT | wx.TOP, 4)

        self.remember_me = wx.CheckBox(self, label="Remember Me")
        self.remember_me.SetFont(font_check)
        self.remember_me.SetForegroundColour(self.TEXT_DIM)
        self.remember_me.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        input_sizer.Add(self.remember_me, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 4)
        
        self.error = Utilities.make_error(self, self.ERROR_COLOR)
        input_sizer.Add(self.error, 0, wx.ALIGN_CENTER | wx.BOTTOM, 6)

        self.errors = [self.error2, self.error3, self.error1, self.error]

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)

        def make_button(label):
            btn = wx.Button(self, label=label, size=(160, 38), style=wx.BORDER_NONE)
            btn.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            btn.SetForegroundColour(self.TEXT_WHITE)
            btn.SetBackgroundColour(wx.Colour(100, 50, 170))   # vivid purple button
            return btn

        self.log  = make_button("Sign Up")
        self.home = make_button("Home Page")

        self.Bind(wx.EVT_BUTTON, lambda e: Utilities.go_home(self, self.parent, self.inputs, self.errors), self.home)
        self.Bind(wx.EVT_BUTTON, self.on_sign_in, self.log)

        for btn in (self.log, self.home):
            btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=btn: b.SetBackgroundColour(wx.Colour(130, 70, 210)))
            btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=btn: b.SetBackgroundColour(wx.Colour(100, 50, 170)))

        buttons_sizer.Add(self.log,  0, wx.ALIGN_CENTER | wx.ALL, 8)
        buttons_sizer.Add(self.home, 0, wx.ALIGN_CENTER | wx.ALL, 8)

        self.content_sizer.Add(input_sizer,   0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 40)
        self.content_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER)

        self.main_sizer.Add(self.content_sizer, 0, wx.ALIGN_CENTER)
        self.main_sizer.AddStretchSpacer(1)

        self.SetSizer(self.main_sizer)
        self.Layout()


    def on_paint(self, event, item):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self.bg_bitmap, 0, 0)

        full_rect = wx.Rect()
        for child in item.GetChildren():
            r = child.GetRect()
            if full_rect.IsEmpty():
                full_rect = r
            else:
                full_rect.Union(r)

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            full_rect.Inflate(30, 20)

            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(wx.Colour(160, 80, 255, 60)).Width(6)))
            gc.DrawRoundedRectangle(full_rect.x - 3, full_rect.y - 3, full_rect.width + 6, full_rect.height + 6, 18)

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(25, 10, 55, 195))))
            gc.DrawRoundedRectangle(full_rect.x, full_rect.y, full_rect.width, full_rect.height, 15)


    def on_sign_in(self, event):
        username = self.username.GetLineText(lineNo=0)
        email = self.email.GetLineText(lineNo=0)
        password = self.password.GetLineText(lineNo=0)

        flag = Utilities.check_if_all_input_good(self, [email, password, username], self.errors)

        if not flag:
            return
        
        client = socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Sign up".encode())
        client.recv(1024)
        client.send("register".encode())
        print(client.recv(1024).decode())
        public_key_pem = client.recv(2048)
        public_key = serialization.load_pem_public_key(public_key_pem)  

        secure_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        data = f"{username},{email},{secure_pass.decode()}"
        if self.remember_me.IsChecked():
            data += ',remember'
        encrypted_data = Utilities.encrypt(data.encode(), public_key)
        client.sendall(encrypted_data)

        data = client.recv(1024).decode()
        if data.startswith('200'):
            print("Data input in database completed succesfully! ")
            self.username.SetLabel("")
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

            self.parent.show_user_frame(username ,self)

        else:
            print("Operation was not succesful!")
            self.error.Label = data.split("|")[-1]
            self.error.SetForegroundColour(wx.RED)
            self.Layout()
        client.close()


    def check_helper(self, event):
        index = self.inputs.index(self.password)
        self.password = Utilities.on_check(self, self.TEXT_WHITE, self.password, self.show_password)
        self.inputs[index] = self.password
