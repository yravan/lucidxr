def interpolate(*ticks, x, scale):
    """
    each tick is a list of three values, [r, g, b]. We want to use x to intepolate
    between the ticks. x should be in the range [0, 1], assuming
    each tick takes an equal portion.
    """
    assert 0 <= x <= 1, "x must be in the range [0, 1]"
    assert len(ticks) >= 2, "at least two ticks are required"
    assert all(len(tick) == 3 for tick in ticks), "each tick must have three values"

    # Calculate the index of the tick to interpolate between
    tick_index = int(x * (len(ticks) - 1))
    next_tick_index = min(tick_index + 1, len(ticks) - 1)

    # Calculate the interpolation factor
    t = (x * (len(ticks) - 1)) - tick_index

    # Interpolate between the two ticks
    return [scale * (1 - t) * ticks[tick_index][i] + scale * t * ticks[next_tick_index][i] for i in range(3)]
