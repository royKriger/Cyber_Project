import os
import sys
import time
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    def __init__(self, username, path, ip, current_folder):
        super().__init__()
        self.username = username
        self.path = path
        self.server_ip = ip
        self.current_folder = current_folder


    def on_modified(self, event):
        file = self.path.split('\\')[-1]
        file_or_folder = 'file' if os.path.isfile(self.path) else 'folder'

        if event.src_path.endswith(file):
            client = socket.socket()
            client.connect((self.server_ip, 8200))
            client.send(f'Update {file_or_folder}'.encode())
            client.recv(1024)
            client.send(self.username.encode())
            client.recv(1024)
            client.send(f"{self.current_folder}|{file}".encode())
            if file_or_folder == 'file':
                client.recv(1024)
                self.send_file(client, self.path)
            else:
                self.send_all_files_in_folder(client, self.path)


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


    def send_file(self, client, full_path):
        if self.is_txt(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                length = len(content)
                client.send(f"txt|{length}".encode())
                client.recv(1024)

                client.send(content.encode())
                return

        with open(full_path, 'rb') as f:
            content = f.read()
            length = len(content)
            client.send(f"bytes|{length}".encode())
            client.recv(1024)
            
            client.send(content)


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

        if len(folder_names) > 0:
            folders = ','.join(folder_names)
        else:
            folders = 'none'
                    
        if len(file_names) > 0:
            files = ','.join(file_names)
        else:
            files = 'none'

        data = f"{folders}|{files}"
        client.send(data.encode())

        return folder_names, file_names


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


if __name__ == '__main__':
    username = sys.argv[1]
    ip = sys.argv[2]
    path = sys.argv[3]
    current_folder = sys.argv[4]
    folder = os.path.dirname(path)
    
    event_handler = MyHandler(username, path, ip, current_folder)
    observer = Observer()
    observer.schedule(event_handler, path=folder, recursive=False)        
    observer.start()

    script_path = os.path.abspath(__file__)
    try:
        while os.path.exists(script_path):
            time.sleep(5)

    except KeyboardInterrupt:
        print('An error occured')

    observer.stop()
    observer.join()
    print('Reached the end of the script')
    os.remove(sys.argv[0])