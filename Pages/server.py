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
        self.path = r"C:\Users\roykr\Cyber_Project\ServerFiles"
        self.database = r"C:\Users\roykr\Cyber_Project\drive_db.sqlite"

        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        self.public_key = self.private_key.public_key()

        all_sock = [self.server]
        while True:
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
                    else:
                        sock.send("Joules^2".encode())
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

        username = client.recv(1024).decode()
        client.send("Joules^3".encode())

        conn_cur.execute("SELECT Email FROM Users WHERE User=?", (username,))
        email = conn_cur.fetchone()[0].split('@')[0]

        file_name = fr"{email}\{client.recv(1024).decode()}"
        client.send("Joules^4".encode())
        length = int(client.recv(1024).decode())
        client.send("Joules^5".encode())

        if self.is_txt(file_name):
            content = ""
            with open(fr"{self.path}\{file_name}", 'w') as file:
                for i in range(length):
                    content += client.recv(1024).decode()
                file.write(content)

        if self.is_image(file_name):
            content = b''
            with open(fr"{self.path}\{file_name}", 'wb') as file:
                for i in range(length):
                    content += client.recv(1024)
                file.write(content)

        
    @staticmethod
    def is_image(file_name):
        return file_name.endswith("jpeg") or file_name.endswith("jpg") or file_name.endswith("png")
    

    @staticmethod
    def is_txt(file_name):
        return file_name.endswith("TXT") or file_name.endswith("txt") or file_name.endswith("py")
    

server = Server()