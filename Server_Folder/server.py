import os
import socket
import shutil
import select
import bcrypt
import sqlite3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class Server():
    def __init__(self):
        self.timeout = 2.0
        self.server = socket.socket()
        self.server.bind(("0.0.0.0", 8200))
        self.server.listen(5)
        self.path = r"Server_Folder\ServerFiles"
        self.database = r"Server_Folder\drive_db.sqlite"
        self.text_files, self.bytes_files = [], []

        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        self.public_key = self.private_key.public_key()

        all_sock = [self.server]
        while self.server:
            rList, _, _ = select.select(all_sock, all_sock, [])
            for sock in rList:
                if sock == self.server:
                    client, client_addr = self.server.accept()
                    all_sock.append(client)
                    client.settimeout(self.timeout)
                else:
                    try:
                        request = sock.recv(1024).decode()
                        if request == "Remember me":
                            sock.send("Joules".encode())
                            self.returned_client(sock)
                            all_sock.remove(sock)
                        elif request == "Sign up" or request == "Log in":
                            sock.send("Joules".encode())
                            self.accept_client(sock)
                            all_sock.remove(sock)
                        elif request == "Log out":
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
            email, password = decrypted_data[0], decrypted_data[1].encode()
            if len(decrypted_data) > 2:
                conn_cur.execute("SELECT User FROM Users WHERE Email=?", (email,))
                username = conn_cur.fetchone()[0]
                login_id = bcrypt.hashpw(username.encode(), bcrypt.gensalt()).decode()
                print(login_id)
                conn_cur.execute("UPDATE Users SET login_ID=? WHERE Email=?", (login_id, email))
                data += '|' + login_id
            conn_cur.execute("SELECT Email FROM Users")
            emails = conn_cur.fetchall()
            if (email, ) in emails:
                conn_cur.execute(f"SELECT Password FROM Users WHERE Email=?", (email,))
                db_pass = conn_cur.fetchone()[0].encode()
                if not bcrypt.checkpw(password, db_pass):
                    data = "501|Password or email not correct! "
            else:
                data = "502|Email does not exist! "

        if action == "register":
            user, email, password = decrypted_data[0], decrypted_data[1], decrypted_data[2]
            conn_cur.execute("SELECT Email FROM Users")
            emails = conn_cur.fetchall()
            conn_cur.execute("SELECT User FROM Users")
            users = conn_cur.fetchall()
            if (user,) in users:
                data = "500|Username already exists! "
            elif user == "Admin":
                data = "503|Can't have this username! "
            elif (email,) in emails:
                data = "500|Email already exists! "
            else:
                if len(decrypted_data) > 3:
                    login_id = bcrypt.hashpw(user.encode(), bcrypt.gensalt()).decode()
                    conn_cur.execute("INSERT INTO Users (User, Email, Password, login_ID) VALUES (?, ?, ?, ?)",
                (user, email, password, login_id))
                    print(login_id)
                    data += '|' + login_id
                else:
                    conn_cur.execute("INSERT INTO Users (User, Email, Password) VALUES (?, ?, ?)",
                (user, email, password))
                os.mkdir(f"{self.path}\\{email.split('@')[0]}")

        client.send(data.encode())
        if data.startswith("50"):
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


    def returned_client(self, client):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()

        token = client.recv(1024).decode()

        conn_cur.execute("SELECT User FROM Users WHERE login_ID=?", (token,))
        username = conn_cur.fetchone()[0]
        client.send(username.encode())

        conn.commit()
        conn.close()


    def handle_file(self, client : socket.socket):
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
        file_name = decrypted_bytes.decode()
        full_path = os.path.join(self.path, email)

        if '\\' in file_name:
            path = '\\'.join(file_name.split('\\')[:-1])
            file_name = file_name.split('\\')[-1]
            full_path = os.path.join(full_path, path)

        if self.if_item_exists_dir(file_name, full_path, False):
            client.send('exists!'.encode())
            client.settimeout(None)
            replace = client.recv(1024).decode() == "Replace file"
            if not replace:
                return
            client.settimeout(self.timeout)
            os.remove(os.path.join(full_path, file_name))

        self.get_file(client, file_name, full_path)

        conn.commit()
        conn.close()


    def handle_folder(self, client : socket.socket):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()

        client.send("Joules^2".encode())
        username = client.recv(1024).decode()
        client.send("Joules^2".encode())

        conn_cur.execute("SELECT Email FROM Users WHERE User=?", (username,))
        email = conn_cur.fetchone()[0].split('@')[0]

        folder_name = client.recv(1024).decode()
        full_path = os.path.join(self.path, email)

        if '\\' in folder_name:
            path = '\\'.join(folder_name.split('\\')[:-1])
            folder_name = folder_name.split('\\')[-1]
            full_path = os.path.join(full_path, path)

        if self.if_item_exists_dir(folder_name, full_path, True):
            client.send('exists!'.encode())
            client.settimeout(None)
            replace = client.recv(1024).decode() == "Replace folder"
            if not replace:
                return
            client.settimeout(self.timeout)
            shutil.rmtree(os.path.join(full_path, folder_name))
        client.send('doesnt exist'.encode())

        full_path = os.path.join(full_path, folder_name)
        os.mkdir(full_path)
        self.recieve_all_files_and_folders(client, full_path)

        conn.commit()
        conn.close()

    
    def recieve_all_files_and_folders(self, client, full_path):
        folders, files = self.get_all_filenames(client)
        if not folders:
            for item in files:
                self.get_file(client, item, full_path)
            return

        for folder in folders:
            path = os.path.join(full_path, folder)
            os.mkdir(path)
            for item in files:
                self.get_file(client, item, full_path)
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


    def get_file(self, client, file, full_path):
        client.send("Joules".encode())
        data = client.recv(1024).decode()
        try:
            extension, length = data.split('|')[0], int(data.split('|')[-1])
        except TypeError:
            raise(TimeoutError)
        client.send("Joules1".encode())

        print(file, length)

        path = os.path.join(full_path, file)
        file_content = client.recv(length)
        while len(file_content) < length:
            file_content += client.recv(length)

        if extension == 'txt':
            file_content = file_content.decode()
            with open(path, 'w') as file:
                file.write(file_content)
            self.text_files.append(path)

        else:
            with open(path, 'wb') as f:
                f.write(file_content)
            if self.is_image(path):
                self.bytes_files.append(path)


    def send_filenames(self, client):
        email = self.get_email(client)
        self.text_files, self.bytes_files = [], []

        client.send("Joules".encode())
        folder = client.recv(1024).decode()
        path = os.path.join(self.path, email)
        folder, check = folder.split("\n")
        if check:
            path = os.path.join(path, folder)
        
        _, files = self.get_and_send_folders_and_files(client, path)
        for file in files:
            full_path = os.path.join(path, file)
            if self.is_txt(full_path):
                self.text_files.append(full_path)
            else:
                if self.is_image(full_path):
                    self.bytes_files.append(full_path)


    def get_file_or_folder(self, client, request):
        email = self.get_email(client)
        client.send("Joules^2".encode())

        file_name = client.recv(1024).decode()
        
        path = fr"{self.path}\{email}"

        if request.endswith("folder"):
            path = os.path.join(path, file_name)
            self.send_all_files_in_folder(client, path)
            return
        
        client.send("Joules1".encode())
        self.send_all_files(client, path, file_name)
        
    
    def send_all_files(self, client, folder_path, file):
        client.recv(1024)
        
        full_path = os.path.join(folder_path, file)
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


    def remove_file(self, client):
        email = self.get_email(client)
        client.send("Joules^2".encode())

        file_name = client.recv(1024).decode()

        path = os.path.join(self.path, email, file_name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            if self.is_txt(path):
                self.text_files.remove(path)
            else:
                self.bytes_files.remove(path)
            os.remove(path)

    
    def get_email(self, client):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()
        username = client.recv(1024).decode()
        
        conn_cur.execute("SELECT Email FROM Users WHERE User=?", (username,))
        email = conn_cur.fetchone()[0]

        conn.commit()
        conn.close()

        return email.split('@')[0]
        

    def if_item_exists_dir(self, file_name, full_path, file_or_folder):
        items = os.listdir(full_path)
        file_names = []
        
        for item in items:
            current_path = os.path.join(full_path, item)
            if file_or_folder:
                if os.path.isdir(current_path):
                    file_names.append(item)
            else:
                if not os.path.isdir(current_path):
                    file_names.append(item)

        files = ','.join(file_names)
        if file_name in files:
            return True

        return False


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
    

    def is_image(self, path):
        extension = path.split('.')[-1]
        return extension.lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'avif', 'bmp', 'tiff', 'jfif']


server = Server()
