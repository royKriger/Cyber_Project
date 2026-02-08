import os
import wx
import socket
from user_page import UserPage
from utilities import Utilities
from first_page import FirstPage
from login_page import LoginPage
from register_page import RegisterPage


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
            cur.SetBackgroundColour(wx.Colour(245, 245, 246))
            cur.Hide()
            self.pages[F] = cur
        
        if os.path.isfile('authToken.txt'):
            client = socket.socket()
            client.connect((Utilities.get_pc_ip(), 8200))
            client.send("Remember me".encode())
            client.recv(1024)
            with open('authToken.txt', 'r') as file:
                token = file.read()
            client.send(token.encode())
            username = client.recv(1024).decode()
            self.show_user_frame(username)
            client.close()
        else:
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


    def show_user_frame(self, username, cur=None):
        frame = UserPage(self, self.size, username)
        self.sizer.Add(frame, proportion=1, flag=wx.EXPAND | wx.ALL)
        frame.SetBackgroundColour(wx.Colour(245, 245, 246))
        self.pages[frame] = frame
        if cur != None:
            cur.Hide()
        frame.Show(True)
        self.Layout()
        self.Refresh()
