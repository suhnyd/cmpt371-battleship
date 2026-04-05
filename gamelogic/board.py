"""
This class holds information about the board. Handles the logistics of placing ships and receiving an attack
"""

class Board():
    def __init__(self, size=10):
        # Standard size of board, building a 10x10 grid, and containing the ships that are on the board
        self.size = size
        self.grid = [[' '] * size for _ in range(size)]
        self.ships = []
    
    def place_ship(self, ship, direction, start):
        # start = (r,c)
        # direction = "H" or "V"

        positions = []

        # Validate that entire ship can fit before placing any part of it
        for i in range(ship.size):
            r, c = start
            if direction == "H":
                c += i
            else:
                r += i
            
            if not self.inbound(r, c):
                print(f"Cannot place {ship.name}: Goes out of bounds")
                return False

            if self.grid[r][c] != ' ':
                print(f"Cannot place {ship.name}: Space already occupied")
                return False

            positions.append((r, c))

        for (r, c) in positions:
            self.grid[r][c] = "S"

        ship.positions = positions
        self.ships.append(ship)
        return True

    def receive_attack(self, r, c):
        # Check if the attack is inbound
        if not self.inbound(r, c):
            return {"status": "ERROR", "message": "Out of Bounds"}
        
        target_cell = self.grid[r][c]

        # Check if the cell is already attacked
        if target_cell == "X" or target_cell == "O":
            return {"status": "ERROR", "message": "Already Fired At This Location"}

        # Check for a hit
        if target_cell == "S":
            self.grid[r][c] = "X"

            for ship in self.ships:
                if (r, c) in ship.positions:
                    ship.hits.add((r, c))

                    if ship.isSunk():
                        return {"status": "SUNK", "ship": ship.name}
                    else:
                        return {"status": "HIT"}
        # If it reaches here then it is a miss
        elif target_cell == ' ':
            self.grid[r][c] = "O"
            return {"status": "MISS"}

    # Simple function for checking whether a (r,c) is inbound
    def inbound(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size