import socket
import sqlite3
from threading import Thread
import base64
import bcrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def accept_client(client, private_key, public_key):
    conn = sqlite3.Connection(r"C:\Users\Roy\Desktop\Cyber_Project\drive_db.sqlite")
    
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
                data = "500"
        else:
            data = "500"

    if action == "register":
        user, email, password = decrypted_data[0], decrypted_data[1], base64.b64decode(decrypted_data[2])
        conn_cur.execute("SELECT Email FROM Users")
        emails = conn_cur.fetchall()
        if (email,) in emails:
            data = "500"
        else:
            conn_cur.execute("INSERT INTO Users (User, Email, Password) VALUES (?, ?, ?)",
    (user, email, password))
            #with open(f"{Utilities.generate_id(email.split('@')[0])}") as file:

    client.send(data.encode())

    if data == "200":
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

if __name__ == "__main__":
    server = socket.socket()
    server.bind(("0.0.0.0", 8200))
    server.listen(5)

    private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
    )

    public_key = private_key.public_key()

    while True:
        (client, client_address) = server.accept()
        handle = Thread(target=accept_client, args=(client, private_key, public_key))
        handle.start()

