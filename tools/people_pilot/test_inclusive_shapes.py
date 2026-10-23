from inclusive_shapes import child_coordinate


def test_raised_hand_uses_body_scale_even_above_head_threshold():
    assert child_coordinate((-.35, -.035, 1.58), (.37, 0, 0)) == (.16, -.021, .948)


def test_head_enlargement_keeps_neck_datum_and_enlarges_head_only():
    assert child_coordinate((0, 0, 1.4), is_head=True)[2] == .84
    head = child_coordinate((.10, 0, 1.78), is_head=True)
    hand = child_coordinate((.10, 0, 1.78), is_head=False)
    assert head[0] > hand[0]
    assert head[2] > hand[2]
