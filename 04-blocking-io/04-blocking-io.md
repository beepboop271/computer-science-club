# Blocking IO & Sockets

## Python `with`

The socket examples make use of the `with` Python keyword.

```python
f = open("file.txt")
print(f.read())
raise RuntimeError("lol")
f.close()
```

In the above code, the file object is never closed because the error halts the program. If the program was longer, and there was maybe a `try` block around it, that file could remain open for a while, which isn't ideal. To solve this issue, we use a `with` block.

```python
with open("file.txt") as f:
    print(f.read())
    raise RuntimeError("lol")
```

When you create a variable `f` in the `with` block, Python will try its best to make sure `f` is closed whenever the `with` block goes out of scope (for example an error, or just whenever the code finishes running).

This works for any object that implements the `__enter__` and `__exit__` methods, such as files or sockets.

## Dotenv

`.env` files are something we will be using quite often by the time we get to JS/TS.

When writing code that will be publicly available on GitHub, it's not a good idea to hardcode passwords and API keys, unless you want random people being able to have those credentials. `.env` allows us to store configuration inside a file called `.env`, and then we can exclude the `.env` file from version control (by adding a line that says `.env` to `.gitignore`, for example). In our program, we can load the variables into our process environment variables.

For this lesson, you need to create a file named `.env` and place it in the root directory of this repository. The `.gitignore` file is already set up to exclude this file. Then, you'll need to write the following:

```text
HOST="127.0.0.1"
PORT="1234"
```

Where `HOST` contains the IP address you want to connect to with the examples (most likely localhost, unless you have a friend running the server code or something), and `PORT` contains a valid port number you want to connect over. Note that only strings can be stored in a `.env` file, since only strings can be stored in environment variables.

To load the variables stored in this file into the process environment, you `import dotenv` and call `dotenv.load_dotenv()` before you need to use the variables. To access them, you can `import os` and use `os.getenv`.

`os.getenv("HOST")` will return `"127.0.0.1"` in the above example, or `None` if dotenv wasn't able to load the variables or it wasn't set in the file. You can use a default value with a second argument: `os.getenv("HOST", "127.0.0.1")` to prevent returns of `None`.

## Sockets

Sockets are the lowest (reasonable) level of networking to be involved with. They exist between the transport and application layers: they allow you to use the transport layer (and the layers below) to send and receive arbitrary data across networks for your application.

Since they live above the transport layer, they mainly work with IP addresses, ports, and the transport protocols (and these are the 3 main things you need to create a socket).

You can imagine a socket like two one-way pipes. You can put bytes down one pipe for the other end to receive, and you can read bytes from the other pipe, which was sent from the other end.

There are two types of sockets: listening/server sockets and connection/client sockets. They are like a USB connector and port (male/female USB).

### Listening Sockets

The job of a listening socket is to listen for and accept new connections. It cannot connect to anything by itself. A listening socket is like the USB port. You can't plug the port into a port, because... it's a hole... You can only plug USB devices into the port.

Listening sockets are used on servers, because clients connect to the server, and the server doesn't connect to anyone, it just replies to clients on the connections started by the client. The listening socket listens for a new client connection, and accepts it.

Here is the code for a socket echo server in Python (an echo server sends back all data it receives to the client).

```python
import os
import socket

import dotenv
dotenv.load_dotenv()

with socket.socket() as sock:
    sock.bind(("0.0.0.0", int(os.getenv("PORT", ""))))

    sock.listen()
    print("server listening!")

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
```

(see `echo-server-verbose.py`)

When you create a socket in Python using `sock = socket.socket()`, it doesn't really exist until you call either `sock.bind` or `sock.connect`, at which point the OS gets involved to manage the socket.

`sock.bind` makes a listening socket and attaches (*binds*) it to a given address, so you need to provide an IP address and port to bind to. This code uses `"0.0.0.0"` to listen on all available addresses (the empty string `""` is also equivalent), and loads the port from the environment. Binding is a permanent operation, you need to create a new socket if you want some other port or address. By default, the socket will bind and use TCP, but you can change the protocol by passing more arguments to `sock.bind`.

Then, we call `sock.listen`, which enables listening. The socket must be a bound socket to call `sock.listen`.

Finally, we enter an infinite loop of calling `sock.accept`, which accepts an incoming connection, returning a tuple of the connection socket as well as the connection info. The socket must be bound and have listening enabled to call `sock.accept`.

### Connection Sockets

The job of a connection socket is to connect to a listening socket. It cannot listen for or accept connections. A connection socket is like a USB drive, it plugs into a USB port, not another USB drive.

Connection sockets are used on both clients and servers. The client creates a connection socket to perform the initial connection to the server's listening socket, and once the connection is accepted, the server's listening socket will return with a connection socket so that the server can interact with the client.

While listening sockets have `bind`+`listen` for setup and `accept` for normal use, connection sockets have `connect` for setup and `send`+`recv` for normal use.

Here is the code for a socket echo client in Python.

```python
import os
import socket

import dotenv
dotenv.load_dotenv()

with socket.socket() as sock:
    sock.connect((os.getenv("HOST", ""), int(os.getenv("PORT", ""))))
    print("connected!")

    while 1:
        msg = input("enter message: ")
        sock.send(msg.encode())

        print(f"received: '{sock.recv(4096).decode()}'")
```

(see `echo-client-verbose.py`)

`sock.connect` creates a connection socket and attempts to connect to a listening socket at the address `HOST:PORT` with `sock.connect((HOST, PORT))`. By default, the connection is made with TCP, but you can change the protocol by passing more arguments to `sock.connect`.

After we connect, we can then call `sock.send` and `sock.recv`.

`sock.send(msg.encode())` uses the `str.encode` method to convert our string input into a `bytes` object, and then sends the bytes to the other end of the socket.

`sock.recv(4096).decode()` receives a `bytes` buffer up to 4096 bytes long from the socket (sent from the other end), and converts it into a string.

By default, `str.encode` and `str.decode` use UTF-8 bytes.

Going back to our echo server, the `sock.accept` method on a listening socket would return a connection socket in the `conn` variable, so now we can look at that:

```python
conn, addr = sock.accept()
print(f"received connection from {addr}")
while 1:
    data = conn.recv(4096)
    if data == b"":
        break
    print(f"echoing: '{data.decode()}'")
    conn.send(data)
print(f"connection from {addr} ended")
```

We enter an infinite loop that just receives bytes, prints them out, and sends them right back to the client. We just have a little `if` statement that checks if the data received is equal to an empty bytes object. This will happen if the connection is closed, so that means we can break out of the echo loop.

## Blocking Calls

***THIS PART IS REALLY IMPORTANT***

If we had the following code:

```python
while 1:
    conn, addr = sock.accept()
    print("infinite loop weeee")
```

Nothing would be printed, unless we ran our client program to connect to the listening socket. We could perform the same test with the infinite `recv` and `send` loops, the print would only happen once we actually send data to the socket.

```python
while 1:
    data = sock.recv(4096)
    print("infinite loop weeee")
    sock.send(data)
```

This is because `sock.accept`, `sock.recv`, and `sock.send` (in their default modes) are all considered to be something called a blocking operation. `sock.connect` is also blocking, bind and listen are also probably blocking, but connect, bind, and listen are only used once in a program so we won't talk about them too much.

Bringing back this text diagram from last lesson, we can investigate what is happening.

```text
sock.accept()
|       ^
v       |
Some more software
|       ^
v       |
Network devices

sock.recv()
|       ^
v       |
Some more software
|       ^
v       |
Network devices
```

Between Python lies the CPython and OS layers, but ultimately at the bottom we're **waiting** on the physical network devices to return data to us (or tell us that the data has been sent). When we're waiting, **none of our code is being run**, like the print statements. We have no clue how long we'll need to wait for. There might be data already waiting for us to read, or the client might not send us anything for another 10 minutes. **Since we wait and do nothing until the I/O completes, the operations are considered to be blocking**.

Why is this bad?

```python
while 1:
    conn, addr = sock.accept()
    data = []
    chunk = b""
    while b"done" not in chunk:
        chunk = conn.recv(4096)
        data.append(chunk.decode())
    print("".join(data))
```

This server accepts a connection and continues receiving data until the characters `"done"` appear in the data somewhere. This could take a while. The byte and string processing code runs fairly quickly, but the `recv` call could eat up minutes of time. Since a client can only establish a connection with the server once the server calls `sock.accept`, a client could be waiting for an unknown amount of time until the server is done with the current client.

That means this server code can handle *one* concurrent user. How can we handle 1000? 10000? 100000? or 1000000? We shall see...

As mentioned before, the byte and string processing code runs quickly compared to all the time spent waiting on the blocking `recv` call. What if we could be accepting new connections in the downtime, instead of doing nothing at all? If we had 100 clients, all sending data at the same time, could we swap between each client, always processing someone's data while waiting on the other clients? The answer is definitely yes.

Blocking happens with file IO too, not just network IO. Reading in 1 gigabyte off a hard drive will definitely take some time, so your program will block and wait until it's done.

## Exercise

Open `04-activity.py`, which contains the code for a tic-tac-toe socket server. At the top is a comment containing an overview of the network messages being sent between the server and the client. Implement the client and a basic console interface to play the game. Do pay attention to the specification: note that the win/lose/tie processing happens on the server, the client does nothing for that.
