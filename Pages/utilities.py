import wx
import re


class Utilities():
    def get_pc_path():
        return "192.168.2.64"
    

    def check_email_input(self, label, email):
        if len(email) == 0:
            label.Label = "Enter an email! "
            label.SetForegroundColour(wx.RED)
            label.Layout()
            return False
        elif "@gmail" not in email:
            label.Label = "Must inclue @gmail! "
            label.SetForegroundColour(wx.RED)
            label.Layout()
            return False
        elif ".com" not in email:
            label.Label = "Must inclue .com! "
            label.SetForegroundColour(wx.RED)
            label.Layout()
            return False
        label.Label = ""
        label.Layout()
        return True


# סיסמה חזקה, כולל תווים, אות קטנה, אות גדולה, תווים מיוחדים
    def check_password_input(self, label, password):
        if len(password) < 4:
            label.Label = "Password length too short! "
            label.SetForegroundColour(wx.RED)
            label.Layout()
            return False
        elif re.search("[A-Z]", password) is None:
            label.Label = "Use an uppercase letter"
            label.SetForegroundColour(wx.RED)
            label.Layout()
            return False
        elif re.search("[a-z]", password) is None:
            label.Label = "Use a lowercase letter"
            label.SetForegroundColour(wx.RED)
            label.Layout()
            return False
        elif re.search("[0-9]", password) is None:
            label.Label = "Use a number"
            label.SetForegroundColour(wx.RED)
            label.Layout()
            return False
        elif re.search("[! @ # $ % ^ & *]", password) is None:
            label.Label = "Use a special letter"
            label.SetForegroundColour(wx.RED)
            label.Layout()
            return False
        label.Label = ""
        label.Layout()
        return True
