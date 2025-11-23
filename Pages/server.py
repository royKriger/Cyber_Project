import socket
import sqlite3
from threading import Thread
import bcrypt
from utilities import Utilities


def accept_client(client):
    conn = sqlite3.Connection(r"C:\Users\roykr\Cyber_Project\Cyber_Project\drive_db.sqlite")
    
    conn_cur = conn.cursor()

    type = client.recv(1024).decode()
    client.send("Connected To The Server! ".encode())
    data = client.recv(4096).decode()
    parts = data.split(',')

    if type == "login":
        email, password = parts[0], parts[1]
        conn_cur.execute("SELECT Email FROM Users")
        emails = conn_cur.fetchall()
        if (email, ) in emails:
            conn_cur.execute(f"SELECT Password FROM Users WHERE Email='{email}'")
            db_pass = conn_cur.fetchone()[0]
            if bcrypt.checkpw(password.encode(), db_pass.encode()):
                client.send("200".encode())
            else:
                client.send("500".encode())
        else:
            client.send("500".encode())

    if type == "register":
        user, email, password = parts[0], parts[1], parts[2]
        conn_cur.execute("SELECT Email FROM Users")
        emails = conn_cur.fetchall()
        if (email,) in emails:
            client.send("500 Email already exists!".encode())
        else:
            conn_cur.execute("INSERT INTO Users (User, Email, Password) VALUES (?, ?, ?)",
    (user, email, password))
            client.send("200".encode())
            with open(f"{Utilities.generate_id(email.split('@')[0])}") as file:

    type = client.recv(1024).decode()
    if type.startswith("logged in"):
        email = type.split(',')[1]
        conn_cur.execute("SELECT User FROM Users WHERE Email=?", (email,))
        username = conn_cur.fetchone()[0]
        client.send(username.encode())
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    server = socket.socket()
    server.bind(("0.0.0.0", 8200))
    server.listen(5)
    while True:
        (client, client_address) = server.accept()
        handle = Thread(target=accept_client, args=(client, ))
        handle.start()
