# Threading IO

## Recap

Last lesson involved looking at how sockets need to wait on network IO, and the fact that our server implementation could only support one client at a time.

Since `recv` represents the reception of data from (for example) a completely different computer, it is unknown how long it would take before they send data.

This resulted in our code getting stuck waiting for `recv` often, preventing it from calling `accept`, which is what actually allows us to connect a new client.

Ideally, we could have some system that allows us to be waiting on `accept` and `recv` at the same time, preventing us from missing out on one being ready because we are waiting on the other. We want our program to just start handling the client when `accept` is ready, while also performing appropriate data processing when `recv` is ready, with as minimal latency as possible.

We'll look at how threads can help us achieve this.

## Threads

A simple program consists of the sequential execution of instructions. Though things like loops and branches cause jumps around in code, we can still look at the actual path of execution as a single line of instructions. Consider this 'line of execution' as a single thread or string of fabric.

Each program is executing its own sequence of instructions, which means each program has a single thread of fabric executing/running.

```python
print("hello")
print(5)
print("bye")
```

Running the above code would start a new Python program (Python process), which contains a main thread, which would execute the first line, then the second line, then the third line.

### Context Switching

Programs run on the operating system, and the whole computer runs on a CPU that has a certain number of cores. If each core is able to process one instruction at a time (though modern CPUs are far more complex), and you have 4 cores, you could only be running 4 threads of execution.

However, since having a maximum of 4 programs open at once is not very convenient, the OS manages each program's threads by repeatedly switching what thread is actually running on the available CPU. For example, one program might run on one core for 10 ms, then the OS swaps it out for a second program, and then for a third one after 90 ms, etc. Each swap of the currently running thread is called a context switch, since it's a switch of the execution context, or environment (function stack, local variables, global variables, registers, etc).

To each running program, context switches are invisible, since no memory or data within each program is modified, and the thread of execution resumes at the exact instruction it left off at.

Of course, there is a performance penalty to context switches, since it takes a bit of time to swap out the data of each program.

### Starting multiple threads

If you're on Windows 10 and you open the CPU Performance menu in Task Manager (there may be a similar equivalent in other operating systems), you can see some counts of active processes and threads. At the time of writing, I have about 390 processes and 4650 threads running. Clearly, there are multiple threads per process.

It is possible for one program to spawn many threads. Even if the CPU does not have enough cores to work on them all, the OS can switch between each thread of a program just like they were threads of different programs.

However, unlike threads between multiple programs, which are totally independent, threads spawned by the same parent process share common memory, though their call stacks are still independent. This means you could interact with the same global variable across many threads of a program, though you wouldn't be able to access that variable from another program.

The fact that the call stacks are separate means that multiple threads of a program can each be inside the same function with different local variables or inside entirely different functions, all at the same time, even if they're not guaranteed to be running at the exact same time. On a larger timescale, the various threads will appear to be running at the same time.

The fact that two threads might try to access/modify a shared object at the same time and the issues that arise are not in the scope of this lesson (read on locking, synchronization, data races...).

If we can spawn many threads under a single program, and allow the OS to manage when each thread is being executed and which thread is suspended, we can try to solve our concurrent client problem.

## Threading Servers

A threading server creates a new thread for each new client connection, or maintains a pool of threads to work through client requests on.

By creating threads, when a single client handler is blocked on a `recv`, the OS can then suspend that thread and switch contexts to another thread, for example the server main loop (that calls `accept`) or to another client handler (to see if `recv` is done or not). There can be 1000 threads, each thread inside the same client handling function, executing the echoing code, but with different call stacks and thus different local variables, to deal with different clients.

From `threading-echo-server-pure.py`:

```python
import os
import socket
import threading
from typing import List

import dotenv
dotenv.load_dotenv()
```

Imports. Note the import for `threading`, which is new. This is the standard library module that allows us to create new threads of execution.

```python
def handle(conn: socket.socket, addr):
    print(f"received connection from {addr}")
    while 1:
        data = conn.recv(4096)
        if data == b"":
            break
        print(f"echoing: '{data.decode()}'")
        conn.send(data)
    print(f"connection from {addr} ended")
```

The same client handling code from before that repeatedly echoes data, except this time inside a function which takes the return value of `accept` as arguments. We want to have this function run in many different threads, so that the blocking `recv` will not prevent other client handlers from running.

```python
pool: List[threading.Thread] = []

with socket.create_server(("", int(os.getenv("PORT", "")))) as sock:
    print("server listening!")

    while 1:
        info = sock.accept()

        thread = threading.Thread(
            target=handle,
            args=info,
            daemon=True,
        )
        thread.start()

        pool.append(thread)
```

This is the real threading part of the server. We create the listening socket as usual, and then enter an infinite `accept` loop. However, after `accept`, instead of directly calling our client handler, we first do `thread = threading.Thread(target=handle, args=info, daemon=True)`. This creates a `Thread` object that represents a new thread of execution (which has yet to start). `target` specifies what function will be run inside the new thread, `args` is a tuple of arguments for the `target`, and the `daemon` argument specifies that the thread should be a daemon thread.

A daemon thread is a thread in a program that does not prevent the program from exiting. If a program runs its main thread and finishes executing, the program will still run if a non-daemon thread was spawned and is still running. However, once the only remaining threads are daemon threads (running or not), the program ends.

Once we call `thread.start()`, Python creates a new thread of execution to call the `handle` function in. We append the thread to our list, and go back to the top of the loop. This process of creating and starting a thread between completing `accept` and going back to block on `accept` again takes a very short amount of time.

By using threads, we are effectively able to block on `accept` and `recv`s at the same time, solving the issue from last lesson.
