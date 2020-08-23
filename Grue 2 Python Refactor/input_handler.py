import tcod



def handle_input(event):

    # If the event is a key that has been pressed, process here
    if event.type == "KEYDOWN":
        # Vim controls
        if event.sym == tcod.event.K_j:
            return {'move': (0, -1)}
        elif event.sym == tcod.event.K_k:
            return {'move': (0, 1)}
        elif event.sym == tcod.event.K_h:
            return {'move': (-1, 0)}
        elif event.sym == tcod.event.K_l:
            return {'move': (1, 0)}
        # Vim diagonals
        if event.sym == tcod.event.K_y:
            return {'move': (-1, -1)}
        if event.sym == tcod.event.K_u:
            return {'move': (1, -1)}
        elif event.sym == tcod.event.K_b:
            return {'move': (-1, 1)}
        elif event.sym == tcod.event.K_n:
            return {'move': (1, 1)}

        # Arrow keys
        elif event.sym == tcod.event.K_UP:
            return {'move': (0, -1)}
        elif event.sym == tcod.event.K_DOWN:
            return {'move': (0, 1)}
        elif event.sym == tcod.event.K_LEFT:
            return {'move': (-1, 0)}
        elif event.sym == tcod.event.K_RIGHT:
            return {'move': (1, 0)}

        # Numpad cardinal input
        elif event.sym == tcod.event.K_KP_8:
            return {'move': (0, -1)}
        elif event.sym == tcod.event.K_KP_2:
            return {'move': (0, 1)}
        elif event.sym == tcod.event.K_KP_4:
            return {'move': (-1, 0)}
        elif event.sym == tcod.event.K_KP_6:
            return {'move': (1, 0)}
        # Diagonal numpad input
        elif event.sym == tcod.event.K_KP_7:
            return {'move': (-1, -1)}
        elif event.sym == tcod.event.K_KP_9:
            return {'move': (1, -1)}
        elif event.sym == tcod.event.K_KP_1:
            return {'move': (-1, 1)}
        elif event.sym == tcod.event.K_KP_3:
            return {'move': (1, 1)}

        # No movement/wait with Space or numpad 5
        if event.sym == tcod.event.K_KP_5 or event.sym == tcod.event.K_SPACE:
            return {'move': (0, 0)}

        # Rest
        if event.sym == tcod.event.K_r:
            return {'rest': True}

        # Eat
        if event.sym == tcod.event.K_e:
            return {'eat':True}

        # Esc key, to quit game
        elif event.sym== tcod.event.K_ESCAPE:
            print("Escape key detected")
            raise SystemExit()
    
    if event.type == "QUIT":
        raise SystemExit()
    
    # Default case to return an empty object if no recognized input is given
    else:
        return {}