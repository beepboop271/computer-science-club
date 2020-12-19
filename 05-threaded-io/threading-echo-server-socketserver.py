import os
import socketserver

import dotenv
dotenv.load_dotenv()


# extend the TCP request handler
class EchoHandler(socketserver.StreamRequestHandler):
    # function that will be called on each new client connection
    def handle(self):
        # same as echo-server.py from lesson 04
        print(f"received connection from {self.client_address}")
        while 1:
            data = self.request.recv(4096)
            if data == b"":
                break
            print(f"echoing: '{data.decode()}'")
            self.request.send(data)
        print(f"connection from {self.client_address} ended")


# create a TCP server that creates a new thread for each client
# connection with the given request handler
with socketserver.ThreadingTCPServer(
    ("", int(os.getenv("PORT", ""))), EchoHandler
) as server:
    # start the infinite loop of accepting and starting
    server.serve_forever()
