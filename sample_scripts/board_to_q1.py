import autoeagle


def board_to_q1():
    """Move the pcb to quadrant 1 (bottom left bounds at (0, 0))"""
    with autoeagle.core.ScriptWriter() as scr:
        brd = autoeagle.core.Board()
        bounds = brd.get_bounds()
        scr.display_all()
        scr.group_all()
        scr += f"move (>0 0) ({-1*bounds['x0']} {-1*bounds['y0']})"
        scr.display_layers(brd.get_visible_layers())


if __name__ == "__main__":
    board_to_q1()
