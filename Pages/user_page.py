import wx
import os
import socket
from utilities import Utilities
from cryptography.hazmat.primitives import serialization


class UserPage(wx.Panel):
    def __init__(self, parent : wx.Window, size, username : str):
        super(UserPage, self).__init__(parent, size=size)
        self.row_size = 4
        self.parent = parent
        self.username = username
        self.current_folder = []

        self.folders, self.files = self.get_user_filenames_from_server()
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.timer = wx.Timer(self)

        left_sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        
        icon_path = r"Pages\Assets\Logo.png"
        img = wx.Image(icon_path, wx.BITMAP_TYPE_ANY)
        img = img.Scale(50, 50, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(img)
        self.logo = wx.StaticBitmap(self, wx.ID_ANY, bitmap)
        left_sidebar_sizer.Add(self.logo, 0, wx.ALL, 10)
        
        self.add = wx.Button(self, label="+ Add", size=(100, 60), name="Add")
        self.Bind(wx.EVT_BUTTON, lambda event: self.show_popup(event, ["Upload file", "Upload folder"]), self.add)
        left_sidebar_sizer.Add(self.add, 0, wx.LEFT, 5)
        self.sizer.Add(left_sidebar_sizer, 0, wx.LEFT, 10)
        
        self.main_panel = wx.Panel(self)
        self.main_panel.SetBackgroundColour(wx.Colour(225, 225, 226))
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self.main_panel, label=f"My Droyve")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.main_sizer.Add(self.label, 0, wx.ALIGN_CENTER | wx.ALL, 15)

        self.path_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.path_label = wx.StaticText(self.main_panel, label=f"Path:")
        font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.path_label.SetFont(font)
        self.path_sizer.Add(self.path_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.path_buttons = []

        button = wx.Button(self.main_panel, label=self.username, size=(60, 40))
        self.main_panel.Bind(wx.EVT_BUTTON,lambda event: self.show_current_folder_contents(event), button)
        self.path_sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.path_buttons.append(button)

        self.main_sizer.Add(self.path_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        
        self.print_files()

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


    def show_current_folder_contents(self, event):
        btn = event.GetEventObject()
        stop = self.path_buttons.index(btn)
        self.delete_unwanted_files(self.path_sizer, stop)

        self.current_folder = self.current_folder[0:stop]
        self.folders, self.files = self.get_user_filenames_from_server()
        self.print_files()
        self.path_buttons = self.path_buttons[0:stop + 1]


    def print_files(self):
        self.delete_unwanted_files(self.main_sizer)
        
        container_sizer = ["Folders:", "Files:", "Zips:"]
        sizers = []

        for i in range(len(container_sizer)):
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(wx.StaticText(self.main_panel, wx.ID_ANY, container_sizer[i]), 0, wx.ALIGN_CENTER | wx.ALL, 5)
            container_sizer[i] = sizer
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizers.append(sizer)
            
        for i in range(len(self.folders)):
            if sizers[0].ItemCount % self.row_size == 0 and sizers[0].ItemCount != 0:
                container_sizer[0].Add(sizers[0], 0, wx.ALIGN_CENTER | wx.ALL, 5)
                sizers[0] = wx.BoxSizer(wx.HORIZONTAL)

            button = wx.Button(self.main_panel, wx.ID_ANY, label=self.folders[i], name="folder")
            button.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.on_dclick_folder(event))
            self.main_panel.Bind(wx.EVT_BUTTON, lambda event: self.show_popup(event, ["Download", "Delete"]), button)
            sizers[0].Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        for i in range(len(self.files)):
            button = wx.Button(self.main_panel, wx.ID_ANY, label=self.files[i], name="file")
            self.main_panel.Bind(wx.EVT_BUTTON, lambda event: self.show_popup(event, ["Download", "Delete"]), button)
            
            if self.files[i].endswith('.zip'):
                sizers[2].Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
                if sizers[2].ItemCount % self.row_size == 0 and sizers[2].ItemCount != 0:
                    container_sizer[2].Add(sizers[2], 0, wx.ALIGN_CENTER | wx.ALL, 5)
                    sizers[2] = wx.BoxSizer(wx.HORIZONTAL)
            else:
                sizers[1].Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
                if sizers[1].ItemCount % self.row_size == 0 and sizers[1].ItemCount != 0:
                    container_sizer[1].Add(sizers[1], 0, wx.ALIGN_CENTER | wx.ALL, 5)
                    sizers[1] = wx.BoxSizer(wx.HORIZONTAL)

        for i in range(len(container_sizer)):
            if container_sizer[i].GetItemCount() > 0:
                container_sizer[i].Add(sizers[i], 0, wx.ALIGN_CENTER | wx.ALL, 10)

        for i in range(len(sizers)):
            if container_sizer[i].GetItemCount() > 1 and sizers[i].GetItemCount() > 0:
                self.main_sizer.Add(container_sizer[i], 0, wx.ALIGN_CENTER | wx.ALL, 10)
            else:
                for item in container_sizer[i].GetChildren():
                    widget = item.GetWindow()
                    if widget:
                        widget.Destroy()
                    container_sizer[i].Clear(delete_windows=True)

        self.Layout()


    def send_file(self, client, full_path: str):
        if self.is_txt(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                length = len(content)
                client.send(f"txt|{length}".encode())
                client.recv(1024)

                client.send(content.encode())

        else:
            with open(full_path, 'rb') as f:
                content = f.read()
                length = len(content)
                client.send(f"bytes|{length}".encode())
                client.recv(1024)
                
                client.send(content)


    def open_file_dialoge(self, event):
        file_dialog = wx.FileDialog(self, "Select a file")
        if file_dialog.ShowModal() != wx.ID_OK:
            return
        
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Upload file".encode())

        public_key_pem = client.recv(2048)
        public_key = serialization.load_pem_public_key(public_key_pem)

        encrypted_data = Utilities.encrypt(self.username.encode(), public_key)

        client.sendall(encrypted_data)
        
        full_path = file_dialog.GetPath()

        file_name = full_path.split("\\")[-1]
        client.recv(1024)
        if len(self.current_folder) > 0:
            file_name = ('\\').join(self.current_folder) + '\\' + file_name

        encrypted_data = Utilities.encrypt(file_name.encode(), public_key)
        file_name = full_path.split("\\")[-1]
        client.sendall(encrypted_data)
        file_exists = client.recv(1024).decode()
        if file_exists == 'exists!':
            if not self.show_dialog('File'):
                return
            client.send(f'Replace file'.encode())
            client.recv(1024)

            self.files.remove(file_name)
        
        self.send_file(client, full_path)
        
        self.files.append(file_name)
        self.print_files()


    def open_dir_dialoge(self, event):
        folder_dialog = wx.DirDialog(self, "Select a folder")
        if folder_dialog.ShowModal() != wx.ID_OK:
            return
        
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Upload folder".encode())

        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)

        folder_path = folder_dialog.GetPath()

        folder_name = folder_path.split("\\")[-1]
        if len(self.current_folder) > 0:
            folder_name = ('\\').join(self.current_folder) + '\\' + folder_name

        client.send(folder_name.encode())
        folder_name = folder_path.split("\\")[-1]
        folder_exists = client.recv(1024).decode()
        if folder_exists == 'exists!':
            if not self.show_dialog('Folder'):
                return
            client.send(f'Replace folder'.encode())
            client.recv(1024)

            self.folders.remove(folder_name)

        self.send_all_files_in_folder(client, folder_path)

        self.folders.append(folder_name)
        self.print_files()


    def send_all_files(self, client, folder_path, file):
        client.recv(1024)
        
        full_path = os.path.join(folder_path, file)
        self.send_file(client, full_path)


    def send_all_files_in_folder(self, client, folder_path):
        folders, files = self.get_and_send_folders_and_files(client, folder_path)
        if not folders:
            for item in files:
                self.send_all_files(client, folder_path, item)
            return
        
        for folder in folders:
            path = os.path.join(folder_path, folder)
            for item in files:
                self.send_all_files(client, folder_path, item)
            self.send_all_files_in_folder(client, path)


    def get_and_send_folders_and_files(self, client, folder_path):
        items = os.listdir(folder_path)
        folder_names = []
        file_names = []
        
        for item in items:
            full_path = os.path.join(folder_path, item)
            if os.path.isdir(full_path):
                folder_names.append(item)
            else:
                file_names.append(item)

        files = ','.join(file_names)
        folders = ','.join(folder_names)

        if folders == '':
            client.send("none".encode())
            folders = []
        else:
            client.send(folders.encode())
            folders = folders.split(',')

        client.recv(1024)

        if files == '':
            client.send("none".encode())
            files = []
        else:
            client.send(files.encode())
            files = files.split(',')
        return folders, files


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

        self.show_popup(event, ["Sign out"], [email])


    def sign_out(self, popup_win):
        popup_win.Hide()
        self.current_folder = []
        self.parent.show_frame(cur=self)


    def get_user_filenames_from_server(self):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Get filenames".encode())
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)
        if len(self.current_folder) > 0:
            path = ('\\').join(self.current_folder) + "\n "
            client.send(path.encode())
        else:
            client.send("\n".encode())

        return self.get_all_filenames(client)


    def on_dclick_folder(self, event):
        button = event.GetEventObject()
        folder = button.Label
        self.current_folder.append(folder)
        self.folders, self.files = self.get_user_filenames_from_server()
        
        button = wx.Button(self.main_panel, label=folder, size=(60, 40))
        self.main_panel.Bind(wx.EVT_BUTTON,lambda event: self.show_current_folder_contents(event), button)
        self.path_sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.path_buttons.append(button)

        self.print_files()


    def download_folder_or_files(self, event, btn):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        name = btn.Name
        client.send(f"Get {name}".encode()) #Check to see which button (file/folder) called the function and using that I sent the correct name for the server.
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)

        label = btn.Label
        if len(self.current_folder) > 0: #Checks to see if I'm in a folder within the interface 
            label = ('\\').join(self.current_folder) + '\\' + label #If so I append the path to the folder I'm currently in to the name of the file/folder

        client.send(label.encode())
        label = btn.Label

        full_path =  fr'C:\Users\Pc2\Desktop\{label}'
        if name == "folder":
            os.mkdir(full_path) #Makes a new folder in the desktop
            self.recieve_all_files_and_folders(client, full_path)
            """Function that saves all the files and folders in the folder we created
              on the desktop, while mantaining their order and structure"""
            return
        
        client.recv(1024)
        self.recieve_file(client, full_path)


    def recieve_all_files_and_folders(self, client, full_path):
        folders, files = self.get_all_filenames(client)
        if not folders:
            self.get_all_files(client, files, full_path)
            return

        for folder in folders:
            path = os.path.join(full_path, folder)
            os.mkdir(path)
            self.get_all_files(client, files, full_path)
            self.recieve_all_files_and_folders(client, path)


    def get_all_filenames(self, client):
        folders = client.recv(1024).decode()
        client.send("Joules".encode())
        files = client.recv(1024).decode()

        if files != "none":
            files = files.split(',')
        else:
            files = []

        if folders != "none":
            folders = folders.split(',')
        else:
            folders = []

        return folders, files


    def get_all_files(self, client, files, full_path):
        for item in files:
            path = os.path.join(full_path, item)
            self.recieve_file(client, path)


    def remove_folder_or_files(self, event, btn):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        name = btn.Name
        client.send("Remove file".encode())
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)
        
        label = btn.Label
        if name == "folder":
            self.folders.remove(label)
        else:
            self.files.remove(label)

        if len(self.current_folder) > 0:
            label = ('\\').join(self.current_folder) + '\\' + label
        client.send(label.encode())

        self.print_files()


    def recieve_file(self, client, full_path):
        client.send("Joules1".encode())
        data = client.recv(1024).decode()
        extension, length = data.split('|')[0], int(data.split('|')[-1])

        client.send("Joules1".encode())

        file_content = client.recv(length)
        while len(file_content) < length:
            file_content += client.recv(length)

        if extension == 'txt':
            file_content = file_content.decode()
            with open(full_path, 'w') as file:
                file.write(file_content)

            return
            
        with open(full_path, 'wb') as file:
            file.write(file_content)


    def show_popup(self, event, button_list, label_list = []):
        popup = wx.PopupTransientWindow(self, flags=wx.BORDER_NONE)

        btn = event.GetEventObject()
        btn_pos = btn.ClientToScreen((0, btn.GetSize().height))

        panel = wx.Panel(popup)
        panel.SetBackgroundColour(wx.Colour(250, 250, 251))
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        for label_name in label_list:
            label = wx.StaticText(panel, label=label_name)
            sizer.Add(label, 0, wx.ALL, 10)

        for button_name in button_list:
            button = wx.Button(panel, label=button_name)
            if button_name == "Upload file":
                panel.Bind(wx.EVT_BUTTON, lambda event: self.open_file_dialoge(event), button)
            elif button_name == "Upload folder":
                panel.Bind(wx.EVT_BUTTON, lambda event: self.open_dir_dialoge(event), button)
            elif button_name == "Download":
                panel.Bind(wx.EVT_BUTTON, lambda event: self.download_folder_or_files(event, btn), button)
            elif button_name == "Delete":
                panel.Bind(wx.EVT_BUTTON, lambda event: self.remove_folder_or_files(event, btn), button)
            elif button_name == "Sign out":
                panel.Bind(wx.EVT_BUTTON, lambda evt: self.sign_out(popup), button)
            
            sizer.Add(button, 0, wx.ALL, 10)
        
        panel.SetSizer(sizer)
        sizer.Fit(panel)
        popup.SetSize(panel.GetSize())

        if btn.Name == "Add":
            popup.Position(btn_pos, (100, -55))
        else:
            popup.Position(btn_pos, (0, 0))
        popup.Popup()


    def show_dialog(self, item : str):
        dialog = wx.Dialog(self, title=f'{item} already exists!', size=(300, 220),
                            name=f'{item} already exists!', style=wx.DEFAULT_DIALOG_STYLE & ~wx.CLOSE_BOX)
        dialog.Centre()

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(dialog, label=f'{item} already exists!')
        sizer.Add(label, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        replace_file = wx.Button(dialog, label=f"Replace {item.lower()} in destination", size=(200, 60), name="replace")
        close = wx.Button(dialog, label="Cancel", size=(200, 50), name="cancel")

        sizer.Add(replace_file, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        sizer.Add(close, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        dialog.SetSizer(sizer)

        dialog.Bind(wx.EVT_BUTTON, lambda e: dialog.EndModal(wx.ID_OK), replace_file)
        dialog.Bind(wx.EVT_BUTTON, lambda e: dialog.EndModal(wx.ID_CANCEL), close)

        state = dialog.ShowModal()
        dialog.Destroy()

        if state == wx.ID_OK:
            return True
        return False


    def delete_unwanted_files(self, sizer: wx.BoxSizer, stop: int=0) -> None:
        while sizer.GetItemCount() > stop + 2:
            item = sizer.GetItem(stop + 2)

            if item.IsSizer():
                temp_sizer = item.GetSizer()
                sizer.Detach(temp_sizer)
                temp_sizer.Clear(delete_windows=True)
            else:
                window = item.GetWindow()
                sizer.Detach(window)
                window.Destroy()


    def is_txt(self, path):
        with open(path, "rb") as file:
            chunk = file.read(4096)

        if b"\x00" in chunk:
            return False

        try:
            chunk.decode()
            return True
        except UnicodeDecodeError:
            return False


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
