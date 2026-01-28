import wx
from my_frame import MyFrame


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, title="Main Page", size=(900, 750))
        self.frame.Centre(True)
        self.frame.Show()
        return True
    

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
