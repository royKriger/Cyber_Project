import os
import wx
from utilities import Utilities
from login_page import LoginPage
from register_page import RegisterPage


class FirstPage(wx.Panel):
    def __init__(self, parent, size, username=''):
        super(FirstPage, self).__init__(parent, size=size)
        self.PURPLE_DARK = wx.Colour(40,  20,  70,  255)   # deep card bg
        self.PURPLE_MID = wx.Colour(80,  40, 130,  200)   # input bg (semi-transparent feel via label bg)
        self.PURPLE_LIGHT = wx.Colour(160, 100, 220, 255)   # accent / highlights
        self.TEXT_WHITE = wx.Colour(230, 220, 255, 255)   # soft lavender-white text
        self.TEXT_DIM = wx.Colour(160, 140, 200, 255)   # dimmed label text
        self.ERROR_COLOR = wx.Colour(255, 100, 120, 255)   # red-pink errors
        self.TRANSPARENT_PANEL = wx.Colour(30, 15, 60, 180)  # dark overlay

        self.bg_bitmap = wx.Bitmap(r"Assets\background_image.jpg")
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, lambda e: self.on_paint(e, self.content_sizer))
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.AddStretchSpacer(1)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.label = wx.StaticText(self, label="Welcome!")
        font_title = wx.Font(32, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label.SetFont(font_title)
        self.label.SetForegroundColour(self.TEXT_WHITE)
        self.label.SetBackgroundColour(wx.Colour(0, 0, 0, 0))   # fully transparent
        self.content_sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.login = Utilities.make_button(self, "Login Page", self.TEXT_WHITE)
        self.register = Utilities.make_button(self, "Register Page", self.TEXT_WHITE)

        self.Bind(wx.EVT_BUTTON, lambda event, p=LoginPage: parent.show_frame(p, self), self.login)
        self.Bind(wx.EVT_BUTTON, lambda event, p=RegisterPage: parent.show_frame(p, self), self.register)

        for btn in (self.login, self.register):
            btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=btn: b.SetBackgroundColour(wx.Colour(130, 70, 210)))
            btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=btn: b.SetBackgroundColour(wx.Colour(100, 50, 170)))

        buttons_sizer.Add(self.login,  0, wx.ALIGN_CENTER | wx.ALL, 8)
        buttons_sizer.Add(self.register, 0, wx.ALIGN_CENTER | wx.ALL, 8)

        if os.path.isfile('authToken.json'):
            self.user = Utilities.make_button(self, "User Page", self.TEXT_WHITE)
            self.user.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=self.user: b.SetBackgroundColour(wx.Colour(130, 70, 210)))
            self.user.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=self.user: self.user.SetBackgroundColour(wx.Colour(100, 50, 170)))
            buttons_sizer.Add(self.user, 0, wx.ALIGN_CENTER | wx.ALL, 8)
            self.user.Bind(wx.EVT_BUTTON, lambda event: parent.show_user_frame(username, cur=self))
               
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
        for item in item.GetChildren():
            item_rect = item.GetRect()
            
            if full_rect.IsEmpty():
                full_rect = item_rect
            else:
                full_rect.Union(item_rect)

        self.make_opacity_less(dc, full_rect, size=(100, 120))


    def make_opacity_less(self, dc, full_rect, size=(0, 0)):
        gc = wx.GraphicsContext.Create(dc)
        if size == (0, 0):
            full_rect = full_rect.GetRect() #Gets the bounds of the container

        if gc:
            full_rect.Inflate(size)

            gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0, 0, 0, 150))))
            gc.DrawRoundedRectangle(full_rect.x, full_rect.y, full_rect.width, full_rect.height, 15)
