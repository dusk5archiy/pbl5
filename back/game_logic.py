from game_data import TRACK_DATA


def move_with_dice_path(cur_pos: str, steps: int, track: list[str] = TRACK_DATA):
    current_position = track.index(cur_pos)
    board_size = len(track)
    path = []
    for i in range(steps + 1):
        pos = (current_position + i) % board_size
        path.append(track[pos])
    return path
