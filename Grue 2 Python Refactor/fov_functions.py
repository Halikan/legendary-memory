import tcod

def initialize_fov(forest_map):
    # Create a new field of view map that is based on the Tile properties block_sight and blocked
    fov_map = tcod.map_new(forest_map.width, forest_map.height)

    for y in range(forest_map.height):
        for x in range(forest_map.width):
            tcod.map_set_properties(fov_map, x, y, not forest_map.tiles[x][y].block_sight,
                                    not forest_map.tiles[x][y].blocked)

    return fov_map

def recompute_fov(fov_map, x, y, radius):
    # Recompute based on the existing criteria, and given coordinates/radius to work with
    tcod.map_compute_fov(fov_map, x, y, radius)