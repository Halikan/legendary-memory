import tcod
from tile import Tile
from random import randint
from map_objects.clearing import Clearing
from entity import Entity
from modules.fighter import Fighter
from modules.ai import BasicHuman
from modules.torch import Torch
from renderer import RenderOrder

class ForestMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self): # Creates an [x][y] array of Tile objects that reference the tiles on screen
        tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def add_trees(self, tree_density): # Generate trees randomly based on a given density for spawn chance.
        for x in range(self.width):
            for y in range(self.height):

                spawn_chance = randint(0,100)

                if spawn_chance < tree_density and self.has_room(x,y):
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].block_sight = True
    def add_clearings(self,clearing_min,clearing_max,max_clearings,player, entities, max_entities_per_room):
        clearings = []
        total_clearings = 0

        for x in range(max_clearings):
            # randomize width and height for each clearing based on given parameters
            width = randint(clearing_min, clearing_max)
            height = randint(clearing_min, clearing_max)

            # random position within the ForestMap
            x = randint(0, self.width-width-1)
            y = randint(0, self.height-height-1)
            clearing = Clearing(x, y, width, height)

            # place Player in first generated clearing
            # Technically, will still be a random location.
            if total_clearings == 0:
                self.create_clearing(clearing)
                player.x = clearing.x1+1
                player.y = clearing.y1+1
                clearings.append(clearing)
                total_clearings += 1

            # check and avoid clearings intersecting each other
            else:
                intersecting = False
                for other_clearing in clearings:
                    if clearing.intersect(other_clearing):
                        intersecting = True # The currently spawned clearing would have intersected with an existing clearing
                        break
                if not intersecting: # If it doesn't intersect with any existing clearings
                    self.create_clearing(clearing) # Create the clearing
                    self.place_entities(clearing, entities, max_entities_per_room) # Populate the clearing with humans
                    clearings.append(clearing) # Add to list of clearings that are checked for intersecting
                    total_clearings +=1

    def gen_forest(self, tree_density,clearing_min,clearing_max,max_clearings,
                    player, entities, max_entities_per_room):
        # Add trees, then add clearings that contain human entities
        self.add_trees(tree_density)
        self.add_clearings(clearing_min,clearing_max,max_clearings,
                            player, entities, max_entities_per_room)

        

    def create_clearing(self, clearing): # Clearings remove trees that were previously spawned, improving map variety
        for x in range(clearing.x1 + 1, clearing.x2):
            for y in range(clearing.y1 + 1, clearing.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def is_blocked(self, x,y): # Get's a Tile object's blocked property.
        if self.tiles[x][y].blocked:
            return True
        else:
            return False

    def has_room(self, x, y):# Checks if any tiles around a given coordinate are occupied
        
        for x in range(x-1, x+1):
            for y in range(y-2, y+2):
                try:
                    if self.tiles[x][y].blocked == True:
                        return False # At least 1/8 surround tiles were not clear
                except:
                    # Looped index is out of range due to map edges, disregard this loop
                    pass
        return True # All 8 surrounding tiles were clear

    def place_entities(self, clearing, entities, max_entities_per_room):
        # Get a random number of entities
        number_of_humans = randint(1, max_entities_per_room)

        for x in range(number_of_humans):
            # Random spot in the clearing
            x = randint(clearing.x1 + 1, clearing.x2 - 1)
            y = randint(clearing.y1 + 1, clearing.y2 - 1)
            # if random spot is clear of entities
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                fighter_module = Fighter(hp=10,defense=0,power=randint(1,5))
                ai_module = BasicHuman()
                torch_module = Torch(self,lightLeft=randint(30,70),brightness=randint(4,8))

                # Basic human that will attack player on sight
                human = Entity(x, y, 'H', tcod.white, 'Human', True,RenderOrder.ACTOR,fighter_module,ai_module, None,torch_module)
                entities.append(human)