import tcod
from game_messages import Message

# This fighter module is provided to each entity that can perform combat, including the player.
class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        # self.owner defined when initialized by parent Entity object
        self.owner = None

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        if self.hp <= 0: # This flag tells main.py to perform death functions for an entity
            results.append({'dead': self.owner})

        return results

    def heal(self, amount):
        results = []

        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        # Messages are returned as feedback to print in the message log.
        results.append({'message':Message("{0} recovered {1} HP!".format(self.owner.name.capitalize(), str(amount)), tcod.green)})

        return results

    def attack(self, target):
        results = []
        damage = self.power - target.fighter.defense

        if damage > 0: # Player being attacked is specifically returned in red due to danger to the player
            if target.name == 'Player':
                textColor = tcod.red
            else:
                textColor = tcod.white
            results.append({'message':Message("{0} attacks {1} for {2} HP damage!".format(self.owner.name.capitalize(), target.name, str(damage)), textColor)})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'message':Message("{0} attacks {1}, but does no damage!".format(self.owner.name.capitalize(), target.name), tcod.white)})
        return results