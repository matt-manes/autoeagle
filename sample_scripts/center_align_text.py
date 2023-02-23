import autoeagle


def center_align_text():
    """Change all text to be center aligned."""
    with autoeagle.core.ScriptWriter() as scr:
        # Only display layers "tNames", "bNames", "tValues", and "bValues"
        brd = autoeagle.core.Board()
        visible_layers = brd.get_visible_layers()
        scr += "display none 25 26 27 28"
        scr.group_all()
        scr += "change align center (>0 0)"
        # Switch back to originally visible layers
        scr.display_layers(visible_layers)


if __name__ == "__main__":
    center_align_text()
