from argusloop.screen import normalized_to_screen


def test_normalized_corners_are_in_bounds():
    assert normalized_to_screen(0, 0, (1920, 1080)) == (0, 0)
    assert normalized_to_screen(1000, 1000, (1920, 1080)) == (1919, 1079)


def test_normalized_center():
    assert normalized_to_screen(500, 500, (1920, 1080)) == (960, 540)

