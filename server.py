import socket
import sqlite3


class Server(socket.socket):
    def __init__(self):
        super().__init__()
        self.bind(("0.0.0.0", 8200))
        self.listen()
        (client_socket, client_address) = self.accept()


    def accept_client(self):
        conn = sqlite3.connect(r"C:\Users\Pc2\Desktop\Cyber_Project\drive_db.sqlite")
        conn.commit()

        conn_cur = conn.cursor()


        data = self.recv(1024).decode()
        email = data.split(',')[0]
        password = data.split(',')[1]
        print(conn_cur.execute("SELECT Email FROM Users WHERE Email = {email}"))
        
