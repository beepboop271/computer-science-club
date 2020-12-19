import os
import socket
import threading
from typing import List

import dotenv
dotenv.load_dotenv()


# create a function that will be called every time we get a
# new client, taking their socket connection
def handle(conn: socket.socket, addr):
    # same as echo-server.py from lesson 04
    print(f"received connection from {addr}")
    while 1:
        data = conn.recv(4096)
        if data == b"":
            break
        print(f"echoing: '{data.decode()}'")
        conn.send(data)
    print(f"connection from {addr} ended")


# keep a list because why not
pool: List[threading.Thread] = []

with socket.create_server(
    ("", int(os.getenv("PORT", "")))
) as sock:
    print("server listening!")

    # accept requests in an infinite loop but don't block the
    # server accepting loop when handling clients
    while 1:
        # blocks until someone connects
        info = sock.accept()

        thread = threading.Thread(
            # function to run in the thread (remember lesson 02)
            target=handle,
            # argument tuple
            args=info,
            # daemon thread means that it won't keep the whole
            # program alive if the main program has ended
            # (normal threads would continue to be run, even
            # when the main thread has ended)
            daemon=True,
        )
        # actually start running the function in a new thread
        # (call the function but continue running this loop)
        thread.start()

        pool.append(thread)
