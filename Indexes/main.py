import wx
from threading import Thread
from my_frame import MyFrame
from server import Server


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, title="Main Page", size=(900, 750))
        self.frame.Center()
        self.frame.Show()
        self.server = Server()
        client = Thread(target=Server.accept_client, args=(self.server.client_socket, ))

        return True
    

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()