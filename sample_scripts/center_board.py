import autoeagle


def center_board():
    """Move pcb so the center is at (0, 0)"""
    with autoeagle.core.ScriptWriter() as scr:
        brd = autoeagle.core.Board()
        scr.display_all()
        scr.group_all()
        center = brd.get_center()
        scr += f"move (>0 0) ({-1*center[0]} {-1*center[1]})"
        scr.display_layers(brd.get_visible_layers())


if __name__ == "__main__":
    center_board()
