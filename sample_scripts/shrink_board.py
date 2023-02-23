import autoeagle


def shrink_board(clearance: float):
    """Shrink board outline to be a given amount
    away from the outermost components.

    :param clearance: The minimum distance between
    the board edge and a component's center."""
    brd = autoeagle.core.Board()
    get_coordinates = lambda n: list(float(part.get(n)) for part in brd.parts)
    xs = get_coordinates("x")
    ys = get_coordinates("y")
    left = min(xs) - clearance
    right = max(xs) + clearance
    bottom = min(ys) - clearance
    top = max(ys) + clearance
    x0, xf, y0, yf = brd.get_bounds().values()

    with autoeagle.core.ScriptWriter() as scr:
        movements = [
            (x0, yf, left, top),
            (xf, yf, right, top),
            (xf, y0, right, bottom),
            (x0, y0, left, bottom),
        ]
        scr.display_layers(["Dimension"])
        for m in movements:
            scr += f"move ({m[0]} {m[1]}) ({m[2]} {m[3]})"
        scr.display_layers(brd.get_visible_layers())


if __name__ == "__main__":
    clearance = float(input("Enter minimum board clearance: "))
    shrink_board(clearance)
