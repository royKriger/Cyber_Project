import os
import wx
import wx.lib.buttons as buttons
from login_page import LoginPage
from register_page import RegisterPage


class FirstPage(wx.Panel):
    def __init__(self, parent, size):
        super(FirstPage, self).__init__(parent, size=size)
        color = wx.Colour(100, 100, 100, 1)

        self.bg_bitmap = wx.Bitmap(r"Assets\background_image.jpg")
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, lambda e: self.on_paint(e, self.content_sizer))
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer.AddStretchSpacer(1)

        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.label = wx.StaticText(self, label="Welcome!")
        self.label.SetForegroundColour(wx.WHITE)
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.content_sizer.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 40)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_list = {"Login Page": LoginPage, "Register Page": RegisterPage}
        
        for text, page in buttons_list.items():
            btn = buttons.GenButton(self, label=text, size=(120, 40))
            btn.SetBackgroundColour(color)
            btn.SetForegroundColour(wx.WHITE)
            btn.SetBezelWidth(0)
            btn.Bind(wx.EVT_BUTTON, lambda event, p=page: parent.show_frame(p, self))
            buttons_sizer.Add(btn, 0, wx.ALL, 40)

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
