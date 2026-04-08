# CMPT 371 A3: Multiplayer Battleship

- Sunny Cui — 301544988 — syc50@sfu.ca
- Ryan Fung — 301579052 — rjf9@sfu.ca

[Demo Video](https://www.youtube.com/watch?v=a-BFZ6rrnvE)

This project is a terminal-based multiplayer Battleship game built with Python sockets. One server accepts TCP connections, matches two players together, receives ship placements, and relays turn-based attack results between both clients using JSON messages over TCP.

## Project Structure

- `server.py`: Starts the matchmaking server and creates a game thread for each matched pair.
- `client.py`: Terminal client used by each player to connect, place ships, and play the game.
- `gamelogic/`: Shared game logic for boards, ships, players, and turn resolution.

## Features

- Two-player matchmaking over TCP.
- Local validation for ship placement before data is sent to the server.
- Turn-based firing with hit, miss, and sunk results.
- Side-by-side terminal rendering of your board and your tracking board.
- Standard Battleship fleet:
  - Carrier (5)
  - Battleship (4)
  - Cruiser (3)
  - Submarine (3)
  - Destroyer (2)

## Limitations

These are the main limitations and edge cases:

- Only supports exactly 2 players per game.
- Server is configured for `127.0.0.1:5050`, so it is set up for local-machine testing by default.
- If a player disconnects, the server closes the game.
- Player 1 always gets the first turn once both players finish ship placement.

## Requirements

- Python 3.11 or newer is recommended.
- A terminal window for the server.
- Two terminal windows for two clients.

## Fresh Environment Setup

1. Clone the repository:

```bash
git clone https://github.com/suhnyd/CMPT371_A3_battleship.git
cd CMPT371_A3_battleship
```

2. Confirm Python 3 is installed:

```bash
python3 --version
```

## How To Run

Open 3 terminal windows in the project root.

### 1. Start the server

In terminal 1:

```bash
python3 server.py
```

Expected output:

```text
[STARTING] Server is listening on 127.0.0.1:5050
```

### 2. Start client 1

In terminal 2:

```bash
python3 client.py
```

Expected output:

```text
Connected. Waiting for an opponent....
```

### 3. Start client 2

In terminal 3:

```bash
python3 client.py
```

Once the second client connects, both clients should receive a match and ship placement will begin.

## How To Play

### Ship placement

Each player is prompted to place the 5 ships one at a time.

Input format:

```text
A5 H
```

Meaning:

- `A5` is the starting coordinate.
- `H` means horizontal.
- `V` means vertical.

Valid rows are `A-J`. Valid columns are `1-10`.

Examples:

- `A1 H`
- `C7 V`
- `J8 H`

If a placement overlaps another ship or goes out of bounds, the client will reject it and ask again.

### Firing

When it is your turn, enter a target coordinate like:

```text
B6
```

The game reports:

- `HIT`
- `MISS`
- `SUNK`

If you miss, your turn is over. The board updates after every attack for both players.

## End Of Game

The game ends when one player sinks all of the opponent's ships.

The winner sees:

```text
YOU WON! :)
```

The loser sees:

```text
YOU LOST :(
```

## Troubleshooting

- If `python3` is not found, install Python 3 and rerun the commands.
- If the client cannot connect, make sure `server.py` is already running.
- If you see "Address already in use", another process is already using port `5050`. Stop that process or change the port in both `server.py` and `client.py`.
- If one player closes their client, the current game session ends.
