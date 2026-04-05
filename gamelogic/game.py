"""

"""
from gamelogic.players import Player

class Game:
    def __init__(self, player1_name, player2_name):
        self.players = {
            player1_name: Player(player1_name),
            player2_name: Player(player2_name)
        }
        
        self.p1_name = player1_name
        self.p2_name = player2_name
        
        # Game states: "WAITING_FOR_SHIPS", "PLAYING", "GAME_OVER"
        self.state = "WAITING_FOR_SHIPS"
        
        # Player 1 goes first by default
        self.current_turn = player1_name 
        self.winner = None

    # Checks if the player is ready (If all ships have been placed)
    def check_ready(self):
        if self.players[self.p1_name].is_ready and self.players[self.p2_name].is_ready:
            self.state = "PLAYING"
            return True
        return False

    # Switches the current turn of the game
    def switch_turn(self):
        if self.current_turn == self.p1_name:
            self.current_turn = self.p2_name
        else:
            self.current_turn = self.p1_name

    # Handles logic of an attack
    def process_attack(self, attacker_name, r, c):
        if self.state != "PLAYING":
            return {"status": "ERROR", "message": "Game is not currently active"}
            
        if self.current_turn != attacker_name:
            return {"status": "ERROR", "message": "It is not your turn"}

        # Determine who is being attacked
        defender_name = self.p2_name if attacker_name == self.p1_name else self.p1_name
        defender = self.players[defender_name]
        
        # Defender takes the attack
        result = defender.board.receive_attack(r, c)
        
        # If the attack was valid (Hit, Miss, or Sunk), update game state and return the result
        if result["status"] in ["HIT", "MISS", "SUNK"]:
            if defender.check_loss():
                self.state = "GAME_OVER"
                self.winner = attacker_name
                result["game_over"] = True
                result["winner"] = attacker_name
            else:
                if result["status"] == "MISS":
                    self.switch_turn()
            
        result["next_turn"] = self.current_turn
        result["attacker"] = attacker_name
        result["r"] = r
        result["c"] = c
        
        return result
