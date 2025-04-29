from fizgrid.utils import RectangleMoverUtils


success = True
try:
    # Test case 1: Basic Movement
    seg_start = 0
    seg_end = 1
    t_start = 0
    t_end = 2
    shift = 2

    expected_result = {
        0: (0.0, 1.0),
        1: (0.0, 2.0),
        2: (1.0, 2.0),
    }

    result = RectangleMoverUtils.moving_segment_overlap_intervals(
        seg_start, seg_end, t_start, t_end, shift
    )

    if result != expected_result:
        print("Basic movement test failed")
        success = False
except:
    print("Basic movement test exception")
    success = False

try:
    # Test case 2: No Movement
    seg_start = 0
    seg_end = 1
    t_start = 0
    t_end = 2
    shift = 0

    expected_result = {
        0: (0.0, 2.0),
    }

    result = RectangleMoverUtils.moving_segment_overlap_intervals(
        seg_start, seg_end, t_start, t_end, shift
    )

    if result != expected_result:
        print("No movement test failed")
        success = False
except:
    print("No movement test exception")
    success = False

try:
    # Negative Movement
    seg_start = 0
    seg_end = 1
    t_start = 0
    t_end = 2
    shift = -2
    expected_result = {
        0: (0.0, 1.0),
        -1: (0.0, 2.0),
        -2: (1.0, 2.0),
    }
    result = RectangleMoverUtils.moving_segment_overlap_intervals(
        seg_start, seg_end, t_start, t_end, shift
    )
    if result != expected_result:
        print(result)
        print("Negative movement test failed")
        success = False
except:
    print("Negative movement test exception")
    success = False

try:
    # Test case 4: Zero Duration
    seg_start = 0
    seg_end = 1
    t_start = 0
    t_end = 0
    shift = 2

    expected_result = {}

    result = RectangleMoverUtils.moving_segment_overlap_intervals(
        seg_start, seg_end, t_start, t_end, shift
    )

    if result != expected_result:
        print("Zero duration test failed")
        success = False
except:
    print("Zero duration test exception")
    success = False


try:
    # Test with a rectangle
    x_start = 0
    x_end = 1
    y_start = 0
    y_end = 1
    x_shift = 2
    y_shift = 2
    t_start = 0
    t_end = 2
    expected_result = {
        (0, 0): (0.0, 1.0),
        (0, 1): (0.0, 1.0),
        (1, 0): (0.0, 1.0),
        (1, 1): (0.0, 2.0),
        (2, 1): (1.0, 2.0),
        (1, 2): (1.0, 2.0),
        (2, 2): (1.0, 2.0),
    }

    result = RectangleMoverUtils.moving_rectangle_overlap_intervals(
        x_start=x_start,
        x_end=x_end,
        y_start=y_start,
        y_end=y_end,
        x_shift=x_shift,
        y_shift=y_shift,
        t_start=t_start,
        t_end=t_end,
    )

    if expected_result != result:
        print("Rectangle test failed")
        success = False
except:
    print("Rectangle test exception")
    success = False

try:
    # test with a shape as a rectangle
    # Use a triangle at (0,0), (1,0), (0,1)
    shape = [[0, 0], [1, 0], [0, 1]]
    x_coord = 0
    y_coord = 0
    x_shift = 2
    y_shift = 2
    t_start = 0
    t_end = 2
    expected_result = {
        (0, 0): (0.0, 1.0),
        (0, 1): (0.0, 1.0),
        (1, 0): (0.0, 1.0),
        (1, 1): (0.0, 2.0),
        (2, 1): (1.0, 2.0),
        (1, 2): (1.0, 2.0),
        (2, 2): (1.0, 2.0),
    }

    result = RectangleMoverUtils.moving_shape_overlap_intervals(
        shape=shape,
        x_coord=x_coord,
        y_coord=y_coord,
        x_shift=x_shift,
        y_shift=y_shift,
        t_start=t_start,
        t_end=t_end,
    )
    if expected_result != result:
        print("Shape test failed")
        success = False
except:
    print("Shape test exception")
    success = False

if success:
    print("test_03.py: passed")
else:
    print("test_03.py: failed")
