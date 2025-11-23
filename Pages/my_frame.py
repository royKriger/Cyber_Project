import wx
from first_page import FirstPage
from login_page import LoginPage
from register_page import RegisterPage
from user_page import UserPage


class MyFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE,
                 name="Main Page"):
        super(MyFrame, self).__init__(parent, id, title,
                                      pos, size, style, name)
        self.size = size

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.pages = {}

        for F in (FirstPage, LoginPage, RegisterPage):
            cur = F(self, size)
            self.sizer.Add(cur, proportion=1, flag=wx.EXPAND | wx.ALL)
            cur.Hide()
            self.pages[F] = cur

        self.show_frame()

        self.SetSizer(self.sizer)
        
        self.Layout()


    def show_frame(self, page=FirstPage, cur=None):
        frame = self.pages[page]
        if cur != None:
            cur.Hide()
        frame.Show(True)
        self.Layout()
        self.Refresh()


    def show_user_frame(self, cur, username):
        frame = UserPage(self, self.size, username)
        self.pages[frame] = frame
        cur.Hide()
        frame.Show(True)
        self.Layout()
        self.Refresh()
