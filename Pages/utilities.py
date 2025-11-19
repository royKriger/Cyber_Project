import wx
import re


class Utilities():
    def get_pc_path():
        return "192.168.1.228"
    

    def check_user_input(self, label, username):
        label.SetForegroundColour(wx.RED)
        if len(username) == 0:
            label.Label = "Enter a username! "
            self.Layout()
            return False
        label.Label = ""
        label.SetForegroundColour(wx.BLACK)
        self.Layout()
        return True


    def check_email_input(self, label, email):
        label.SetForegroundColour(wx.RED)
        if len(email) == 0:
            label.Label = "Enter an email! "
            self.Layout()
            return False
        elif re.search("[! @ # $ % ^ & *]", email[0:email.index('@')]) is not None:
            label.Label = "Email cannot contain special letters! "
            self.Layout()
            return False
        elif email.count('@') > 1:
            label.Label = "Email cannot contain more than one @! "
            self.Layout()
            return False
        elif "@gmail" not in email:
            label.Label = "Must inclue @gmail! "
            self.Layout()
            return False
        elif ".com" not in email:
            label.Label = "Must inclue .com! "
            self.Layout()
            return False
        label.Label = ""
        label.SetForegroundColour(wx.BLACK)
        self.Layout()
        return True


# סיסמה חזקה, כולל תווים, אות קטנה, אות גדולה, תווים מיוחדים
    def check_password_input(self, label, password):
        label.SetForegroundColour(wx.RED)
        if len(password) == 0:
            label.Label = "Enter a password! "
            self.Layout()
            return False
        if len(password) < 4:
            label.Label = "Password length too short! "
            self.Layout()
            return False
        elif re.search("[A-Z]", password) is None:
            label.Label = "Use an uppercase letter"
            self.Layout()
            return False
        elif re.search("[a-z]", password) is None:
            label.Label = "Use a lowercase letter"
            self.Layout()
            return False
        elif re.search("[0-9]", password) is None:
            label.Label = "Use a number"
            self.Layout()
            return False
        elif re.search("[! @ # $ % ^ & *]", password) is None:
            label.Label = "Use a special letter"
            self.Layout()
            return False
        label.Label = ""
        label.SetForegroundColour(wx.BLACK)
        self.Layout()
        return True


    def on_check(self, password_input, checkbox):
        password = password_input.GetLineText(lineNo=0)
        input_sizer = password_input.GetContainingSizer()
        index = input_sizer.GetItemIndex(self.password)

        input_sizer.Hide(index)
        input_sizer.Remove(index)
        password_input.Destroy()

        if checkbox.IsChecked():
            password_input = wx.TextCtrl(self, size=(250, 25))
        else:
            password_input = wx.TextCtrl(self, size=(250, 25), style=wx.TE_PASSWORD)

        password_input.SetValue = password
        
        input_sizer.Insert(index, password_input, 0, wx.Left | wx.Right, 20)

        self.Layout()
