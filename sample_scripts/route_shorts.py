from xml.etree.ElementTree import Element

import autoeagle


def get_end_points(wire: Element) -> tuple[tuple[float, float]]:
    """Return a pair of two-tuples where the first pair
    is the start coordinates and the second is the stop
    coordinates of the given wire element."""
    p = lambda v: float(wire.get(v))
    return ((p("x1"), p("y1")), (p("x2"), p("y2")))


def wire_length(wire: Element) -> float:
    """Return the length of a wire Element
    using the Pythagorean Theorem."""
    start, stop = get_end_points(wire)
    a = stop[1] - start[1]
    b = stop[0] - start[0]
    return (a**2 + b**2) ** 0.5


def route_shorts(max_distance: float):
    """Route air wires shorter than 'max_distance'
    using the editor's current routing settings."""
    brd = autoeagle.core.Board()
    # Get all wires that don't have a polygon pour,
    # are on layer 19, and are shorter than max_distance.
    airwires = [
        wire
        for signal in brd.signals
        for wire in signal.findall("wire")
        if not signal.find("polygon")
        and wire.get("layer") == "19"
        and wire_length(wire) <= max_distance
    ]
    with autoeagle.core.ScriptWriter() as scr:
        scr.display_all()
        for wire in airwires:
            start, stop = get_end_points(wire)
            scr += f"route ({start[0]} {start[1]}) ({stop[0]} {stop[1]})"
        scr.rats_nest()
        scr.display_layers(brd.get_visible_layers())


if __name__ == "__main__":
    max_distance = float(input("Enter max length of airwires to route: "))
    route_shorts(max_distance)
