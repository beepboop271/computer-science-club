import os
import socket

import dotenv

dotenv.load_dotenv()

# create, bind, and listen on a socket in one go.
# in addition, using an empty string is equal to 0.0.0.0
with socket.create_server(("", int(os.getenv("PORT", "")))) as sock:
    print("server listening!")

    # everything else is identical
    while 1:
        conn, addr = sock.accept()
        print(f"received connection from {addr}")
        while 1:
            data = conn.recv(4096)
            if data == b"":
                break
            print(f"echoing: '{data.decode()}'")
            conn.send(data)
        print(f"connection from {addr} ended")
