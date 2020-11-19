import os
import socket

import dotenv

dotenv.load_dotenv()

# create a socket
with socket.socket() as sock:
    # don't bind/listen the socket because we don't want
    # to be accepting connections, we want to be connecting.
    # thus, we use the connect call
    sock.connect((os.getenv("HOST", ""), int(os.getenv("PORT", ""))))
    print("connected!")

    while 1:
        msg = input("enter message: ")
        # send bytes to the other end
        sock.send(msg.encode())

        # receive bytes and decode assuming utf-8
        print(f"received: '{sock.recv(4096).decode()}'")
