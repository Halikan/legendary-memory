import tcod

from game_states import GameStates
from renderer import RenderOrder
from game_messages import Message
from modules.food import Food

def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red

    return Message("You died!", tcod.red), GameStates.PLAYER_DEAD

def kill_enemy(enemy): 
    death_message = Message('{0} is dead!'.format(enemy.name.capitalize()), tcod.orange)
    
    # Update's an entity's tile character, color, render order, and no longer blocks the tile
    enemy.char = '%'
    enemy.charInt = ord(enemy.char)
    enemy.color = tcod.dark_red
    enemy.blocks = False
    enemy.render_order = RenderOrder.CORPSE

    # Remove an entity's interactive modules, turn it into Food for the player to heal
    enemy.fighter = None
    enemy.ai = None
    enemy.torch = None
    enemy.food = Food(1,3)
    enemy.food.owner = enemy

    # Finally, update the name of the entity.
    enemy.name = 'remains of ' + enemy.name

    return death_message