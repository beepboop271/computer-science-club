import os
import socket

import dotenv

dotenv.load_dotenv()

# create and connect in one go - not much simpler than
# the "verbose" example but whatever
with socket.create_connection((os.getenv("HOST", ""), int(os.getenv("PORT", "")))) as sock:
    print("connected!")
    while 1:
        msg = input("enter message: ")
        sock.send(msg.encode())
        print(f"received: '{sock.recv(4096).decode()}'")
