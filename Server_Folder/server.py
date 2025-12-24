import os
import socket
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
                else:
                    request = sock.recv(1024).decode()
                    if request == "Sign up" or request == "Log in":
                        sock.send("Joules".encode())
                        self.accept_client(sock, self.private_key, self.public_key)
                        all_sock.remove(sock)
                    elif request == "Log out":
                        all_sock.remove(sock)
                        sock.close()
                    elif request == "Get email":
                        sock.send("Joules".encode())
                        self.get_email(sock)
                        all_sock.remove(sock)
                        sock.close()
                    elif request == "Get filenames":
                        sock.send("Joules".encode())
                        self.get_filenames(sock)
                        all_sock.remove(sock)
                        sock.close()
                    else:
                        self.handle_client(sock, self.private_key, self.public_key)
                        all_sock.remove(sock)
                        sock.close()


    def accept_client(self, client, private_key, public_key):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()

        action = client.recv(1024).decode()

        client.send(f"Connected To The Server! ".encode())
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        client.sendall(public_key_pem)
        encrypted_data = client.recv(4096)

        decrypted_bytes = private_key.decrypt(
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
        
        decrypted_bytes = private_key.decrypt(
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


    def handle_client(self, client, private_key, public_key):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()

        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        client.sendall(public_key_pem)
        encrypted_data = client.recv(4096)

        decrypted_bytes = private_key.decrypt(
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

        try:
            encrypted_data = client.recv(4096)
        except:
            client.close()
            return

        decrypted_bytes = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        file_name = fr"{email}\{decrypted_bytes.decode()}"
        client.send("Joules^3".encode())
        length = int(client.recv(1024).decode())
        client.send("Joules^4".encode())

        if self.is_txt(file_name):
            encrypted_file = b''
            with open(fr"{self.path}\{file_name}", 'w') as file:
                for i in range(length):
                    encrypted_file += client.recv(1024)

                decrypted_file = b''
                for i in range(0, len(encrypted_file), 256):
                    chunk = encrypted_file[i:i + 256]
                    decrypted_file += private_key.decrypt(
                        chunk,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )
                decrypted_file = decrypted_file.decode()
                file.write(decrypted_file)

        if self.is_image(file_name):
            encrypted_image = b''
            with open(fr"{self.path}\{file_name}", 'wb') as file:
                for i in range(length):
                    encrypted_image += client.recv(1024)

                decrypted_image = b''
                for i in range(0, len(encrypted_image), 256):
                    chunk = encrypted_image[i:i + 256]
                    decrypted_image += private_key.decrypt(
                        chunk,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )

                file.write(decrypted_image)

        conn.commit()
        conn.close()

        
    def get_email(self, client):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()
        username = client.recv(1024).decode()
        conn_cur.execute("SELECT Email FROM Users WHERE User=?", (username,))
        email = conn_cur.fetchone()[0]
        client.send(email.encode())
        conn.commit()
        conn.close()


    def get_filenames(self, client):
        conn = sqlite3.connect(self.database)
        conn_cur = conn.cursor()
        username = client.recv(1024).decode()
        conn_cur.execute("SELECT Email FROM Users WHERE User=?", (username,))
        email = conn_cur.fetchone()[0].split('@')[0]

        folder_names = []
        file_names = []
        path = f"{self.path}\{email}"
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                folder_names.append(item)
            else:
                file_names.append(item)
    
        client.send(f"folder: {folder_names}, files: {file_names}".encode())


    @staticmethod
    def is_image(file_name):
        return file_name.endswith("jpeg") or file_name.endswith("jpg") or file_name.endswith("png") or file_name.endswith("gif")
    

    @staticmethod
    def is_txt(file_name):
        return file_name.endswith("TXT") or file_name.endswith("txt") or file_name.endswith("py")
    

server = Server()