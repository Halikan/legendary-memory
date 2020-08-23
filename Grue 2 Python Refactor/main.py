import tcod
# If tcod is not currently installed in test environment, run the following command: py -m pip install tcod
# Documentation: https://python-tcod.readthedocs.io/en/latest/
from random import randint
from input_handler import handle_input
from entity import Entity, Player, get_blocking_entity, get_consumable_entity
from renderer import render, clear, RenderOrder, render_bar
from forestMap import ForestMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from modules.fighter import Fighter
from modules.ai import BasicHuman
from modules.torch import Torch
from modules.food import Food
from modules.eater import Eater
from death_functions import kill_enemy, kill_player
from game_messages import MessageLog, Message


def main():
    # Define the console and map's size
    console_width = 80
    console_height = 60

    map_width = 80
    map_height = 45

    # UI component sizes, partially based off of the sizes above
    bar_width = 20
    message_x = bar_width + 2
    message_width = console_width - bar_width - 2
    message_height = console_height-map_height -2

    # The colors passed into the rendering functions
    map_colors = {
        'tree' :tcod.Color(102,51,0),
        'dark tree':tcod.Color(51,25,0),
        'grass':tcod.Color(0,102,0),
        'dark grass':tcod.Color(0,51,0),
        'burning out':tcod.orange,
        'dim':tcod.yellow,
        'bright':tcod.yellow,
        'too bright':tcod.white
    }

    # Random generation variables
    tree_density = 30
    clearing_min = 5
    clearing_max = 10
    max_clearings = 25
    max_entities_per_room = 4

    # Init player
    player_x = randint(0, map_width)
    player_y = randint(0, map_height)

    fighter_module=Fighter(hp=30, defense=2, power=5)
    eater_module=Eater(50,30)

    player = Player(player_x,player_y,'G', tcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR,fighter=fighter_module, eater=eater_module)

    fov_radius = 8

    # Entities list will keep track of all humans,corpses, and the player
    entities = [player]

    # Create a console using a provided tileset image to contain the game
    tileset = tcod.console_set_custom_font('dejavu10x10_gs_tc.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    console = tcod.Console(console_width, console_height)  
    
    # Initialize map
    forestMap = ForestMap(map_width,map_height)
    forestMap.gen_forest(tree_density,clearing_min,clearing_max,max_clearings, player, entities, max_entities_per_room)

    # Player's field of view
    fov_map = initialize_fov(forestMap)
    fov_recompute = True
    
    # Message log that prints game Messages
    message_log = MessageLog(message_x,message_width, message_height)


    # Initialize mouse location for mouse hover hints feature
    mouse_hover_loc=(0,0)




    with tcod.context.new_terminal(console.width, console.height,title='Grue 2', tileset=tileset,) as root_console:

        # Intro text
        intro = ["Welcome to Grue 2!",
                "The humans are trying to hunt you down, and you're hungry!",
                "1. Avoid the light! it burns and its hard to see in it.",
                "2. Win the game by filling your hunger bar! Lose by starving.",
                "Controls:",
                "Up,Down,Left,Right: J,K,H,L",
                "Up-Left,Up-Right: Y,U",
                "Down-Left,Down-Right: B,N",
                "Wait: Space Bar",
                "Eat: E when available",
                "Rest: R when alone"
        ]
        for text in intro: # Print intro to message log
            message = Message(text,tcod.white)
            message_log.add_message(message)

        for entity in entities:
            if entity.torch:
                entity.torch.updateFov()
            
        # Starts the game with the player moving first
        game_state = GameStates.PLAYER_TURN
        while True: # Main  game loop

            #Clear console before redrawing
            if fov_recompute:
                recompute_fov(fov_map, player.x, player.y, fov_radius)
                console.clear(fg=(255,127,0))
                
            # Render player in their current position, and the message log
            render(console,entities,player,forestMap,fov_map, fov_recompute,console_width,console_height,bar_width,map_colors, message_log, mouse_hover_loc)
            fov_recompute = False


            
            # Display the console            
            root_console.present(console)

            # Process events
            for event in tcod.event.wait():
                # Events are sent to input_handler.py for processing
                action = handle_input(event)

                move = action.get('move')
                eat = action.get('eat')
                rest = action.get('rest')

                if event.type == 'MOUSEMOTION': # Converts event's pixel coordinates into tile coordinates
                    root_console.convert_event(event)
                    mouse_hover_loc = event.tile

                player_turn_results = [] # Messages and flags are gathered into a list to process all at once
            

                if game_state == GameStates.PLAYER_TURN:
                    # Update player's position if they have moved
                    if move:
                        dx, dy = move

                        dest_x = player.x + dx
                        dest_y = player.y + dy

                        # Check for a valid move
                        if dest_x >= 0 and dest_x < map_width and dest_y >= 0 and dest_y < map_height:
                            if not forestMap.is_blocked(dest_x, dest_y):
                                target = get_blocking_entity(entities, dest_x, dest_y)
                                if target and target is not player: # Attack enemy if in destination tile
                                    attack_results = player.fighter.attack(target)
                                    player_turn_results.extend(attack_results)
                                else: # Otherwise, just move to the new empty tile
                                    player.move(dest_x, dest_y)
                                
                                starve_results = player.eater.starve()
                                player_turn_results.extend(starve_results)
                                
                                game_state = GameStates.ENEMY_TURN
                            # Note: Nothing is printed to the message log if the player walks into a tree, to avoid excessive messages
                        else:
                            # Print an error if the player reaches the edges of the map
                            message = Message("You can't leave the dark forest!",tcod.yellow)
                            message_log.add_message(message)
                        fov_recompute = True # Set flag to render player's new field of view due to changed coordinates

                    elif eat:
                        # If the player tries to eat, check if a food entity is available
                        target = get_consumable_entity(entities, player.x, player.y)
                        if target:
                            # If so, eat it, and add items to player_turn_results. Healing is processed later.
                            amount_eaten, consume_result = target.food.consume()
                            eat_results = player.eater.eat(amount_eaten)

                            player_turn_results.extend(consume_result)
                            player_turn_results.extend(eat_results)
                            fov_recompute = True # Rerender field of view because of possible removed entity
                            game_state = GameStates.ENEMY_TURN

                    elif rest:
                        being_chased = False
                        for entity in entities: # Check if an Entity is currently chasing the player
                            if entity.ai:
                                if entity.ai.chasing:
                                    being_chased = True

                        message = None
                        if being_chased: # If so, print an error in the Message Log, and keep it as the player's turn
                            message = Message("You cannot rest while there are enemies nearby",tcod.orange)
                            message_log.add_message(message)
                        elif player.fighter.hp < player.fighter.max_hp and player.eater.hunger > 0:
                            # If it's safe to rest, they heal, lose hunger value, and end the player's turn
                            message = Message("You rest briefly...",tcod.light_grey)
                            message_log.add_message(message)

                            heal_results = player.fighter.heal(1)
                            player_turn_results.extend(heal_results)

                            starve_results = player.eater.starve()
                            player_turn_results.extend(starve_results)

                            fov_recompute = True # Rerender field of view because of changed HP/Hunger bars
                            game_state = GameStates.ENEMY_TURN  
                                     
            

                for player_turn_result in player_turn_results: # Parse results from player moves
                    message = player_turn_result.get('message')
                    dead_entity = player_turn_result.get('dead')
                    recovery = player_turn_result.get('recovery')
                    consumed = player_turn_result.get('consumed')
                    starving = player_turn_result.get('starving')
                    
                    # Print messages to message log
                    if message:
                        message_log.add_message(message)

                    # Heal the player, check if their hunger bar reaches max hunger, which is the winning condition
                    if recovery:
                        heal_results = player.fighter.heal(recovery)
                        eating_results = player.eater.eat(recovery)
                        for result in heal_results:
                            message = result.get('message')
                            if message:
                                message_log.add_message(message)
                        for result in eating_results:
                            message = result.get('message')
                            stuffed = result.get('stuffed')
                            if message:
                                message_log.add_message(message)
                            if stuffed:
                                message = Message("Your stomach is fit to burst, and does! You win!", tcod.yellow)
                                message_log.add_message(message)
                                game_state = GameStates.PLAYER_WINS
                                break
                        if game_state == GameStates.PLAYER_WINS:
                            break
                    if game_state == GameStates.PLAYER_WINS: # When the player wins, no further input is possible
                            break                            # Except for Esc which closes the game

                    if consumed: # If an entity's food module has been consumed, remove the entity from existence
                        message = Message("{0} has been eaten whole!".format(consumed.name.capitalize()), tcod.grey)
                        message_log.add_message(message)
                        entities.remove(consumed)

                    if starving: # If the player is starving, take damage each turn
                        starved = player.fighter.take_damage(1)
                        if starved: # If the starved flag is returned, the player has died of starvation
                            dead_entity = player

                    if dead_entity: # Handle all entity deaths
                        if dead_entity == player: # The player's death results in a game over, in death_functions.py
                            message, game_state = kill_player(player)
                            fov_recompute = True
                        else: # Other entities are killed and turned into corpses/food
                            message = kill_enemy(dead_entity)
                        message_log.add_message(message) # Message about who died is passed into the message log

            # Process all of the enemy's turns
            if game_state == GameStates.ENEMY_TURN:
                enemy_turn_results = []
                player_lightLevel = 0
                for entity in entities:
                    if entity.ai: # If the entity has an ai module attached, they get a turn (non ai Entities are just items, like corpses)
                        enemy_turn_results.extend(entity.ai.take_turn(player, fov_map, forestMap, entities))
                    if entity.torch: # If the entity has a torch, check the field of view and if it touches the player
                        entity.torch.updateFov()
                        if entity.torch.brightness > 0: # Check and get the highest brightness on the player's tile
                            lit = tcod.map_is_in_fov(entity.torch.fov,player.x,player.y)
                            if lit == True: # Keep track of the brightest value touching the player, if any
                                if entity.torch.brightness > player_lightLevel:
                                    player_lightLevel = entity.torch.brightness

                        burn_results = entity.torch.burn(fov_map)
                        enemy_turn_results.extend(burn_results)   
                    if game_state == GameStates.PLAYER_DEAD:
                        break
                if player_lightLevel: # If the player was caught in torchlight, add message about damage, and take damage basedon the light level
                    message = [{'message':Message("You are burning from the light and take {0} damage!".format(player_lightLevel),tcod.red)}]
                    enemy_turn_results.extend(message)
                    burning_result = player.fighter.take_damage(player_lightLevel)
                    enemy_turn_results.extend(burning_result)
                        
                for enemy_turn_result in enemy_turn_results: # Process all enemy turn results at once
                    message = enemy_turn_result.get('message')
                    dead_entity = enemy_turn_result.get('dead')
                    torch_out = enemy_turn_result.get('torch_out')

                    if message: # Print any messages to the message log
                        message_log.add_message(message)

                    if torch_out: # If an entity's torch has gone out, remove their torch module
                        torch_out.torch = None

                    if dead_entity: # If an entity died, process based on who
                        if dead_entity == player: # Player death = game over
                            message, game_state = kill_player(dead_entity)
                        else: # Entity death results in losing ai/fighter/torch modules, gaining food module and becoming a corpse
                            message = kill_enemy(dead_entity)
                        message_log.add_message(message) # Add message about who died to the message log
                
                if game_state is not GameStates.PLAYER_DEAD: # So long as the player is not dead, it becomes the player's turn again
                    game_state = GameStates.PLAYER_TURN      # First, however, the map will be rendered again.


if __name__ == '__main__':
    main()