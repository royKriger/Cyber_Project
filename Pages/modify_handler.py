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
        self.is_dir = os.path.isdir(path)


    def on_modified(self, event):
        file = os.path.basename(self.path)
        event_name = os.path.basename(event.src_path)

        if self.is_dir:
            is_relevant = (
                    event.src_path == self.path or
                    event.src_path.startswith(self.path + os.sep)
            )
        else:
            is_relevant = event_name == file

        if not is_relevant:
            return

        file_or_folder = 'folder' if self.is_dir else 'file'

        client = socket.socket()
        client.connect((self.server_ip, 8200))
        client.send(f'Update {file_or_folder}'.encode())
        client.recv(1024)
        client.send(self.username.encode())
        client.recv(1024)
        client.send(f"{self.current_folder}|{file}".encode())
        client.recv(1024)
        if file_or_folder == 'file':
            self.send_file(client, self.path)
        else:
            self.send_all_files_in_folder(client, self.path)
        client.close()


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
                client.recv(1024)
                return

        with open(full_path, 'rb') as f:
            content = f.read()
            length = len(content)
            client.send(f"bytes|{length}".encode())
            client.recv(1024)
            
            client.send(content)
            client.recv(1024)


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

        folders = ','.join(folder_names) if folder_names else 'none'
        files = ','.join(file_names) if file_names else 'none'

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
    watch_dir = path if os.path.isdir(path) else os.path.dirname(path)

    event_handler = MyHandler(username, path, ip, current_folder)
    observer = Observer()

    observer.schedule(event_handler, path=watch_dir, recursive=os.path.isdir(path))
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