import tcod
from game_messages import Message

# Items that are edible are given this module.
# Currently, this means the humans that are edible by the player
# This can be further expanded to other inventory items later
class Food:
    def __init__(self, amount,recovery): # The food item stores how much is left, and how much it's meant to heal
        self.amount = amount
        self.recovery = recovery
        # self.owner defined when initialized by parent Entity object
        self.owner = None

    def consume(self):
        results = []
        self.amount -= 1
        results.append({"message":Message("You eat {0}.".format(self.owner.name), tcod.grey)})
        results.append({"recovery":self.recovery})
        if self.amount <= 0: # When no Food amount is left, this flag tells main to delete the entity.
            results.append({"consumed":self.owner})
        return self.recovery*2, results # Returns 2 values, one int to pass to the eater module, and then another for the healing/message log.

