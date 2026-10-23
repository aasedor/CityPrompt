from inclusive_shapes import child_coordinate
import inclusive_shapes


def test_raised_hand_uses_body_scale_even_above_head_threshold():
    assert child_coordinate((-.35, -.035, 1.58), (.37, 0, 0)) == (.16, -.021, .948)


def test_head_enlargement_keeps_neck_datum_and_enlarges_head_only():
    assert child_coordinate((0, 0, 1.4), is_head=True)[2] == .84
    head = child_coordinate((.10, 0, 1.78), is_head=True)
    hand = child_coordinate((.10, 0, 1.78), is_head=False)
    assert head[0] > hand[0]
    assert head[2] > hand[2]


def test_relaxed_stance_uses_person_hip_width_and_preserves_ankle_height():
    assert hasattr(inclusive_shapes, 'relaxed_ankle_target')
    assert inclusive_shapes.relaxed_ankle_target((.11, .02, .94), (.22, .08, .09), 'l', 1.75) == (.125, .08, .09)
    assert inclusive_shapes.relaxed_ankle_target((-.11, .02, .94), (-.22, .08, .09), 'r', 1.75) == (-.125, .08, .09)
