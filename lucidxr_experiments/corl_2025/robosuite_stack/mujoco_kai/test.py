def find_ep_id(index, data_sizes):
    ep_id = -1
    rel_idx = 0
    for i, length in enumerate(data_sizes):
        index -= length
        if index < 0:
            ep_id = i
            rel_idx = index + length
            break

    assert ep_id >= 0, "Index too large."

    return ep_id, rel_idx

def test_find_ep_id():
    # Case 1: Simple case
    assert find_ep_id(0, [10, 20, 30]) == (0, 0)
    assert find_ep_id(5, [10, 20, 30]) == (0, 5)
    assert find_ep_id(10, [10, 20, 30]) == (1, 0)
    assert find_ep_id(29, [10, 20, 30]) == (1, 19)
    assert find_ep_id(30, [10, 20, 30]) == (2, 0)
    assert find_ep_id(59, [10, 20, 30]) == (2, 29)

    # Case 2: Index at boundary
    assert find_ep_id(3, [3, 3, 3]) == (1, 0)

    # Case 3: Single episode
    assert find_ep_id(2, [5]) == (0, 2)

    # Case 4: Index too large
    try:
        find_ep_id(60, [10, 20, 30])
        assert False, "Should have raised AssertionError"
    except AssertionError as e:
        assert str(e) == "Index too large."

    # Case 5: Empty data_sizes
    try:
        find_ep_id(0, [])
        assert False, "Should have raised AssertionError"
    except AssertionError as e:
        assert str(e) == "Index too large."

    print("All test cases passed.")

if __name__ == "__main__":
    test_find_ep_id()