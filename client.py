"""
CMPT 371 A3: Battleship Multiplayer Client
Architecture: JSON over TCP Protocol
Reference: GENAI used to help upscale DEMO SAMPLE BOARD & main logic loop adapted from TA DEMO SAMPLE
"""
import socket
import json
from gamelogic.board import Board 
from gamelogic.ships import Ship, STANDARD_FLEET

HOST = '127.0.0.1'
PORT = 5050

# Draws the board of the game (FORMART ADAPTED FROM SAMPLE REPO)
def draw_boards(my_board, tracking_board):
    print("\n        --- YOUR SHIPS ---                                       --- ENEMY BOARD ---")
    
    col_nums = "      1   2   3   4   5   6   7   8   9  10  "
    top_bord = "    ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐"
    mid_bord = "    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤"
    bot_bord = "    └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘"
    pad = "          "
    
    print(f"{col_nums}{pad}{col_nums}")
    print(f"{top_bord}{pad}{top_bord}")
    
    letters = "ABCDEFGHIJ"
    for i in range(10):
        my_cells = "│".join([f" {c} " for c in my_board.grid[i]])
        track_cells = "│".join([f" {c} " for c in tracking_board.grid[i]])
        
        row1 = f"  {letters[i]} │{my_cells}│"
        row2 = f"  {letters[i]} │{track_cells}│"
        
        print(f"{row1}{pad}{row2}")
        if i < 9:
            print(f"{mid_bord}{pad}{mid_bord}")
        else:
            print(f"{bot_bord}{pad}{bot_bord}\n")

# Logic Loop for when its the client's turn
def take_turn(client):
    while True:
        target = input("\nEnter coordinate to fire at (A-J and 1-10) [e.g. A5]: ").strip().upper()
        try:
            r = ord(target[0]) - 65
            c = int(target[1:]) - 1

            # Check for valid input
            if 0 <= r <= 9 and 0 <= c <= 9:
                payload = {"action": "FIRE", "row": r, "col": c}
                client.sendall((json.dumps(payload) + "\n").encode())
                break
            else:
                print("Out of bounds! Must be A-J and 1-10.")
        except Exception:
            print("Invalid format! Use format A5.")

def start_client():
    # === PHASE 1: CONNECTION ===
    # Connect to TCP Host
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    client.sendall((json.dumps({"type": "CONNECT"}) + '\n').encode())
    print("Connected. Waiting for an opponent....")

    player = None

    # Loop 
    while player is None:
        data = client.recv(1024).decode()
        # If data is empty then server is closed
        if not data:
            print("Server disconnected.")
            return

        # Strip and parse through each data segment
        messages = data.strip().split('\n')
        for clean_data in messages:
            if not clean_data:
                continue
            
            msg = json.loads(clean_data)
            # Check if a match is found then start game and assign client player #
            if msg.get("type") == "MATCH FOUND":
                player = msg.get("payload")
                print(f"MATCH FOUND! You are {player}.")

    # === PHASE 2: PLACEMENT ===
    print("\n--- SHIP PLACEMENT ---")
    fleet_payload = {}
    
    # Use the Board class to validate our placements before sending to server
    my_board = Board()
    tracking_board = Board()
    
    draw_boards(my_board, tracking_board)
    
    for ship_name, size in STANDARD_FLEET.items():
        while True:
            # Ask the user for input like "A5 H"
            user_input = input(f"Place your {ship_name} (Size: {size}) (A-J and 1-10) [e.g. A5 H]: ").strip().upper()
            
            try:
                coords, direction = user_input.split(" ")
                
                # Used to convert alphabet to numbers
                r = ord(coords[0]) - 65
                c = int(coords[1:]) - 1
                
                # Make sure it's valid locally so server doesn't have to deal with junk
                temp_ship = Ship(ship_name, size)
                if my_board.place_ship(temp_ship, direction, (r, c)):
                    # Save to dictionary if valid
                    fleet_payload[ship_name] = {
                        "direction": direction,
                        "start": [r, c]
                    }
                    draw_boards(my_board, tracking_board)
                    break # Break out of the loop to move to the next ship
                else:
                    print("Invalid placement. It overlaps or goes off the board. Try again.")
            except Exception as e:
                print("Invalid format! Please use format 'A5 H' where H=Horizontal and V=Vertical.")
                
    # Once all 5 ships are successfully placed, send the final dictionary
    print("\nAll ships placed locally! Sending coordinates to server...")
    placement_message = {
        "action": "PLACE_SHIPS",
        "payload": fleet_payload
    }
    client.sendall((json.dumps(placement_message) + "\n").encode())

    # === PHASE 3: THE GAME LOOP ===
    
    while True:
        # Receive data from server

        data = client.recv(1024).decode()
        if not data:
            print("Server disconnected.")
            return

        messages = data.strip().split('\n')
        for clean_data in messages:
            if not clean_data:
                continue
            
            msg = json.loads(clean_data)
            
            if msg.get("type") == "GAME_START":
                print("\n\n★ THE GAME HAS BEGUN! ★")
                player_turn = msg["first_turn"]
                
                # Draw the boards at first to assist user visually
                draw_boards(my_board, tracking_board)
                
                if player_turn == player:
                    take_turn(client)
                else:
                    print("\nWaiting for opponent to attack...")

            elif msg.get("type") == "ATTACK_RESULT":
                result = msg["payload"]
                
                # Extract context from the server message
                attacker = result.get("attacker")
                r = result.get("r")
                c = result.get("c")
                status = result.get("status")
                
                if attacker == player:
                    # We attacked them, update results to our local boards
                    if status in ["HIT", "SUNK"]:
                        tracking_board.grid[r][c] = "X"
                        print(f"\n[HOT RESULT]: You hit an enemy ship!")
                        if status == "SUNK":
                            print(f"[HOT RESULT]: You sunk their {result.get('ship')}!")
                    elif status == "MISS":
                        tracking_board.grid[r][c] = "O"
                        print("\n[RESULT]: You missed.")
                    elif status == "ERROR":
                        print(f"\n[ERROR]: {result.get('message', 'Invalid move.')}")
                else:
                    # We got attacked, update the results to our local boards
                    if status in ["HIT", "SUNK"]:
                        my_board.grid[r][c] = "X"
                        print(f"\n[ALERT]: Enemy hit your ship!")
                    elif status == "MISS":
                        my_board.grid[r][c] = "O"
                        print("\n[ALERT]: Enemy fired and missed!")
                        
                draw_boards(my_board, tracking_board)
                
                if result.get("game_over"):
                    if result.get('winner') == player:
                        print("YOU WON! :)")
                    else:
                        print("YOU LOST :(")
                    return
                
                if result.get("next_turn") == player:
                    take_turn(client)
                else:
                    print("\nWaiting for opponent to attack...")

if __name__ == "__main__":
    start_client()
