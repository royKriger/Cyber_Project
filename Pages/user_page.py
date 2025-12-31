import wx
import os
import socket
from utilities import Utilities
from cryptography.hazmat.primitives import serialization


class UserPage(wx.Panel):
    def __init__(self, parent : wx.Window, size, username : str):
        super(UserPage, self).__init__(parent, size=size)
        self.parent = parent
        self.username = username

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.timer = wx.Timer(self)

        left_sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        
        icon_path = r"Pages\Assets\Logo.png"
        img = wx.Image(icon_path, wx.BITMAP_TYPE_ANY)
        img = img.Scale(50, 50, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(img)
        self.logo = wx.StaticBitmap(self, wx.ID_ANY, bitmap)
        left_sidebar_sizer.Add(self.logo, 0, wx.ALL, 10)
        
        self.add = wx.Button(self, label="+ Add", size=(100, 60))
        self.Bind(wx.EVT_BUTTON, lambda event: self.file_or_folder(event), self.add)
        left_sidebar_sizer.Add(self.add, 0, wx.LEFT, 5)
        self.sizer.Add(left_sidebar_sizer, 0, wx.LEFT, 10)
        
        self.main_panel = wx.Panel(self)
        self.main_panel.SetBackgroundColour(wx.Colour(225, 225, 226))
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self.main_panel, label=f"My Droyve")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.main_sizer.Add(self.label, 0, wx.ALIGN_CENTER | wx.ALL, 15)

        self.path_label = wx.StaticText(self.main_panel, label=f"Path: {self.username}")
        font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.path_label.SetFont(font)
        self.main_sizer.Add(self.path_label, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        
        files = self.get_user_filenames()
        self.files = files.split(',')
        self.files.remove('|')

        self.print_files(self.files)

        self.main_panel.SetSizer(self.main_sizer)
        self.sizer.Add(self.main_panel, 1, wx.EXPAND | wx.ALL, 10)

        self.Bind(wx.EVT_TIMER, self.OnSingleClick)

        right_sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        icon_path = r"Pages\Assets\User_logo.jpg"
        img = wx.Image(icon_path, wx.BITMAP_TYPE_ANY)
        img = img.Scale(50, 50, wx.IMAGE_QUALITY_HIGH)
        logo_bitmap = wx.Bitmap(img)
        self.logo_button = wx.BitmapButton(self, wx.ID_ANY, logo_bitmap)
        self.logo_button.Bind(wx.EVT_BUTTON, self.on_logo_click)
        right_sidebar_sizer.Add(self.logo_button, 0, wx.RIGHT | wx.TOP, 10)
        self.sizer.Add(right_sidebar_sizer, 0, wx.LEFT, 10)

        self.SetSizer(self.sizer)
        self.Layout()


    def file_or_folder(self, event):
        popup = wx.PopupTransientWindow(self, flags=wx.BORDER_NONE)

        btn = event.GetEventObject()
        btn_pos = btn.ClientToScreen((0, btn.GetSize().height))

        panel = wx.Panel(popup)
        panel.SetBackgroundColour(wx.Colour(250, 250, 251))
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        file = wx.Button(panel, label="Upload file")
        panel.Bind(wx.EVT_BUTTON, lambda event: self.open_file_dialoge(event), file)

        folder = wx.Button(panel, label="Upload folder")
        panel.Bind(wx.EVT_BUTTON, lambda event: self.open_dir_dialoge(event), folder)

        sizer.Add(file, 0, wx.ALL, 10)
        sizer.Add(folder, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(sizer)
        sizer.Fit(panel)
        popup.SetSize(panel.GetSize())

        popup.Position(btn_pos, (100, -55))
        popup.Popup()


    def print_files(self, files):
        while self.main_sizer.GetItemCount() > 2:
            item = self.main_sizer.GetItem(2)

            if item.IsSizer():
                sizer = item.GetSizer()
                self.main_sizer.Detach(sizer)
                sizer.Clear(delete_windows=True)
            else:
                window = item.GetWindow()
                self.main_sizer.Detach(window)
                window.Destroy()

        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(len(files)):
            if i % 4 == 0:
                self.main_sizer.Add(file_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)
                file_sizer = wx.BoxSizer(wx.HORIZONTAL)
            if files[i].endswith(".folder"):
                files[i] = files[i].split('.folder')[0]
                button = wx.Button(self.main_panel, wx.ID_ANY, label=f"{files[i]}")
                button.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.on_dclick_folder(event))
                self.main_panel.Bind(wx.EVT_BUTTON, lambda event: self.on_click_folder(event), button)
            else:
                button = wx.Button(self.main_panel, wx.ID_ANY, label=f"{files[i]}")
                self.main_panel.Bind(wx.EVT_BUTTON, lambda event: self.on_click_file(event), button)
            file_sizer.Add(button, 0, wx.ALL, 5)

        self.main_sizer.Add(file_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)

        self.Layout()


    def open_file_dialoge(self, event):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Upload file".encode())

        public_key_pem = client.recv(2048)
        public_key = serialization.load_pem_public_key(public_key_pem)

        data = self.username
        encrypted_data = Utilities.encrypt(data.encode(), public_key)

        client.sendall(encrypted_data)
        
        file_dialog = wx.FileDialog(self, "Select a file")
        if file_dialog.ShowModal() != wx.ID_OK:
            return
        
        file_path = file_dialog.GetPath()

        file_name = file_path.split("\\")[-1]
        client.recv(1024)
        encrypted_data = Utilities.encrypt(file_name.encode(), public_key)
        client.sendall(encrypted_data)
        client.recv(1024)

        if self.is_txt(file_name):
            self.send_txt(file_path, client, public_key)

        elif self.is_bytes(file_name):
            self.send_bytes(file_path, client, public_key)
                
        self.files.append(file_name)
        self.print_files(self.files)


    def open_dir_dialoge(self, event):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Upload folder".encode())

        public_key_pem = client.recv(2048)
        public_key = serialization.load_pem_public_key(public_key_pem)

        encrypted_data = Utilities.encrypt(self.username.encode(), public_key)

        client.sendall(encrypted_data)
        
        folder_dialog = wx.DirDialog(self, "Select a folder")
        if folder_dialog.ShowModal() != wx.ID_OK:
            return
        
        folder_path = folder_dialog.GetPath()

        folder_name = folder_path.split("\\")[-1]
        client.recv(1024)
        encrypted_data = Utilities.encrypt(folder_name.encode(), public_key)
        client.sendall(encrypted_data)
        client.recv(1024)

        items = os.listdir(folder_path)
        files = ','.join(items)
        client.send(files.encode())

        for item in items:
            client.recv(1024)
            full_path = os.path.join(folder_path, item)
            if self.is_txt(item):
                with open(full_path, 'r') as file:
                    content = file.read()
                    length = len(content)
                    client.send(str(length).encode())
                    client.send(content.encode())

            if self.is_bytes(item):
                with open(full_path, 'rb') as file:
                    content = file.read()
                    length = len(content)
                    client.send(str(length).encode())
                    client.recv(1024)
                    client.send(content)
                
        self.files.append(folder_name)
        self.print_files(self.files)


    def on_logo_click(self, event):
        if self.username == "admin":
            email = "admin@gmail.com"
        else:
            client = socket.socket()
            client.connect((Utilities.get_pc_ip(), 8200))
            client.send("Get email".encode())
            client.recv(1024)
            client.send(self.username.encode())
            email = client.recv(1024).decode()

        popup = wx.PopupTransientWindow(self, flags=wx.BORDER_NONE)

        panel = wx.Panel(popup)
        panel.SetBackgroundColour(wx.Colour(250, 250, 251))

        sizer = wx.BoxSizer(wx.VERTICAL)

        email = wx.StaticText(panel, label=email)

        signout = wx.Button(panel, label="Sign out")
        signout.Bind(wx.EVT_BUTTON, lambda evt: self.sign_out(popup))

        sizer.Add(email, 0, wx.ALL, 10)
        sizer.Add(signout, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)
        sizer.Fit(panel)
        popup.SetSize(panel.GetSize())

        btn = event.GetEventObject()
        btn_pos = btn.ClientToScreen((0, btn.GetSize().height))

        popup.Position(btn_pos, (0, 0))
        popup.Popup()


    def sign_out(self, popup_win):
        popup_win.Hide()
        self.parent.show_frame(cur=self)


    def get_user_filenames(self, folder='\00b'):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Get filenames".encode())
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)
        client.send(folder.encode())
        filenames = client.recv(1024).decode()
        return filenames


    def on_click_file(self, event):
        popup = wx.PopupTransientWindow(self, flags=wx.BORDER_NONE)

        btn = event.GetEventObject()
        btn_pos = btn.ClientToScreen((0, btn.GetSize().height))

        panel = wx.Panel(popup)
        panel.SetBackgroundColour(wx.Colour(250, 250, 251))
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        download = wx.Button(panel, label="Download")
        panel.Bind(wx.EVT_BUTTON, lambda event: self.download_file(event, btn), download)

        remove = wx.Button(panel, label="Delete")
        panel.Bind(wx.EVT_BUTTON, lambda event: self.remove_file(event, popup, btn), remove)

        sizer.Add(download, 0, wx.ALL, 10)
        sizer.Add(remove, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(sizer)
        sizer.Fit(panel)
        popup.SetSize(panel.GetSize())

        popup.Position(btn_pos, (0, 0))
        popup.Popup()


    def on_click_folder(self, event):
        popup = wx.PopupTransientWindow(self, flags=wx.BORDER_NONE)

        btn = event.GetEventObject()
        btn_pos = btn.ClientToScreen((0, btn.GetSize().height))

        panel = wx.Panel(popup)
        panel.SetBackgroundColour(wx.Colour(250, 250, 251))
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        download = wx.Button(panel, label="Download")
        panel.Bind(wx.EVT_BUTTON, lambda event: self.download_folder(event, btn), download)

        remove = wx.Button(panel, label="Delete")
        panel.Bind(wx.EVT_BUTTON, lambda event: self.remove_file(event, popup, btn), remove)

        sizer.Add(download, 0, wx.ALL, 10)
        sizer.Add(remove, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(sizer)
        sizer.Fit(panel)
        popup.SetSize(panel.GetSize())

        popup.Position(btn_pos, (0, 0))
        popup.Popup()


    def on_dclick_folder(self, event):
        button = event.GetEventObject()
        folder = button.Label
        files = self.get_user_filenames(folder)
        self.path_label.SetLabel(fr"Path: {self.username}\{folder}")
        files = files.split(',')
        files.remove('|')
        self.print_files(files)


    def download_file(self, event, btn):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Get file".encode())
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)

        label = btn.Label
        if self.path_label.GetLabel() != self.username:
            label = self.path_label.GetLabel().split('\\')[-1] + "\\" + label

        client.send(label.encode())
        length = int(client.recv(1024).decode())
        client.send("Joules".encode())

        if self.is_txt(label):
            file_content = ''
            for i in range(length // 1024 + 1):
                file_content += client.recv(1024).decode()
            
            file_name = label.split("\\")[-1]
            with open(fr'C:\Users\Pc2\Desktop\{file_name}', 'w') as file:
                file.write(file_content)

        if self.is_bytes(label):
            file_content = b''
            for i in range(length // 1024 + 1):
                file_content += client.recv(1024)

            with open(fr'C:\Users\Pc2\Desktop\{label}', 'wb') as file:
                file.write(file_content)
    
    
    def download_folder(self, event, btn):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Get folder".encode())
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)

        label = btn.Label
        client.send(label.encode())
        full_path =  fr'C:\Users\Pc2\Desktop\{label}'
        os.mkdir(full_path)
        files = client.recv(1024).decode().split(',')

        for file_name in files:
            client.send("Joules".encode())
            length = int(client.recv(1024).decode())
            client.send("Joules1".encode())

            if self.is_txt(file_name):
                file_content = ''
                for i in range(length // 1024 + 1):
                    file_content += client.recv(1024).decode()

                with open(fr"{full_path}\{file_name}", 'w') as file:
                    file.write(file_content)
                
            if self.is_bytes(file_name):
                file_content = b''
                for i in range(length // 1024 + 1):
                    file_content += client.recv(1024)

                with open(fr"{full_path}\{file_name}", 'wb') as file:
                    file.write(file_content)


    def remove_file(self, event, popup, btn):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Remove file".encode())
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)

        label = btn.Label
        client.send(label.encode())

        self.files.remove(label)
        self.print_files(self.files)


    def send_bytes(self, file_path, client, public_key):
        with open(file_path, "rb") as file:
                image_bytes = file.read()

                length = len(image_bytes) // 190 + 1
                client.send(str(length).encode())
                client.recv(1024)

                encrypted_image = b''
                for i in range(0, len(image_bytes), 190):
                    chunk = image_bytes[i:i + 190]
                    encrypted_image += Utilities.encrypt(chunk, public_key)

                client.sendall(encrypted_image)


    def send_txt(self, file_path, client, public_key):
        with open(file_path, "r") as file:
            lines = file.readlines()
            content = ""
            for line in lines:
                content += line

            length = len(content) // 190 + 1
            client.send(str(length).encode())
            client.recv(1024)

            encrypted_file = b''
            for i in range(0, len(content), 190):
                chunk = content[i: i + 190]
                encrypted_file += Utilities.encrypt(chunk.encode(), public_key)

            client.sendall(encrypted_file)


    @staticmethod
    def is_bytes(file_name):
        return (file_name.endswith("jpeg") or file_name.endswith("jpg") or file_name.endswith("png")
                or file_name.endswith("gif") or file_name.endswith("exe") or file_name.endswith("avif")
                or file_name.endswith("jfif"))
    

    @staticmethod
    def is_txt(file_name):
        return file_name.endswith("TXT") or file_name.endswith("txt") or file_name.endswith("py")
    

    def OnLeftDown(self, event):
        self.timer.Start(200, oneShot=True)
        event.Skip() 
    def OnDoubleClick(self, event):
        if self.timer.IsRunning():
            self.timer.Stop()
        event.Skip()
    def OnSingleClick(self, event):
        if self.timer.IsRunning():
            self.timer.Stop()
