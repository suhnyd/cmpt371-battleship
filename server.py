"""
CMPT 371 A3: Multiplayer Battleship Server
"""

import socket
import json
import threading
import select
from gamelogic.ships import Ship, STANDARD_FLEET
from gamelogic.game import Game

HOST = '127.0.0.1'
PORT = 5050

matchmaking_queue = []

def handle_game(p1_socket, p2_socket):
    game = Game("Player1", "Player2")

    # Tell both clients "MATCH FOUND, place your ships"
    p1_socket.sendall((json.dumps({"type": "MATCH FOUND", "payload": "Player1"}) + '\n').encode())
    p2_socket.sendall((json.dumps({"type": "MATCH FOUND", "payload": "Player2"}) + '\n').encode())

    sockets = [p1_socket, p2_socket]

    # Dict to map sockets to player#
    socket_to_player = {p1_socket: "Player1", p2_socket: "Player2"}

    # Use a while True loop to receive and process JSON actions
    while True:
        # Using select to check both sockets for updates
        read_sockets, _, _ = select.select(sockets, [], [])

        # Only returns the socket that has new data to be read
        for pinged_socket in read_sockets:
            try:
                data = pinged_socket.recv(1024)
            except Exception:
                data = None

            # If no data then a player disconnected, so we close the game for both players (Remaining player wins by default but not sent)
            if not data:
                print(f"A player disconnected. Closing game for both players...")
                for s in sockets:
                    try:
                        s.close()
                    except:
                        pass
                return
                
            messages = data.decode('utf-8').strip().split('\n')
            for clean_data in messages:
                if not clean_data:
                    continue
                msg = json.loads(clean_data)

                if msg["action"] == "FIRE":
                    r, c = msg["row"], msg["col"]
                    result = game.process_attack(socket_to_player[pinged_socket], r, c)

                    response = {
                        "type": "ATTACK_RESULT",
                        "payload": result
                    }

                    update_msg = (json.dumps(response) + "\n").encode()
                    p1_socket.sendall(update_msg)
                    p2_socket.sendall(update_msg)
                elif msg["action"] == "PLACE_SHIPS":
                    player_name = socket_to_player[pinged_socket]
                    player = game.players[player_name]

                    fleet_data = msg["payload"]

                    for ship_name, placement in fleet_data.items():
                        size = STANDARD_FLEET[ship_name]
                        new_ship = Ship(ship_name, size)

                        direction = placement["direction"]
                        start = tuple(placement["start"])

                        if not player.board.place_ship(new_ship, direction, start):
                            print(f"[ERROR] {player_name} sent and illegal placement for {ship_name}")
                    
                    player.is_ready = True
                    print(f"[STATUS] {player_name} fleet has been set.")

                    if game.check_ready():
                        print("[GAME START] Both players ready.")
                    
                        response = {
                            "type": "GAME_START",
                            "first_turn": game.current_turn
                        }
                        msg = (json.dumps(response) + "\n").encode()
                        p1_socket.sendall(msg)
                        p2_socket.sendall(msg)


def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen()
    print(f"[STARTING] Server is listening on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = s.accept()
            data = conn.recv(1024).decode('utf-8')

            if "CONNECT" in data:
                matchmaking_queue.append(conn)
                print(f"QUEUE: PLAYER ADDED. Queue size: {len(matchmaking_queue)}")

                if len(matchmaking_queue) >= 2:
                    player1 = matchmaking_queue.pop(0)
                    player2 = matchmaking_queue.pop(0)

                    # Create a thread that runs the game session loop in case more than 2 players want to play
                    print("[MATCH] 2 Players found. Spawning Game thread.")
                    threading.Thread(target=handle_game, args=(player1, player2)).start()
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        print("\n[SHUTDOWN] Server closing...")
    finally:
        s.close()

if __name__ == "__main__":
    start_server()
