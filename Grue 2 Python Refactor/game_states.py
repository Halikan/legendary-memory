from enum import Enum

# States determine if the player can move, when to process enemy turns, and if the player won or lost
class GameStates(Enum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
    PLAYER_WINS = 4