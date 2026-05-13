import wx
import os
import json
import socket
import deploy_algo
from utilities import Utilities
from login_page import LoginPage
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
        
        icon_path = r"Assets\Logo.png"
        img = wx.Image(icon_path, wx.BITMAP_TYPE_ANY)
        img = img.Scale(50, 50, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(img)
        self.logo = wx.StaticBitmap(self, wx.ID_ANY, bitmap)
        left_sidebar_sizer.Add(self.logo, 0, wx.ALL, 10)
        
        self.add = wx.Button(self, label="+ Add", size=(100, 60), name="Add", style=wx.BORDER_NONE)
        self.add.SetBackgroundColour((213, 250, 255))
            
        self.add.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=self.add: self.on_button_hover(b, True, 1))
        self.add.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=self.add: self.on_button_hover(b, False, 2))

        self.Bind(wx.EVT_BUTTON, lambda event: self.show_popup(event, ["Upload file", "Upload folder"]), self.add)
        left_sidebar_sizer.Add(self.add, 0, wx.LEFT, 5)

        self.share = wx.Button(self, label="Files Shared \n with Me", size=(100, 60), name="SharedFiles", style=wx.BORDER_NONE)
        self.share.SetBackgroundColour((213, 250, 255))
            
        self.share.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=self.share: self.on_button_hover(b, True, 1))
        self.share.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=self.share: self.on_button_hover(b, False, 2))

        self.Bind(wx.EVT_BUTTON, lambda event: self.on_dclick_folder(event), self.share)
        left_sidebar_sizer.Add(self.share, 0, wx.LEFT | wx.TOP, 5)
        self.sizer.Add(left_sidebar_sizer, 0, wx.LEFT, 10)
        
        self.main_panel = wx.Panel(self)
        self.main_panel.SetBackgroundColour(wx.Colour(225, 225, 226))
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self.main_panel, label=f"My Droyve")
        font = wx.Font(30, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.label.SetFont(font)
        self.main_sizer.Add(self.label, 0, wx.ALIGN_CENTER | wx.ALL, 15)

        self.path_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.path_label = wx.StaticText(self.main_panel, label="Path:")
        font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        self.path_label.SetFont(font)
        self.path_sizer.Add(self.path_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.path_buttons = []

        button = wx.Button(self.main_panel, label=self.username, size=(70, 40), style=wx.BORDER_NONE)
        button.SetBackgroundColour((255, 244, 206))
            
        button.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=button: self.on_button_hover(b, True, 3))
        button.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=button: self.on_button_hover(b, False, 4))

        self.main_panel.Bind(wx.EVT_BUTTON, lambda event: self.show_current_folder_contents(event), button)
        self.path_sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.path_buttons.append(button)

        self.main_sizer.Add(self.path_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        
        self.print_files()

        self.main_panel.SetSizer(self.main_sizer)
        self.sizer.Add(self.main_panel, 1, wx.EXPAND | wx.ALL, 10)

        self.Bind(wx.EVT_TIMER, self.OnSingleClick)

        right_sidebar_sizer = wx.BoxSizer(wx.VERTICAL)

        icon_path = r"Assets\User_logo.jpg"
        img = wx.Image(icon_path, wx.BITMAP_TYPE_ANY)
        img = img.Scale(60, 60, wx.IMAGE_QUALITY_HIGH)
        logo_bitmap = wx.Bitmap(img)
        self.logo_button = wx.BitmapButton(self, wx.ID_ANY, logo_bitmap, name='User')
        self.logo_button.Bind(wx.EVT_BUTTON, lambda event : self.show_popup(event, ["Add account", "Sign out"]))
        right_sidebar_sizer.Add(self.logo_button, 0, wx.ALIGN_CENTER | wx.RIGHT | wx.TOP, 10)

        self.auto_save_file = wx.Button(self, label='Auto save file', size=(100, 60), style=wx.BORDER_NONE)
        self.auto_save_file.SetBackgroundColour((213, 250, 255))
            
        self.auto_save_file.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=self.auto_save_file: self.on_button_hover(b, True, 1))
        self.auto_save_file.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=self.auto_save_file: self.on_button_hover(b, False, 2))

        self.Bind(wx.EVT_BUTTON, lambda e: self.show_auto_save_dialog(), self.auto_save_file)
        right_sidebar_sizer.Add(self.auto_save_file, 0, wx.ALIGN_CENTER | wx.RIGHT | wx.TOP, 10)

        self.sizer.Add(right_sidebar_sizer, 0, wx.LEFT, 10)

        self.SetSizer(self.sizer)
        self.Layout()


    def show_current_folder_contents(self, event):
        btn = event.GetEventObject()
        stop = self.path_buttons.index(btn)
        self.delete_unwanted_files(self.path_sizer, stop)

        self.current_folder = self.current_folder[0:stop]
        if 'SharedFiles' in self.current_folder:
            self.add.Hide()
        else:
            self.add.Show()
        self.folders, self.files = self.get_user_filenames_from_server()
        self.print_files()
        self.path_buttons = self.path_buttons[0:stop + 1]


    def print_files(self):
        self.delete_unwanted_files(self.main_sizer)
        
        container_sizer = ["Folders:", "Files:", "Zips:"]
        color_list = [(0, 122, 255), (40, 167, 69), (255, 153, 0)]
        sizers = []

        for i in range(len(container_sizer)):
            sizer = wx.BoxSizer(wx.VERTICAL)
            text = wx.StaticText(self.main_panel, wx.ID_ANY, container_sizer[i])
            text.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            text.SetForegroundColour(color_list[i])
            sizer.Add(text, 0, wx.ALIGN_CENTER | wx.ALL, 5)
            container_sizer[i] = sizer
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizers.append(sizer)

        btn_color = (21, 81, 170)

        for i in range(len(self.folders)):
            if sizers[0].ItemCount % self.row_size == 0 and sizers[0].ItemCount != 0:
                container_sizer[0].Add(sizers[0], 0, wx.ALIGN_CENTER | wx.ALL, 5)
                sizers[0] = wx.BoxSizer(wx.HORIZONTAL)

            button = wx.Button(self.main_panel, wx.ID_ANY, label=self.folders[i], name="folder", style=wx.BORDER_NONE)
            button.SetBackgroundColour(btn_color)
            button.SetForegroundColour((255, 255, 255))
            
            button.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=button: self.on_button_hover(b, True, 1))
            button.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=button: self.on_button_hover(b, False, 0))

            button.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.on_dclick_folder(event))
            self.main_panel.Bind(wx.EVT_BUTTON, lambda event: self.show_popup(event, ["Download", "Share", "Delete"]), button)
            sizers[0].Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        for i in range(len(self.files)):
            button = wx.Button(self.main_panel, wx.ID_ANY, label=self.files[i], name="file", style=wx.BORDER_NONE)
            button.SetBackgroundColour(btn_color)
            button.SetForegroundColour((255, 255, 255))
            
            button.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=button: self.on_button_hover(b, True, 1))
            button.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=button: self.on_button_hover(b, False, 0))

            self.main_panel.Bind(wx.EVT_BUTTON, lambda event: self.show_popup(event, ["Download", "Share", "Delete"]), button)
            
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
            elif container_sizer[i].GetItemCount() > 2:
                self.main_sizer.Add(container_sizer[i], 0, wx.ALIGN_CENTER | wx.ALL, 10)
            else:
                for item in container_sizer[i].GetChildren():
                    widget = item.GetWindow()
                    if widget:
                        widget.Destroy()
                    container_sizer[i].Clear(delete_windows=True)

        self.Layout()


    def on_button_hover(self, button: wx.Button, hover: bool, index: int):
        color = [(21, 81, 170), (52, 152, 219), (213, 250, 255), (255, 229, 214), (255, 244, 206)]
        
        button.SetBackgroundColour(color[index] if hover else color[index])
        button.Refresh()


    def send_file(self, client, full_path: str):
        if self.is_txt(full_path):
            with open(full_path, 'r', errors='ignore') as f:
                content = f.read().encode()
                length = len(content)
                client.send(f"txt|{length}".encode())
                client.recv(1024)

                client.sendall(content)
                return

        with open(full_path, 'rb') as f:
            content = f.read()
            length = len(content)
            client.send(f"bytes|{length}".encode())
            client.recv(1024)
            
            client.sendall(content)


    def open_file_or_folder_dialog(self, event, file_or_folder, full_path=''):
        if file_or_folder == 'file' and full_path == '':
            file_dialog = wx.FileDialog(self, "Select a file")
            if file_dialog.ShowModal() != wx.ID_OK:
                return
            full_path = file_dialog.GetPath()
        elif file_or_folder == 'folder' and full_path == '':
            folder_dialog = wx.DirDialog(self, "Select a folder")
            if folder_dialog.ShowModal() != wx.ID_OK:
                return
            full_path = folder_dialog.GetPath()

        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send(f"Upload {file_or_folder}".encode())

        public_key_pem = client.recv(2048)
        public_key = serialization.load_pem_public_key(public_key_pem)

        encrypted_data = Utilities.encrypt(self.username.encode(), public_key)

        client.sendall(encrypted_data)

        file_name = full_path.split("\\")[-1]
        client.recv(1024)
        if len(self.current_folder):
            file_name = os.path.join(*self.current_folder, file_name)

        encrypted_data = Utilities.encrypt(file_name.encode(), public_key)
        client.sendall(encrypted_data)
        file_exists = client.recv(1024).decode()
        if file_exists == 'exists!':
            dialog = file_or_folder[0].upper() + file_or_folder[1:]
            if not self.show_dialog(dialog):
                return
            client.send(f'Replace {file_or_folder}'.encode())
            client.recv(1024)

        file_name = full_path.split("\\")[-1]
        if file_or_folder == 'file':
            if file_name in self.files:
                self.files.remove(file_name)
            self.files.append(file_name)

            self.send_file(client, full_path)
        else:
            if file_name in self.folders:
                self.folders.remove(file_name)
            self.folders.append(file_name)

            self.send_all_files_in_folder(client, full_path)
        self.print_files()


    def send_all_files_in_folder(self, client, folder_path):
        folders, files = self.get_and_send_folders_and_files(client, folder_path)
        if not folders:
            for item in files:
                client.recv(1024)
                file_path = os.path.join(folder_path, item)
                self.send_file(client, file_path)
            return
        
        for folder in folders:
            path = os.path.join(folder_path, folder)
            for item in files:
                client.recv(1024)
                file_path = os.path.join(folder_path, item)
                self.send_file(client, file_path)
            client.recv(1024)
            self.send_all_files_in_folder(client, path)


    def get_and_send_folders_and_files(self, client, folder_path):
        items = os.listdir(folder_path)
        if '.git' in items:
            items.remove('.git')
        folder_names = []
        file_names = []
        
        for item in items:
            full_path = os.path.join(folder_path, item)
            if os.path.isdir(full_path):
                folder_names.append(item)
            else:
                file_names.append(item)

        if len(folder_names):
            folders = ','.join(folder_names)
        else:
            folders = 'none'
                    
        if len(file_names):
            files = ','.join(file_names)
        else:
            files = 'none'

        data = f"{folders}|{files}"
        client.send(data.encode())

        return folder_names, file_names


    def sign_out(self, popup_win):
        popup_win.Hide()
        if os.path.isfile('authToken.json'):
            os.remove('authToken.json')
        self.current_folder = []
        self.parent.show_frame(cur=self)


    def switch_account(self, popup_win, action):
        popup_win.Hide()
        if action == 'login':
            self.parent.show_frame(LoginPage, self)
        else:
            username = Utilities.remember_me(action)
            self.parent.show_user_frame(username, self)


    def get_user_filenames_from_server(self):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send("Get filenames".encode())
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)
        if len(self.current_folder):
            path = os.path.join(*self.current_folder) + "\n "
            client.send(path.encode())
        else:
            client.send("\n".encode())

        return self.get_all_filenames(client)


    def on_dclick_folder(self, event):
        button = event.GetEventObject()
        folder = button.Label
        if folder.startswith('Files Shared'):
            folder = button.Name

        if not folder in self.current_folder:
            if folder == 'SharedFiles':
                self.add.Hide()
                self.current_folder = []
                self.path_buttons = self.path_buttons[0:1]
                self.delete_unwanted_files(self.path_sizer)

            self.current_folder.append(folder)
            button = wx.Button(self.main_panel, label=folder, size=(70, 40), style=wx.BORDER_NONE)
            button.SetBackgroundColour((255, 244, 206))
            
            button.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=button: self.on_button_hover(b, True, 3))
            button.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=button: self.on_button_hover(b, False, 4))

            self.main_panel.Bind(wx.EVT_BUTTON,lambda event: self.show_current_folder_contents(event), button)
            self.path_sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
            self.path_buttons.append(button)
        
        self.folders, self.files = self.get_user_filenames_from_server()
        
        self.print_files()


    def download_folder_or_files(self, event, btn : wx.Button):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        name = btn.Name
        client.send(f"Get {name}".encode())
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)

        label = btn.Label
        full_path =  r'C:\Users\Pc2\Desktop'
        if len(self.current_folder):
            label = os.path.join(*self.current_folder, label)

        client.send(label.encode())
        label = btn.Label

        if name == "folder":
            full_path = os.path.join(full_path, label)
            os.mkdir(full_path)
            self.receive_all_files_and_folders(client, full_path)
            return
        
        self.receive_file(client, full_path, label)


    def show_auto_save_dialog(self):
        frame = wx.Frame(self.parent, title='Auto save file', size=(525, 200))
        frame.Centre()
        frame.Show()
        panel = wx.Panel(frame, size=(525, 300))
        panel.SetBackgroundColour(wx.Colour(245, 245, 246))
        
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(panel, 1, wx.EXPAND)

        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(panel, label='Enter a path of a file you want auto saved')
        font = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        label.SetFont(font)

        panel_sizer.Add(label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 20)

        path_input = wx.TextCtrl(panel, size=(200, 30))
        error_msg = wx.StaticText(panel)
        error_msg.SetFont(wx.Font(13, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD))
        error_msg.SetForegroundColour(wx.RED)
        enter_path = wx.Button(panel, label='Enter path')

        panel.Bind(wx.EVT_BUTTON, lambda e: self.deploy_algo_script(path_input.GetLineText(lineNo=0), frame, error_msg))

        panel_sizer.Add(path_input, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        panel_sizer.Add(error_msg, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        panel_sizer.Add(enter_path, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        panel.SetSizer(panel_sizer)
        frame.SetSizer(frame_sizer)

        panel.Layout()
        frame.Layout()


    def show_share_dialog(self, filename):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send(f"Share file|{self.username}".encode())
        connected_emails = client.recv(1024).decode().split(',')
        frame = wx.Frame(self.parent, title='Share With', size=(525, 300))
        times_shared = []
        if connected_emails[0] != 'No connected emails!':
            client.send('Send user times shared'.encode())
            times_shared = client.recv(1024).decode().split(',')
            client.close()
        frame.Centre()
        frame.Show()

        panel = wx.Panel(frame, size=(525, 300))
        panel.SetBackgroundColour(wx.Colour(245, 245, 246))
        
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(panel, 1, wx.EXPAND)

        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, label='Who do you want to share your files with?')
        font = wx.Font(15, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM)
        label.SetFont(font)

        panel_sizer.Add(label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 20)

        email_input = wx.TextCtrl(panel, size=(250, 30))
        panel.Bind(wx.EVT_TEXT, lambda event: self.emails_match(event, panel, filename, connected_emails, times_shared), email_input)
        panel_sizer.Add(email_input, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        panel.SetSizer(panel_sizer)
        frame.SetSizer(frame_sizer)

        panel.Layout()
        frame.Layout()

        self.emails_match(None, panel, filename, connected_emails, times_shared, frame)


    def emails_match(self, event, parent : wx.Window, file : str, connected_emails, times_shared, frame):
        sizer = parent.GetSizer()
        if event is not None:
            prefix = event.GetString()
        else:
            prefix = ''
        self.delete_unwanted_files(sizer)
        if prefix == '':
            table = dict(zip(connected_emails, times_shared))
            sorted_by_times_shared = dict(sorted(table.items(), key=lambda item: item[1], reverse=True))
            i = 0
            emails = list(sorted_by_times_shared.keys())
            for email in emails[:3]:
                button = wx.Button(parent, label=email)
                parent.Bind(wx.EVT_BUTTON, lambda event, e=email: self.send_files_to_user(e, file, frame), button)
                font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Segoe UI")
                button.SetFont(font)
                sizer.Add(button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
                i += 1

        elif not prefix.endswith('@gmail.com'):
            for email in connected_emails:
                if prefix in email:
                    button = wx.Button(parent, label=email)
                    parent.Bind(wx.EVT_BUTTON, lambda event, e=email: self.send_files_to_user(e, file, frame), button)
                    font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Segoe UI")
                    button.SetFont(font)
                    sizer.Add(button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
        else:
            client = socket.socket()
            client.connect((Utilities.get_pc_ip(), 8200))
            client.send('Share file'.encode())
            client.recv(1024).decode()
            client.send(prefix.encode())
            exists = client.recv(1024).decode()
            client.close()
            if exists == 'True':
                button = wx.Button(parent, label=prefix)  
                parent.Bind(wx.EVT_BUTTON, lambda event, e=prefix: self.send_files_to_user(e, file, frame), button)
                font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Segoe UI")
                button.SetFont(font)
                sizer.Add(button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
            else:
                label = wx.StaticText(parent, label='No emails found with this prefix')
                font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Segoe UI")
                label.SetFont(font)
                label.SetForegroundColour(wx.RED)
                sizer.Add(label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
        
        if event is not None:
            event.Skip()
        parent.Layout()


    def send_files_to_user(self, email, file, frame):
        client = socket.socket()
        client.connect((Utilities.get_pc_ip(), 8200))
        client.send('Share to user'.encode())
        client.recv(1024)
        client.send(f"{self.username}|{email}".encode())
        client.recv(1024)

        if len(self.current_folder):
            file = os.path.join(*self.current_folder, file)

        client.send(file.encode())
        client.close()
        frame.Destroy()


    def receive_all_files_and_folders(self, client, full_path):
        folders, files = self.get_all_filenames(client)
        if not folders:
            for item in files:
                client.send('Send file'.encode())
                self.receive_file(client, full_path, item)
            return

        for folder in folders:
            path = os.path.join(full_path, folder)
            os.mkdir(path)
            for item in files:
                client.send('Send file'.encode())
                self.receive_file(client, full_path, item)
            client.send('Send all files'.encode())
            self.receive_all_files_and_folders(client, path)


    def get_all_filenames(self, client):
        folders, files = client.recv(1024).decode().split('|')

        if files != "none":
            files = files.split(',')
        else:
            files = []

        if folders != "none":
            folders = folders.split(',')
        else:
            folders = []

        return folders, files


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

        if len(self.current_folder):
            label = os.path.join(*self.current_folder, label)
        client.send(label.encode())

        self.print_files()


    def receive_file(self, client, path, file):
        data = client.recv(1024).decode()
        extension, length = data.split('|')[0], int(data.split('|')[-1])

        client.send("Send file content".encode())
        full_path = os.path.join(path, file)

        file_content = client.recv(length)
        while len(file_content) < length:
            file_content += client.recv(length - len(file_content))

        if extension == 'txt':
            file_content = file_content.decode()
            with open(full_path, 'w') as file:
                file.write(file_content)
            return

        with open(full_path, 'wb') as file:
            file.write(file_content)


    def show_popup(self, event, button_list, father_popup=None):
        popup = wx.PopupTransientWindow(self, flags=wx.BORDER_NONE)

        btn = event.GetEventObject()
        btn_pos = btn.ClientToScreen((0, btn.GetSize().height))
        filename = btn.Label

        panel = wx.Panel(popup)
        panel.SetBackgroundColour(wx.Colour(200, 200, 200))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        if btn.Name == "User":
            if os.path.isfile('authToken.json'):
                with open('authToken.json', 'r') as file:
                    emails = list(json.load(file).keys())
                    for email in emails:
                        button = wx.Button(panel, label=email)
                        panel.Bind(wx.EVT_BUTTON, lambda event, e=email: self.switch_account(popup, e), button)
                        sizer.Add(button, 0, wx.ALL, 10)
                    sizer.Add(wx.StaticLine(panel, style=wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        for button_name in button_list:
            button = wx.Button(panel, label=button_name)
            if button_name == "Upload file":
                panel.Bind(wx.EVT_BUTTON, lambda event: self.open_file_or_folder_dialog(event, 'file'), button)
            elif button_name == "Upload folder":
                panel.Bind(wx.EVT_BUTTON, lambda event: self.open_file_or_folder_dialog(event, 'folder'), button)
            elif button_name == "Download":
                panel.Bind(wx.EVT_BUTTON, lambda event: self.download_folder_or_files(event, btn), button)
            elif button_name == "Share":
                panel.Bind(wx.EVT_BUTTON, lambda event: self.show_share_dialog(filename), button)
            elif button_name == "Delete":
                panel.Bind(wx.EVT_BUTTON, lambda event: self.remove_folder_or_files(event, btn), button)
            elif button_name == "Sign out":
                if os.path.isfile('authToken.json'):
                    with open('authToken.json', 'r') as file:
                        emails = list(json.load(file).keys())
                    if len(emails) > 1:
                        one = wx.Button(panel, label='Sign out one account')
                        panel.Bind(wx.EVT_BUTTON, lambda evt: self.show_popup(event, emails, popup), one)
                        sizer.Add(one, 0, wx.ALL, 10)
                panel.Bind(wx.EVT_BUTTON, lambda evt: self.sign_out(popup), button)
            elif button_name == "Add account":
                if not os.path.isfile('authToken.json'):
                    button.SetLabel('Switch account')
                panel.Bind(wx.EVT_BUTTON, lambda evt: self.switch_account(popup, 'login'), button)
            elif button_name.endswith('@gmail.com'):
                panel.Bind(wx.EVT_BUTTON, lambda evt, account=button_name: self.delete_account(father_popup, popup, account), button)
            sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)   
        sizer.Fit(panel)
        popup.SetSize(panel.GetSize())

        if btn.Name == "Add":
            popup.Position(btn_pos, (100, -55))
        elif btn.Name == "User":
            popup.Position(btn_pos, (-158, -55))
        else:
            popup.Position(btn_pos, (-6, 0))
        popup.Popup()


    def delete_account(self, father_popup, popup, account):
        with open('authToken.json', 'r') as file:
            emails = json.load(file)
            del emails[account]
        with open('authToken.json', 'w') as file:
            json.dump(emails, file)
        popup.Hide()
        father_popup.Hide()
        username = Utilities.remember_me('first')
        self.parent.show_user_frame(username, self)


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


    def deploy_algo_script(self, path, frame_to_delete : wx.Frame, error_label : wx.StaticText):
        accepted = False
        try:
            current_folder = '\\'.join(self.current_folder)
            deploy_algo.main(self.username, path, current_folder, Utilities.get_pc_ip())
        except Exception as e:
            error_label.SetLabel('Path not found!')
            frame_to_delete.Layout()
            print(e)
        else:
            accepted = True

        if accepted:
            if os.path.isdir(path):
                self.open_file_or_folder_dialog(None, 'folder', path)
            else:
                self.open_file_or_folder_dialog(None, 'file', path)
            frame_to_delete.Destroy()


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
