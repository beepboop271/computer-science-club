# tic-tac-toe message overview:
#
# All messages end in b"\n"
#
# If b"bye" is received at any time, the server is ending the
# game due to:
# - a player disconnecting
# - a player declined rematch
# - a player made an invalid move or otherwise unexpected
#   message
#
# Client opens with b"hello, world!"
# Server replies with b"x" or b"o" to indicate whether the
# client is X or O
#
# Loop:
#
# The server sends either b"move", b"win", b"tie", b"lose", or
# coordinates indicating a player's move
#
# If b"move" is received, the client replies with the
# coordinates of their move e.g. b"(0, 1)"
#
# (0, 0) │ (1, 0) │ (2, 0)
# ───────┼────────┼───────
# (0, 1) │ (1, 1) │ (2, 1)
# ───────┼────────┼───────
# (0, 2) │ (1, 2) │ (2, 2)
#
# If b"win", b"tie", or b"lose" is received, the client either
# sends b"bye!" and exits, or it sends b"again!" to indicate
# another match is requested
#
# If coordinates are received, they are the location of a
# player's move e.g. b"x(1, 2)", b"o(0, 2)". both players
# receive the other player's moves as well as their own moves

import os
import random
import re
import socket
from typing import Iterable, List, Optional, Tuple

import dotenv
dotenv.load_dotenv()


class Player(object):
    def __init__(self, conn, addr, mark):
        self.conn: socket.socket = conn
        self.addr = addr
        self.mark: str = mark


def broadcast(players: Iterable[Player], msg: bytes) -> None:
    for player in players:
        player.conn.send(msg)


def end(players: Iterable[Player]) -> None:
    broadcast(players, b"bye\n")


def get_players(sock: socket.socket) -> Optional[List[Player]]:
    if random.random() < 0.5:
        marks = ["x", "o"]
    else:
        marks = ["o", "x"]

    player1 = Player(*sock.accept(), marks[0])
    print(f"received connection 1 from {player1.addr}")
    player2 = Player(*sock.accept(), marks[1])
    print(f"received connection 2 from {player2.addr}")

    players = [player1, player2]

    for player in players:
        msg = player.conn.recv(32)
        if msg != b"hello, world!\n":
            end(players)
            return None
        player.conn.send((player.mark+"\n").encode())

    return players


def get_move(player: Player) -> Tuple[int, int]:
    player.conn.send(b"move\n")
    msg = player.conn.recv(32)
    move = re.match(r"\(([012]), ([012])\)\n", msg.decode())
    if move is None:
        raise ValueError("bad message")
    groups = move.groups()
    return (int(groups[0]), int(groups[1]))


directions = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))
chain_dirs = ((0, 4), (1, 5), (2, 6), (3, 7))


def check_win(board: List[List[str]], last_move: Tuple[int, int]) -> bool:
    longest_chain = 0
    for chain in chain_dirs:
        longest_chain = max(
            get_chain_length(
                board,
                *last_move,
                board[last_move[1]][last_move[0]],
                chain[0]
            ) + get_chain_length(
                board,
                *last_move,
                board[last_move[1]][last_move[0]],
                chain[1]
            ) - 1,
            longest_chain,
        )
    return longest_chain == 3


def get_chain_length(
    board: List[List[str]],
    x: int,
    y: int,
    mark: str,
    direction: int,
) -> int:
    if x < 0 or x > 2 or y < 0 or y > 2:
        return 0
    if board[y][x] == mark:
        return 1 + get_chain_length(
            board,
            x+directions[direction][0],
            y+directions[direction][1],
            mark,
            direction
        )
    return 0


def check_rematch(players: Tuple[Player, ...]) -> bool:
    if (
        players[0].conn.recv(32) != b"again!\n"
        or players[1].conn.recv(32) != b"again!\n"
    ):
        end(players)
        return False
    return True


def run(players: Tuple[Player, ...]) -> bool:
    board = [[""]*3 for _ in range(3)]

    current_player = 0
    other_player = 1
    move_count = 0
    while 1:
        player = players[current_player]
        other = players[other_player]

        try:
            move = get_move(player)
        except ValueError:
            end(players)
            return False

        if board[move[1]][move[0]] != "":
            end(players)
            return False
        board[move[1]][move[0]] = player.mark
        move_count += 1

        broadcast(players, (player.mark+str(move)+"\n").encode())
        if check_win(board, move):
            player.conn.send(b"win\n")
            other.conn.send(b"lose\n")
            return check_rematch(players)
        elif move_count == 9:
            broadcast(players, b"tie\n")
            return check_rematch(players)
        else:
            other_player = current_player
            current_player = (current_player+1) % 2


with socket.create_server(("", int(os.getenv("PORT", "")))) as sock:
    while 1:
        players = get_players(sock)
        if players is not None:
            random.shuffle(players)
            while run(tuple(players)):
                random.shuffle(players)
