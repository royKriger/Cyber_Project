import wx
import re
import json
import socket
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class Utilities():
    def get_pc_ip():
        return "localhost"

    def check_user_input(parent, label : wx.StaticText, username):
        label.SetForegroundColour(wx.RED)
        if len(username) == 0:
            label.Label = "Enter a username! "
            parent.Layout()
            return False
        label.Label = ""
        label.SetForegroundColour(wx.BLACK)
        parent.Layout()
        return True


    def check_email_input(parent, label : wx.StaticText, email):
        label.SetForegroundColour(wx.RED)
        if len(email) == 0:
            label.Label = "Enter an email! "
            parent.Layout()
            return False
        elif "@gmail" not in email:
            label.Label = "Must inclue @gmail! "
            parent.Layout()
            return False
        elif re.search("[! @ # $ % ^ & *]", email[0:email.index('@')]) is not None:
            label.Label = "Email cannot contain special letters! "
            parent.Layout()
            return False
        elif email.count('@') > 1:
            label.Label = "Email cannot contain more than one @! "
            parent.Layout()
            return False
        elif ".com" not in email:
            label.Label = "Must inclue .com! "
            parent.Layout()
            return False
        label.Label = ""
        label.SetForegroundColour(wx.BLACK)
        parent.Layout()
        return True


    def check_password_input(parent, label : wx.StaticText, password):
        label.SetForegroundColour(wx.RED)
        if len(password) == 0:
            label.Label = "Enter a password! "
            parent.Layout()
            return False
        if len(password) < 4:
            label.Label = "Password length too short! "
            parent.Layout()
            return False
        elif re.search("[A-Z]", password) is None:
            label.Label = "Use an uppercase letter"
            parent.Layout()
            return False
        elif re.search("[a-z]", password) is None:
            label.Label = "Use a lowercase letter"
            parent.Layout()
            return False
        elif re.search("[0-9]", password) is None:
            label.Label = "Use a number"
            parent.Layout()
            return False
        elif re.search("[! @ # $ % ^ & *]", password) is None:
            label.Label = "Use a special letter"
            parent.Layout()
            return False
        label.Label = ""
        label.SetForegroundColour(wx.BLACK)
        parent.Layout()
        return True
    

    def check_if_all_input_good(parent, inputs, errors):
        functions = [Utilities.check_email_input, Utilities.check_password_input, Utilities.check_user_input]
        flag = True
        for i in range(len(inputs)):
            flag = functions[i](parent, errors[i], inputs[i]) and flag

        return flag


    def make_label(window, text, color):
        lbl = wx.StaticText(window, label=text)
        font_label = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        lbl.SetFont(font_label)
        lbl.SetForegroundColour(color)
        lbl.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        return lbl


    def make_input(window, color, password=False, value=''):
        style = wx.TE_PASSWORD if password else 0
        ctrl = wx.TextCtrl(window, size=(260, 30), style=style | wx.BORDER_NONE)
        font_input = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        ctrl.SetFont(font_input)
        ctrl.SetForegroundColour(color)
        ctrl.SetBackgroundColour(wx.Colour(60, 30, 100))   # dark purple input bg
        if value != '':
            ctrl.SetValue(value)
        return ctrl


    def make_error(window, color):
        err = wx.StaticText(window)
        font_error = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD)
        err.SetFont(font_error)
        err.SetForegroundColour(color)
        err.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        return err


    def make_button(window, label, color):
        btn = wx.Button(window, label=label, size=(160, 38), style=wx.BORDER_NONE)
        btn.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        btn.SetForegroundColour(color)
        btn.SetBackgroundColour(wx.Colour(100, 50, 170))
        return btn


    def on_check(parent, color, password_input : wx.TextCtrl, checkbox : wx.CheckBox):
        password = password_input.GetLineText(lineNo=0)
        input_sizer = password_input.GetContainingSizer()
        index = Utilities.get_item_index(input_sizer, password_input)

        if index == -1:
            return password_input

        input_sizer.Hide(index)
        input_sizer.Remove(index)
        password_input.Destroy()

        if checkbox.IsChecked():
            new_ctrl = Utilities.make_input(parent, color, password=False, value=password)
        else:
            new_ctrl = Utilities.make_input(parent, color, password=True, value=password)
        
        input_sizer.Insert(index, new_ctrl, 0, wx.Left | wx.Right, 20)

        parent.Layout()

        return new_ctrl


    def get_item_index(sizer : wx.BoxSizer, window):
        for i in range(sizer.GetItemCount()):
            item = sizer.GetItem(i)
            if item and item.GetWindow() is window:
                return i
        return -1


    def encrypt(message: bytes, key) -> bytes:
        encrypted_message = key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return encrypted_message


    def go_home(cur, parent, inputs, errors):
        for input in inputs:
            input.SetLabel('')
        for error in errors:
            error.SetLabel('')
        parent.show_frame(cur=cur)


    def remember_me(time):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Remember me".encode())
        client.recv(1024)
        with open('authToken.json', 'r') as file:
            tokens = json.load(file)
            if time == 'first':
                _, token = next(iter(tokens.items()))
            else:
                token = tokens[time]
        client.send(token.encode())
        username = client.recv(1024).decode()
        client.close()
        return username
    