import tcod
from game_messages import Message

# Component for the player, so they can have a hunger bar used for a win/lose condition
class Eater:
    def __init__(self, maxHunger,currentHunger=None):
        self.maxHunger = maxHunger
        if currentHunger:
            self.hunger = currentHunger
        else:
            self.hunger = maxHunger
        self.owner = None

    def eat(self, amount): # Eating sends back a message and flag if the maximum hunger is reached
        results = []
        self.hunger += amount
        if self.hunger >= self.maxHunger:
            results.append({'message':Message("You are stuffed!", tcod.gold)})
            results.append({'stuffed': True})
        return results

    def starve(self): # The player is intended to starve some each turn. This flag determines the consequences of starving (HP loss)
        results = []
        self.hunger -= 1
        if self.hunger <=0:
            self.hunger = 0
            results.append({'message': Message("You are starving to death!", tcod.yellow)})
            results.append({'starving': True})
        return results