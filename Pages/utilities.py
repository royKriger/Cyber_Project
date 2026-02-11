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


# סיסמה חזקה, כולל תווים, אות קטנה, אות גדולה, תווים מיוחדים
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


    def on_check(parent, password_input : wx.TextCtrl, checkbox : wx.CheckBox):
        password = password_input.GetLineText(lineNo=0)
        input_sizer = password_input.GetContainingSizer()
        index = Utilities.get_item_index(input_sizer, password_input)

        if index == -1:
            return password_input

        input_sizer.Hide(index)
        input_sizer.Remove(index)
        password_input.Destroy()

        if checkbox.IsChecked():
            new_ctrl = wx.TextCtrl(parent, size=(250, 25), value=password)
        else:
            new_ctrl = wx.TextCtrl(parent, size=(250, 25), value=password, style=wx.TE_PASSWORD)
        
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


    def go_home(cur, parent, inputs):
        for input in inputs:
            input.SetLabel("")
        parent.show_frame(cur=cur)


    def remember_me(time):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Remember me".encode())
        client.recv(1024)
        with open('authToken.json', 'r') as file:
            tokens = json.load(file)
            if time == 'first':
                email, token = next(iter(tokens.items()))
            else:
                token = tokens[time]
        client.send(token.encode())
        username = client.recv(1024).decode()
        client.close()
        return username
    