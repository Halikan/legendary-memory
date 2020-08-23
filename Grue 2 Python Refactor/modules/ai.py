import tcod

class BasicHuman:
    def __init__(self):
        self.owner = None
        self.chasing = False
    def take_turn(self, target, fov_map, forestMap, entities):
        results = []
        human = self.owner
        self.chasing = False
        # if the human is within the player's field of view, chase them down
        if tcod.map_is_in_fov(fov_map, human.x, human.y):
            self.chasing = True
            if human.distance_to(target) >= 2:
                human.move_astar(target, entities, forestMap)
            # When within range, attack player, and return results
            elif target.fighter.hp > 0:
                attack_results = human.fighter.attack(target)
                results.extend(attack_results)
        return results
    