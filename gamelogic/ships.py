"""
This handles the basic logic for ship logistics such as name, size, etc.. aswell as containing the standard fleet
"""

class Ship():
    def __init__(self, name, size):
        # Store name of the ship, size of ship, what positions it takes up, and in which positions it is hit or not
        self.name = name
        self.size = size
        self.positions = []
        self.hits = set()
        
    def isSunk(self):
        # A ship is officially sunk if the amount of times it got hit matches its total size
        return len(self.hits) == self.size

# The standard fleet for the game
STANDARD_FLEET = {
    "Carrier": 5,
    "Battleship": 4,
    "Cruiser": 3,
    "Submarine": 3,
    "Destroyer": 2
}