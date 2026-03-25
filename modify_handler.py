import os
import time
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    def __init__(self, path, ip, path_to_upload):
        super().__init__()
        self.path = path
        self.server_ip = ip
        self.path_to_upload = path_to_upload


    def on_modified(self, event):
        file = self.path.split('\\')[-1]

        if event.src_path.endswith(file):
            client = socket.socket()
            client.connect((self.server_ip, 8200))
            client.send('Update file'.encode())


if __name__ == '__main__':
    ip = '127.0.0.1'
    path = r'C:\Users\roykr\Desktop'
    folder = '\\'.join(path.split('\\')[:-1])

    event_handler = MyHandler(path, ip, '')
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