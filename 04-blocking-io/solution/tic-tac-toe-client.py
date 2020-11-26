import os
import socket
from typing import List

import dotenv
dotenv.load_dotenv()


def do_move(sock: socket.socket, board: List[List[str]]) -> None:
    x = -1
    y = -1
    move = input("enter move as coords 'x y': ")
    if len(move) == 3:
        x = int(move[0])
        y = int(move[2])
    while x < 0 or x > 2 or y < 0 or y > 2 or board[y][x] != " ":
        move = input("enter move as coords 'x y': ")
        if len(move) == 3:
            x = int(move[0])
            y = int(move[2])
    sock.send(f"({x}, {y})\n".encode())


def prompt_rematch(sock: socket.socket) -> bool:
    response = input("would you like a rematch (y/n): ").lower()
    if len(response) > 0 and response[0] == "y":
        sock.send(b"again!\n")
        return True
    sock.send(b"bye!\n")
    return False


def display_board(board: List[List[str]]) -> None:
    for row in range(2):
        print(f" {board[row][0]} │ {board[row][1]} │ {board[row][2]} ")
        print("───┼───┼───")
    print(f" {board[2][0]} │ {board[2][1]} │ {board[2][2]} ")


with socket.create_connection((
    os.getenv("HOST", "127.0.0.1"),
    int(os.getenv("PORT", "")),
)) as sock:
    sock.send(b"hello, world!\n")

    msg = sock.recv(32)
    mark = msg.decode()[0]
    print(f"you are: {mark}")

    board = [[" "]*3 for _ in range(3)]

    running = True
    while running:
        msg = sock.recv(32)
        print(msg)
        if msg == b"move\n":
            do_move(sock, board)
        elif (msg == b"win\n" or msg == b"lose\n" or msg == b"tie\n"):
            if msg == b"win\n":
                print("you won!")
            elif msg == b"lose\n":
                print("you lost!")
            elif msg == b"tie\n":
                print("the game ended in a tie.")
            board = [[" "]*3 for _ in range(3)]
            running = prompt_rematch(sock)
        elif msg == b"bye\n":
            running = False
        else:
            move = msg.decode()
            board[int(move[5])][int(move[2])] = move[0]
            display_board(board)
    print("the game ended.")
