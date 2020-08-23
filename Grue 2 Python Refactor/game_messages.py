import tcod

import textwrap
# Messages are used by most modules to provide feedback back to main about what happened within the module
# The Message Log prints out details about actions within the game (e.g. fighting, healing, winning, losing)
class Message:
    def __init__(self, text, color=tcod.white):
        self.text = text
        self.color = color

class MessageLog:
    def __init__(self,x,width,height):
        self.messages=[]
        self.x = x
        self.width = width
        self.height = height

    def add_message(self,message):
        new_msg_lines = textwrap.wrap(message.text,self.width)
        for line in new_msg_lines:
            if len(self.messages) >= self.height:
                del self.messages[0]
            self.messages.append(Message(line,message.color))