import tcod
import math
from game_messages import Message
from renderer import RenderOrder


# Intended to represent both the player and human npcs
class Entity: # Entities can be given optional modules that add functionality/interactivity
    def __init__(self, x, y, char, color, name, blocks=False, render_order=RenderOrder.CORPSE,fighter=None, ai=None,food=None, torch=None, eater=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.ai = ai
        self.food = food
        self.torch = torch
        self.eater = eater

        # allows an Entity's modules to reference their associated parent Entity
        if self.fighter:
            self.fighter.owner = self
        if self.ai:
            self.ai.owner = self
        if self.food:
            self.food.owner = self
        if self.torch:
            self.torch.owner = self
            self.torch.updateFov
        if self.eater:
            self.eater.owner = self


    def move(self, dx, dy):
        self.x = dx
        self.y = dy

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx**2 + dy**2)

    def move_towards(self, target_x, target_y, forestMap, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        dx = int(round(dx/distance))
        dy = int(round(dy/distance))

        # If the target tile is not blocked, or occupied by another entity, move
        if not (forestMap.is_blocked(self.x + dx,self.y + dy) or
                get_blocking_entity(entities,self.x + dx,self.y + dy)):
            self.move(dx,dy)

    

    def move_astar(self, target, entities, forestMap):
        # Create a FOV map that has the dimensions of the map
        fov =  tcod.map_new(forestMap.width, forestMap.height)
 
        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(forestMap.height):
            for x1 in range(forestMap.width):
                 tcod.map_set_properties(fov, x1, y1, not forestMap.tiles[x1][y1].block_sight,
                                           not forestMap.tiles[x1][y1].blocked)
 
        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                 tcod.map_set_properties(fov, entity.x, entity.y, True, False)
 
        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path =  tcod.path_new_using_map(fov, 1.41)
 
        # Compute the path between self's coordinates and the target's coordinates
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)
 
        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
        if not  tcod.path_is_empty(my_path) and  tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y =  tcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, forestMap, entities)
 
            # Delete the path to free memory
        tcod.path_delete(my_path)

class Player(Entity):
    def is_burning(self,entities): # Additional player-only function for if the player is burning due to light level
        for entity in entities:
            if entity.torch:
                if entity.torch.brightness > 0:
                    lit = tcod.map_is_in_fov(entity.torch.fov,self.x,self.y)
                    if lit == True:
                        result = {'message':Message("You are burning from the light and take {0} damage!".format(entity.torch.brightness),tcod.red), 'brightness':entity.torch.brightness}
                        return result
        return False

def get_blocking_entity(entities, dest_x, dest_y): # Note: Can also return the entity checking (if entity is "moving" to its current tile. Handled elsewhere)
    for entity in entities:
        if entity.blocks and entity.x ==dest_x and entity.y == dest_y:
            return entity
    return None

def get_consumable_entity(entities, dest_x, dest_y): # Get an entity with the Food module on a target tile, returns None if none exist at location.
    for entity in entities:
        if entity.food and entity.x ==dest_x and entity.y == dest_y:
            return entity
    return None