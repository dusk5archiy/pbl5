def change_track_on_r_condition(steps: int, force: bool = False):
    return force or steps % 2 == 0


def change_track_on_cau_condition(steps: int, force: bool = False):
    return force or steps >= 9
