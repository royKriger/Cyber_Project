import wx


class LoginPage(wx.Panel):
    def __init__(self, parent):
        super(LoginPage, self).__init__(parent, size=(900, 750))
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self, label="Loginnnnnn!")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL, 20)

        inputs = {"Email": 0, "Password": wx.TE_PASSWORD}
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        for name, style in inputs.items():
            text = wx.TextCtrl(self, value=name, size=(250, 25), style=style)
            input_sizer.Add(text, 0, wx.ALL, 20)

        buttons = ["Log In", "Home Page"]
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        for text in buttons:
            button = wx.Button(self, label=text, size=(120, 40))
            self.Bind(wx.EVT_BUTTON, lambda event, cur=self: parent.show_frame(cur=cur), button)
            buttons_sizer.Add(button, 0, wx.ALL, 30)

        self.sizer.Add(input_sizer, 0, wx.ALIGN_CENTER, 50)
        self.sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER, 50)
        self.SetSizer(self.sizer)
        self.Layout()
