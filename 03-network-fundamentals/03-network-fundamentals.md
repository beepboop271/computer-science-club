# Network Fundamentals

## Basic Knowledge

- Computer: A single device.
- Ethernet: Network over a physical wire.
- WiFi: Network over a wireless connection.
- Network interface controller or network adapter: A single component (which can be a real physical device or a software one) that provides the basic functionality to connect a computer to some network, e.g. the ability to connect to another computer over an ethernet cable. A computer can have several adapters, e.g. one for ethernet, one for wifi.

## Layers of Abstraction

Networks operate on a stack of several layers of abstraction. Abstraction helps make things a bit easier to think of. If you aren't too familiar with the idea of layers of abstraction, suppose you have the python code `f = open("file.txt")` and `data = f.read()`, which opens and reads the entire contents of a file.

Even though *a lot* of work is being done behind the scenes, since you're using a high level language like Python, you don't see any of it: you assume all the lower level "layers" will do their job properly.

```text
Python Code
|       ^
v       |
CPython Code
|       ^
v       |
OS System Call
|       ^
v       |
Hard Drive Firmware
|       ^
v       |
Physical Parts of the Drive
```

Python itself is often implemented in C using CPython, so calls to the Python standard library results in C code being run. Depending on the specific OS the code is being run on, the C code will interact with the OS library API or OS system call to open and read a file.

The Python code does not care about the C library implementation, because they are written to be independent: you just assume that C will return with a proper Python object and result. Thus these are two different layers in the abstractions to open a file. The layer above another layer does not care how the layer below implements the functionality they provide, it just assumes the provided interface will work.

Likewise, the C code that interacts with the OS does not care how the OS implements their file opening or reading, as long as the C code gets back a pointer to a file and a pointer to a data buffer it can forward back to Python code as a Python object.

The OS will need to interact with the drive that stores the data, but the OS does not care how the drive implements its file reading, as long as the OS can build a data buffer to return to C.

The hard drive firmware does not care how the laws of physics allow the motors to move the platters and drive header, as long as the magnets can be read as ones or zeroes to return to the OS.

This is very similar to OOP abstraction in software: each layer's implementation can be considered to be private, possibly unstable. However, the interface they use to interact with each other is known, and each layer assumes the interface provided by the lower layer that they use will work.

## Exploration

Let's investigate how data can be transmitted to another computer.

### Physical

We have several computers in a house, each with an ethernet adapter. The way they are wired together and any intermediate devices (like a network switch) is out of scope for this software-oriented lesson. Honestly a lot of this entire page is somewhat out of scope, but whatever.

Each adapter should have its own address, called a MAC address, and the physical hardware knows how to send and receive data.

We can call this the physical or link layer of our network transmission: the ability to transfer data between two directly connected adapters.

### Internet

This works okay for a single home with a few computers, but we want to be able to connect many computers together around the world. So, what we can do is put a device called a router in each house, and all the computers connect to the router.

Then, we imagine each house's router as one device (even though several devices are accessible under the router), and connect several houses together under another router: this forms a larger network, with a router containing many house routers, each containing many computers within houses.

Each router connects to another bigger router, forming a tree of networks and routers. We can keep stacking this until we have a network containing a few routers that span the whole world.

However, our physical layer does not really understand this tree based structure. Thus, we introduce a new system called the Internet Protocol (IP). Each\* adapter now has an address called an IP address as well.

*public/private networks will be addressed later.

The routers added just now are part of the internet layer too. Their job is to route data from a source network to a destination network, using IP addresses and forwarding data across the router tree until the target network is reached. Again, we don't care about the implementation of routing here. The internet layer depends on the physical layer for the device to device transmission, but builds off of it to provide network to network transmission.

The internet layer also adds IP related info into a short header at the front of our data, including (but not limited to) the source and destination IP address. To the physical layer, that's just another few bytes to transmit along the wire, but to the internet layer, those header bytes mean something.

### IP addresses

Jumping back a little, the internet layer introduces the first thing we actually need to care about: IP addresses.

There are two versions of IP: IPv4 and IPv6. The main difference between v4 and v6 is that IPv4 uses 32 bit numbers (written as 4 period separated decimal unsigned bytes: `123.123.123.123`), while IPv6 uses 128 bits (written as 8 colon separated blocks of 4 hex digits: `1234:5678:9abc:def0:1234:5678:9abc:def0`).

However, most of the time, you interact with domain names like `en.wikipedia.org`. These are converted into IP addresses when you try to connect to them, since the internet layer doesn't understand how to route a string.

There are special servers called DNS (domain name system) servers that your computer knows the IP address of. Whenever your computer sees a domain name it doesn't know the IP address of, it connects to the DNS server to lookup the IP address of the name, so that your computer can actually use that IP address to connect to the computer. This is what allows the internet to use easy to remember domain names instead of IP addresses.

### Transport

Now that we have a method of sending data between two computers across the globe, we need a way of organizing that information transfer.

First, we'll split up all our data into smaller pieces called packets, so that large pieces of data don't have to be sent all at once. Just like how the internet layer added header information, we can put information that is meaningful to us at the front of each packet in a transport header. To the internet and physical layers, our transport header is no different from random data, and the internet layer will just slap its own header in front of our transport header.

We might have several applications on our computer that need to use a network connection, but currently we can only transmit packets between two computers as a whole. To help differentiate one application's traffic from another, we introduce the concept of a port to the system.

Each application picks a unique number from 0 to 65535 called the port, to add to each transport header. This will be the source port, and the source IP address will be added by the IP header. By doing this, a reply can be addressed back to the right computer and the right port, which can then be matched back to the source application. The OS makes sure that only one application can use any given port number at a time.

We can write combinations of IP and port by using a colon, for example `1.2.3.4:5555` refers to address `1.2.3.4`, port `5555`.

The internet layer is a little unreliable. Layers typically assume that the layer below does its job properly, but in this case, we assume that the actual job of the internet layer is to *attempt* to send data between different networks. The internet layer might drop a little bit of data, flip a couple bits, or it might end up routing some data through a faster path than the rest, meaning that our packets arrive out of order.

Sometimes, we don't care that we drop a few packets, because the overhead to make sure all the data is correct is too high for applications that need low latency and high speed (e.g. a call). In this case, we only need the absolute minimum added by the transport layer to the header: source port, destination port, packet length, and a basic checksum. This basic method of transportation is called UDP (user datagram protocol). Somewhat similarly to how IP has IPv4 and IPv6, the transport layer has two main protocols to choose from: UDP and TCP.

When we do care about accuracy (e.g. an email or bank account webpage), and don't want errors, TCP (transmission control protocol) can be used. TCP makes sure that packets are read in order, and that packets which have errors are re-delivered. In addition, TCP also provides congestion and flow control of data, to prevent devices or networks from being overloaded with data. TCP adds a header containing a lot more data compared to the UDP header (20 bytes vs 8), since the header contains the data required to give all the benefits TCP provides.

Another thing to note: ports are separated based on protocol, so UDP port 10000 is different from TCP port 10000. It's not like the port numbers are based on any physical slot so they can be separated.

### Application

We've now seen how we can transmit data from device to device, extend that system to be computer to computer, and further extend it to be much more organized and reliable. This system is now capable of transmitting whatever data we want, to wherever we want. All we need to do now is determine what to send.

Application data can be almost anything, an HTTP request, a file download, game data for a multiplayer game, random bytes... We can assume the layers below will be able to transfer the data properly.

Just like how the IP header is meaningless to the physical layer, and the transport header (UDP or TCP header) is meaningless to the internet and physical layers, the application data is totally meaningless to the transport, internet, and physical layers. It can be anything.

This is the layer someone writing typical applications will work in, but it's good to know all the supporting layers, especially since you'll need to use constructs provided by the transport and internet layers (namely ports and IP addresses) to work in the application layer and be able to send data to other computers.

## Special IP Addresses

`127.0.0.1` or `localhost` is an IP address or host name that refers to an imaginary network adapter on a computer, called the loopback adapter. It is named this way because data sent to `127.0.0.1` never leaves the computer it was sent from: it's just an adapter connected to itself. You can use localhost to send and receive data between two applications on one computer.

`0.0.0.0` is an IP address that won't really have much meaning until next lesson. It is meaningless when you try to connect, but when you bind/listen on `0.0.0.0`, you're listening on all available adapters. There can also be other less used meanings.

The IPv6 equivalent for `127.0.0.1` is `::1`, and `0.0.0.0` is `::`. These are both short forms, and expand to `0000:0000:0000:0000:0000:0000:0000:0001` and `0000:0000:0000:0000:0000:0000:0000:0000` respectively.

## Public and Private Networks

You might have noticed that IPv4 can only support a few billion different addresses. This is indeed a problem, as there are more than a few billion devices that connect to the internet. To significantly reduce the number of unique addresses needed, NAT (network address translation) and private networks are used.

On most networks, like a typical home network, the devices inside the home connect to the rest of the world through the router in that home. Instead of providing each device on each home network a unique IP address, the home networks are made into private networks. This means that now each computer in the house only needs to have an address unique to the other computers in the house.

Thus, there are three private address blocks: `192.168.0.0` to `192.168.255.255`, `172.16.0.0` to `172.31.255.255`, and finally `10.0.0.0` to `10.255.255.255`.

This means your home network could look like:

| Address | Device |
|-|-|
`192.168.0.1` | Router
`192.168.0.2` | Desktop
`192.168.0.3` | Phone
`192.168.0.4` | Laptop
`192.168.0.5` | Work Phone
`192.168.0.6` | Kid's Laptop
`192.168.0.7` | Kid's Tablet
`192.168.x.x` | etc... up to 65536 devices

At the same time, your neighbour's home network could look like this too:

| Address | Device |
|-|-|
`192.168.0.1` | Router
`192.168.0.2` | Desktop
`192.168.0.3` | Phone
`192.168.0.4` | Laptop
`192.168.0.5` | Security Camera 1
`192.168.0.6` | Security Camera 2
`192.168.0.7` | Security Camera 3
`192.168.0.8` | Security Camera 4
`192.168.x.x` | etc...

Your work or school's network could look like this:

| Address | Device |
|-|-|
`10.0.0.1` | Router
`10.0.0.2` | Person 1 Laptop
`10.0.0.3` | Person 1 Phone
`10.0.0.4` | Person 2 Laptop
`10.0.0.5` | Person 2 Phone
`10.0.0.6` | Person 3 Laptop
`10.0.0.7` | Person 3 Phone
`10.0.x.x` | etc... up to 16777216 devices

As you might be able to tell, being able to duplicate all these addresses leaves a lot more public IP addresses for use. All that needs to be assigned for the whole network is 1 public IP for the public facing router.

Thus, the router just needs to transform all outgoing requests. The way it does this is with a NAT translation table. When a `192.168.0.2:12345` (private) wants to connect to `1.2.3.4:443` (public), the packet  passes through the home router, which could have a public address of `2.3.4.5`.

The router generates a port number that isn't used in the table already, say 5000. Then, it modifies the packet so that the real private source address is replaced with the router's address, and the real port is replaced with this temporary fake port.

| Real Source | Dest | Translated Source |
|-|-|-|
`192.168.0.2:12345` | `1.2.3.4:443` | `2.3.4.5:5000`

When the destination `1.2.3.4` sees this and replies, it will reply to the source, which is `2.3.4.5:5000`. Once the router sees this reply, it'll look in the table to see what real source was assigned port 5000, and pass the reply over to `192.168.0.2:12345`.

This works great for clients on the private network connecting to public servers, and receiving replies, but it does not work well if a computer in the public wishes to connect to a specific private computer. This does provide a security boost, but can be inconvenient when a 10 year old wants to have their friends play on their local Minecraft server, but doesn't know why his friends can't connect to his private computer.

### Port Forwarding

One solution to this problem is port forwarding. In the software of the NAT router, a table of rules can be setup to forward requests. Here are two example rules:

| Public Port | Private Dest |
|-|-|
1234 | `192.168.0.2:1234`
5555 | `192.168.0.2:443`

What this table of rules says is: whenever a request is received on the given public port, the destination within the private network should be the given destination. Using the addresses from before, this means that someone on a different network can now connect to `2.3.4.5:1234`, and their request will be forwarded from the router (`2.3.4.5`) to the right private destination `192.168.0.2:1234`.
