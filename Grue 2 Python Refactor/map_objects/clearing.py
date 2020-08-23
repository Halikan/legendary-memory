


# Takes initial coordinates, width and height to define a rectangle for a clearing where no other objects exist
class Clearing:
    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def intersect(self, other):
        if (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1):
            return True
        else:
            return False