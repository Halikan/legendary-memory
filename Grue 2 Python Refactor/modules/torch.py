import tcod
from game_messages import Message
from fov_functions import initialize_fov, recompute_fov

# This module is used to render light emitting from the owner entity
class Torch:
    def __init__(self, forestMap, lightLeft, brightness=1):
        self.maxLight = lightLeft
        self.lightLeft = lightLeft
        self.brightness = brightness
        self.fov = initialize_fov(forestMap)
        # self.owner defined when initialized by parent Entity object
        self.owner = None

    def updateFov(self):
        if self.owner==None:
            print("Error, a torch module has no defined owner yet")
        else:
            recompute_fov(self.fov,self.owner.x,self.owner.y,self.brightness)
    def burn(self, fov_map):
        results=[]
        self.lightLeft -= 1

        if self.lightLeft <= 0:
            self.brightness = 0
            results.append({"torch_out":self.owner}) # Flag used to alert main.py to remove an entity's torch module
            
            visible = tcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y)
            if visible:
                results.append({"message":Message("{0}'s torch has gone out!".format(self.owner.name.capitalize()), tcod.light_grey)})

        # progressively dim bright lights to a ratio based on their total runtime.
        # torches will stay at their minimum brightness near the end of life
        elif int(self.lightLeft/self.maxLight)*10 < self.brightness:
            if self.brightness > 0:
                self.brightness -= 1
        return results