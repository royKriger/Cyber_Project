import wx
from login_page import LoginPage
from register_page import RegisterPage


class FirstPage(wx.Panel):
    def __init__(self, parent, size):
        super(FirstPage, self).__init__(parent, size=size)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.admin = wx.Button(self, label="User Page", size=(100, 60))
        self.Bind(wx.EVT_BUTTON, lambda event: parent.show_user_frame(self, "Admin"), self.admin)
        self.sizer.Add(self.admin, 0, wx.ALIGN_LEFT, 5)
        #self.admin.Hide()

        self.label = wx.StaticText(self, label="Welcome!")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL, 20)

        buttons = {
            "Login Page": LoginPage,
            "Register Page": RegisterPage
        }
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for text, page in buttons.items():
            button = wx.Button(self, label=text, name=text, size=(120, 40))
            self.Bind(wx.EVT_BUTTON, lambda event, var=page, cur=self: parent.show_frame(var, cur), button)
            buttons_sizer.Add(button, 0, wx.ALL, 100)
        
        self.sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER)
        self.SetSizer(self.sizer)
        self.Layout()
