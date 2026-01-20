from game_data import BOARD_DATA


def move_with_dice_path(cur_pos: str, steps: int):
    track = BOARD_DATA.track()
    current_position = track.index(cur_pos)
    board_size = len(track)
    path = []
    for i in range(steps + 1):
        pos = (current_position + i) % board_size
        path.append(track[pos])
    return path
