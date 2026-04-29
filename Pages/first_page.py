import os
import wx
import wx.lib.buttons as buttons
from login_page import LoginPage
from register_page import RegisterPage


class FirstPage(wx.Panel):
    def __init__(self, parent, size):
        super(FirstPage, self).__init__(parent, size=size)
        color = wx.Colour(100, 100, 100, 1)

        self.bg_bitmap = wx.Bitmap(r"Assets\backgournd_image.jpg")
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, lambda e: self.on_paint(e))
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer.AddStretchSpacer(1)

        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.label = wx.StaticText(self, label="Welcome!")
        self.label.SetBackgroundColour(color)
        self.label.SetForegroundColour(wx.WHITE)
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.content_sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_list = {"Login Page": LoginPage, "Register Page": RegisterPage}
        
        for text, page in buttons_list.items():
            btn = buttons.GenButton(self, label=text, size=(120, 40))
            btn.SetBackgroundColour(color)
            btn.SetForegroundColour(wx.WHITE)
            btn.SetBezelWidth(0)
            btn.Bind(wx.EVT_BUTTON, lambda event, p=page: parent.show_frame(p, self))
            buttons_sizer.Add(btn, 0, wx.ALL, 15)

        self.content_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)

        if os.path.isfile('authToken.json'):
            btn = buttons.GenButton(self, label='User page', size=(120, 40))
            btn.SetBackgroundColour(color)
            btn.SetForegroundColour(wx.WHITE)
            btn.SetBezelWidth(0)
            btn.Bind(wx.EVT_BUTTON, lambda event: parent.show_user_frame(cur=self))
            self.content_sizer.Add(btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)        
        
        self.main_sizer.Add(self.content_sizer, 0, wx.ALIGN_CENTER)
        self.main_sizer.AddStretchSpacer(1)

        self.SetSizer(self.main_sizer)


    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self.bg_bitmap, 0, 0)
        
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            rect = self.content_sizer.GetChildren()[0].GetWindow().GetParent().GetSizer().GetItem(1).GetRect() #Gets the bounds of the container

            rect.Inflate(120, 150)
            
            gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0, 0, 0, 150))))
            gc.DrawRoundedRectangle(rect.x, rect.y, rect.width, rect.height, 15)
