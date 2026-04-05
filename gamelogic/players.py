"""
Class to 
"""
from gamelogic.board import Board

class Player:
    def __init__(self, name):
        self.name = name
        
        # Own Board
        self.board = Board()
        
        # A tracking board just to keep a record of where they fired
        self.tracking_board = Board() 
        
        self.is_ready = False
        self.has_lost = False

    # Checks if the user lost the game by checking if all ships are sunk. returns Bool
    def check_loss(self):

        # If no ships are placed, they haven't lost, the game just hasn't started
        if len(self.board.ships) == 0:
            return False
            
        for ship in self.board.ships:
            if not ship.isSunk():
                return False
                
        self.has_lost = True
        return True