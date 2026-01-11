import os
import socket
import shutil
import sqlite3
import select
import base64
import bcrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class Server():
    def __init__(self):
        self.server = socket.socket()
        self.server.bind(("0.0.0.0", 8200))
        self.server.listen(5)
        self.path = r"Server_Folder\ServerFiles"
        self.database = r"Server_Folder\drive_db.sqlite"

        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        self.public_key = self.private_key.public_key()

        all_sock = [self.server]
        while self.server:
            rList, wList, xList = select.select(all_sock, all_sock, [])
            for sock in rList:
                if sock == self.server:
                    client, client_addr = self.server.accept()
                    all_sock.append(client)
                    client.settimeout(2.0)
                else:
                    try:
                        request = sock.recv(1024).decode()
                        if request == "Sign up" or request == "Log in":
                            sock.send("Joules".encode())
                            self.accept_client(sock)
                            all_sock.remove(sock)
                        elif request == "Log out":
                            all_sock.remove(sock)
                            sock.close()
                        elif request == "Get email":
                            sock.send("Joules".encode())
                            self.send_email(sock)
                            all_sock.remove(sock)
                            sock.close()
                        elif request == "Get filenames":
                            sock.send("Joules".encode())
                            self.send_filenames(sock)
                            all_sock.remove(sock)
                            sock.close()
                        elif request == "Get folder" or request == "Get file":
                            sock.send("Joules".encode())
                            self.get_file_or_folder(sock, request)
                            all_sock.remove(sock)
                            sock.close()
                        elif request == "Remove file":
                            sock.send("Joules".encode())
                            self.remove_file(sock)
                            all_sock.remove(sock)
                            sock.close()
                        elif request == "Upload file":
                            self.handle_file(sock)
                            all_sock.remove(sock)
                            sock.close()
                        elif request == "Upload folder":
                            self.handle_folder(sock)
                            all_sock.remove(sock)
                            sock.close()
                    except TimeoutError:
                        all_sock.remove(sock)
                        sock.close()

    def accept_client(self, client):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()

        action = client.recv(1024).decode()

        client.send(f"Connected To The Server! ".encode())
        public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        client.sendall(public_key_pem)
        encrypted_data = client.recv(4096)

        decrypted_bytes = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        decrypted_data = decrypted_bytes.decode().split(',')

        data = "200"
        if action == "login":
            email, password = decrypted_data[0], decrypted_data[1]
            conn_cur.execute("SELECT Email FROM Users")
            emails = conn_cur.fetchall()
            if (email, ) in emails:
                conn_cur.execute(f"SELECT Password FROM Users WHERE Email='{email}'")
                db_pass = conn_cur.fetchone()[0]
                if not bcrypt.checkpw(password.encode(), db_pass):
                    data = "500|Password or email not correct! "
            else:
                data = "500|Email does not exist! "

        if action == "register":
            user, email, password = decrypted_data[0], decrypted_data[1], base64.b64decode(decrypted_data[2])
            conn_cur.execute("SELECT Email FROM Users")
            emails = conn_cur.fetchall()
            conn_cur.execute("SELECT User FROM Users")
            users = conn_cur.fetchall()
            if (user,) in users:
                data = "500|Username already exists! "
            elif user == "Admin":
                data = "500|Can't have this username! "
            elif (email,) in emails:
                data = "500|Email already exists! "
            else:
                conn_cur.execute("INSERT INTO Users (User, Email, Password) VALUES (?, ?, ?)",
        (user, email, password))
                os.mkdir(f"{self.path}\\{email.split('@')[0]}")

        client.send(data.encode())
        if data.startswith("500"):
            return

        encrypted_data = client.recv(4096)

        decrypted_bytes = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        action = decrypted_bytes.decode()
        if action.startswith("logged in"):
            email = action.split(',')[1]
            conn_cur.execute("SELECT User FROM Users WHERE Email=?", (email,))
            username = conn_cur.fetchone()[0]
            client.send(username.encode())

        conn.commit()
        conn.close()


    def handle_file(self, client):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()

        public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        client.sendall(public_key_pem)
        encrypted_data = client.recv(4096)
        
        decrypted_bytes = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        client.send("Joules^2".encode())

        username = decrypted_bytes.decode()
        conn_cur.execute("SELECT Email FROM Users WHERE User=?", (username,))
        email = conn_cur.fetchone()[0].split('@')[0]

        encrypted_data = client.recv(4096)
        
        decrypted_bytes = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        file_name = fr"{email}\{decrypted_bytes.decode()}"
        full_path = os.path.join(self.path, file_name)

        client.send("Joules^3".encode())
        data = client.recv(1024).decode()
        try:
            type, length = data.split('|')[0], int(data.split('|')[-1])
        except TypeError:
            raise(TimeoutError)

        client.send("Joules^4".encode())
        
        if type == 'txt':
            file_content = client.recv(length).decode()

            with open(full_path, 'w') as file:
                file.write(file_content)

            return
            
        file_content = client.recv(length)

        with open(full_path, 'wb') as file:
            file.write(file_content)

        conn.commit()
        conn.close()


    def handle_folder(self, client):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()

        client.send("Joules^2".encode())
        username = client.recv(1024).decode()
        client.send("Joules^2".encode())

        conn_cur.execute("SELECT Email FROM Users WHERE User=?", (username,))
        email = conn_cur.fetchone()[0].split('@')[0]

        folder_name = client.recv(1024).decode()

        path = fr"{email}\{folder_name}"
        client.send("Joules".encode())

        full_path = os.path.join(self.path, path)
        os.mkdir(full_path)
        
        self.recieve_all_files_and_folders(client, full_path)

        conn.commit()
        conn.close()

    
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
            client.send("Joules".encode())
            data = client.recv(1024).decode()
            try:
                type, length = data.split('|')[0], int(data.split('|')[-1])
            except TypeError:
                raise(TimeoutError)
            client.send("Joules1".encode())

            print(item, length)

            path = os.path.join(full_path, item)
            
            file_content = client.recv(length)
            while len(file_content) < length:
                file_content += client.recv(length)

            if type == 'txt':
                file_content = file_content.decode()
                with open(path, 'w') as file:
                    file.write(file_content)

            else:
                with open(path, 'wb') as file:
                    file.write(file_content)

        
    def send_email(self, client):
        email = self.get_email(client)
        client.send(email.encode())


    def send_filenames(self, client):
        email = self.get_email(client).split('@')[0]

        client.send("Joules".encode())
        folder_names = []
        file_names = []
        folder = client.recv(1024).decode()
        path = fr"{self.path}\{email}"
        folder, check = folder.split("\n")
        if check:
            path = os.path.join(path, folder)
        
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                folder_names.append(item)

            else:
                file_names.append(item)

        files = ','.join(file_names)
        folders = ','.join(folder_names)

        if folders == '':
            client.send("none".encode())
        else:
            client.send(folders.encode())

        client.recv(1024)
        
        if files == '':
            client.send("none".encode())
        else:
            client.send(files.encode())
    

    def get_file_or_folder(self, client, request):
        email = self.get_email(client).split('@')[0]
        client.send("Joules^2".encode())

        file_name = client.recv(1024).decode()
        
        path = fr"{self.path}\{email}"

        if request.endswith("folder"):
            path = os.path.join(path, file_name)
            self.send_all_files_in_folder(client, path)
            return
        
        client.send("Joules1".encode())
        self.send_all_files(client, path, [file_name])
        
    
    def send_all_files(self, client, folder_path, files):
        for item in files:
            client.recv(1024)
            
            full_path = os.path.join(folder_path, item)
            if self.is_txt(full_path):
                with open(full_path, 'r') as file:
                    content = file.read()
                    length = len(content)
                    client.send(f"txt|{length}".encode())
                    client.recv(1024)
                    client.send(content.encode())

            else:
                with open(full_path, 'rb') as file:
                    content = file.read()
                    length = len(content)
                    client.send(f"bytes|{length}".encode())
                    client.recv(1024)
                    
                    client.send(content)
            
    
    def send_all_files_in_folder(self, client, folder_path):
        folders, files = self.get_and_send_folders_and_files(client, folder_path)
        if not folders:
            self.send_all_files(client, folder_path, files)
            return
        
        for folder in folders:
            path = os.path.join(folder_path, folder)
            self.send_all_files(client, folder_path, files)
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


    def remove_file(self, client):
        email = self.get_email(client).split('@')[0]
        client.send("Joules^2".encode())

        file_name = client.recv(1024).decode()

        path = fr"{self.path}\{email}\{file_name}"
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    
    def get_email(self, client):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()
        username = client.recv(1024).decode()
        
        conn_cur.execute("SELECT Email FROM Users WHERE User=?", (username,))
        email = conn_cur.fetchone()[0]

        conn.commit()
        conn.close()

        return email
        

    @staticmethod
    def is_txt(path):
        with open(path, "rb") as file:
            chunk = file.read(4096)

        if b"\x00" in chunk:
            return False

        try:
            chunk.decode()
            return True
        except UnicodeDecodeError:
            return False
    

server = Server()
