import socket
import sqlite3
from threading import Thread


def accept_client(client):
    conn = sqlite3.Connection(r"C:\Users\Roy\Desktop\Cyber_Project\drive_db.sqlite")
    
    conn_cur = conn.cursor()

    data = client.recv(1024).decode()
    client.send("Connected! ".encode())
    
    if data == "login":
        data = client.recv(1024).decode()
        data = data.split(',')
        email, password = data[0], data[1]
        print(conn_cur.execute("SELECT Email FROM Users WHERE email='roy.kriger@gmail.com'"))
    
    if data == "register":
        data = client.recv(1024).decode()
        data = data.split(',')
        user, email, password = data[0], data[1], data[2]
        conn_cur.execute(f"SELECT Email FROM Users")
        emails = conn_cur.fetchall()
        if email in emails:
            client.send("Error ".encode())
        else:
            conn_cur.execute("INSERT INTO Users (User, Email, Password) VALUES (?, ?, ?)",
    (user, email, password))
            client.send("200".encode())
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    server = socket.socket()
    server.bind(("0.0.0.0", 8200))
    server.listen()
    (client, client_address) = server.accept()
    handle = Thread(target=accept_client, args=(client, ))
    handle.start()
