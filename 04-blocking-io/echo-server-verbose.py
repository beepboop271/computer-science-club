import os
import socket

import dotenv

dotenv.load_dotenv()

# creates a socket with default settings and type,
# which by default can connect to some ip and port.
# use a with statement, which will ensure sock is
# properly closed in almost all exit scenarios
with socket.socket() as sock:
    # permanently attaches the socket to the given address
    # which will allow the socket to listen
    sock.bind(("0.0.0.0", int(os.getenv("PORT", ""))))

    # enables the socket to accept connections. connections
    # are accepted on the bound address, so the socket must
    # be bound already
    sock.listen()
    print("server listening!")

    while 1:
        # accept a new connection, the socket must be bound
        # and listening to accept a connection
        conn, addr = sock.accept()
        print(f"received connection from {addr}")
        # keep echoing data for as long as possible
        while 1:
            data = conn.recv(4096)
            # sock.recv returns with an empty buffer if the
            # conn is closed
            if data == b"":
                break
            # assume we are handling UTF-8 (unicode text)
            print(f"echoing: '{data.decode()}'")
            conn.send(data)
        print(f"connection from {addr} ended")
