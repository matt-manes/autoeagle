import argparse
import inspect
import itertools
import shutil
from pathlib import Path
from xml.etree import ElementTree

from autoeagle import autoeagle_config


class EagleFile:
    """Base class representing and parsing an Eagle file."""

    def __init__(self, file: str = None):
        """:param file: Path to an Eagle file.
        If None, getting the path from command line args
        will be attempted. If that fails, the user will
        be prompted for a file path.

        A backup of the file will be created during the
        initialization."""
        if file:
            file = Path(file)
        else:
            args = self.get_args()
            file = args.file
        self.path = file
        self.tree = ElementTree.parse(self.path)
        self.root = self.tree.getroot()

        self.drawing = self.root.find("drawing")

        self.settings = self.drawing.find("settings").findall("setting")
        self.grid = self.drawing.find("grid")
        self.layers = self.drawing.find("layers").findall("layer")

        shutil.copy(self.path, str(self.path.with_stem(f"{self.path.stem}_Bckup")))

    def get_parser(self) -> argparse.ArgumentParser:
        """Returns an argparse ArgumentParser instance.
        This is in a separate function so additional args
        can be added in subclass without having to
        override the rest of the self.get_args() function.

        Only arg added here is for a file path."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "file",
            type=str,
            nargs="?",
            default=None,
            help=""" Path to an Eagle file. """,
        )
        return parser

    def get_args(self) -> argparse.Namespace:
        """Get file path from command line
        or prompt user for file path."""
        parser = self.get_parser()
        args = parser.parse_args()
        if not args.file:
            args.file = input("Enter path to an Eagle file: ")
        args.file = Path(args.file)
        return args

    def save(self):
        self.tree.write(str(self.path), encoding="utf-8")

    def get_names(self, elements: list[ElementTree.Element]) -> list[str]:
        """Return a list of 'name' attributes for each
        ElementTree Element in 'elements' list."""
        return self.get_attribute("name", elements)

    def get_attribute(
        self, attribute: str, elements: list[ElementTree.Element]
    ) -> list[str]:
        """Return a list of the specified attribute for a list of elements.

        >>> schem = autoeagle.Schematic("schem.sch")
        >>> part_values = schem.get_attribute("value", schem.parts)
        >>> brd = autoeagle.Board("board.brd")
        >>> layer_colors = brd.get_attribute("color", brd.layers)"""
        return [element.get(attribute) for element in elements]


class Schematic(EagleFile):
    """Class representing an Eagle schematic file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.schematic = self.drawing.find("schematic")

        self.libraries = self.schematic.find("libraries").findall("library")
        self.classes = self.schematic.find("classes")
        self.parts = self.schematic.find("parts").findall("part")
        self.sheets = self.schematic.find("sheets").findall("sheet")


class Board(EagleFile):
    """Class representing an Eagle board file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.board = self.drawing.find("board")

        # This contains the 'wire' elements outlining the board
        # No idea why Autodesk calls it 'plain'
        self.plain = self.board.find("plain")
        self.outline = self.plain
        self.libraries = self.board.find("libraries").findall("library")
        self.classes = self.board.find("classes").findall("class")
        self.designrules = self.board.find("designrules").findall("param")
        self.autorouter = self.board.find("autorouter")
        # These are all the actual parts on the board
        self.elements = self.board.find("elements").findall("element")
        self.parts = self.elements
        self.signals = self.board.find("signals").findall("signal")

    def get_packages(self, attribute: str = None) -> list[str | ElementTree.Element]:
        """Return a list of package elements that are used
        in the board file.

        :param attribute: If given, the returned list will only
        contain the given attribute for each element instead of
        the whole ElementTree.Element ."""
        packages = [
            package
            for package in self.board.findall(".//libraries/library/packages/package")
        ]
        return self.get_attribute(attribute, packages) if attribute else packages

    def get_smd_packages(
        self, attribute: str = None
    ) -> list[str | ElementTree.Element]:
        """Return a list of smd packages used in the board file.

        :param attribute: If given, the returned list will only
        contain the given attribute for each element instead of
        the whole ElementTree.Element ."""
        packages = [
            package
            for package in self.get_packages()
            if type(package.find("smd")) is ElementTree.Element
        ]
        return self.get_attribute(attribute, packages) if attribute else packages

    def get_smd_parts(self, attribute: str = None) -> list[str | ElementTree.Element]:
        """Filter self.parts for smd parts.

        :param attribute: If given, the returned list will only
        contain the given attribute for each element instead of
        the whole ElementTree.Element ."""
        smd_packages = self.get_smd_packages("name")
        parts = [part for part in self.parts if part.get("package") in smd_packages]
        return self.get_attribute(attribute, parts) if attribute else parts

    def get_bounds(self) -> dict[str, float]:
        """Return a dictionary representing
        the minimum and maximum x and y coordinates
        of the board."""
        wires = [
            wire for wire in self.plain.findall("wire") if wire.get("layer") == "20"
        ]
        get_coords = lambda n: [
            float(v)
            for wire in wires
            for v in itertools.chain([wire.get(f"{n}1"), wire.get(f"{n}2")])
        ]
        x = get_coords("x")
        y = get_coords("y")
        return {"x0": min(x), "xf": max(x), "y0": min(y), "yf": max(y)}

    def get_dimensions(self) -> tuple[float, float]:
        """Returns a two-tuple containing
        the width and height of the board's
        bounding box."""
        bounds = self.get_bounds()
        return (bounds["xf"] - bounds["x0"], bounds["yf"] - bounds["y0"])

    def get_center(self) -> tuple[float, float]:
        """Returns a two-tuple containing
        the x,y center point of the board's
        bounding box."""
        bounds = self.get_bounds()
        midpoint = lambda n: (bounds[f"{n}f"] + bounds[f"{n}0"]) * 0.5
        return (midpoint("x"), midpoint("y"))

    def get_area(self) -> float:
        """Returns the area of the board's bounding box.
        Note: This is not the same as the board's
        physical area for shapes other than rectangular ones.
        It also doesn't account for cut-outs."""
        wxh = self.get_dimensions()
        return wxh[0] * wxh[1]

    def get_visible_layers(self) -> list[str]:
        """Returns a list of visible layers."""
        return [
            layer.get("name") for layer in self.layers if layer.get("visible") == "yes"
        ]


class ScriptWriter:
    """Class for writing Eagle script files.
    These files use the Editor command syntax
    as documented in the Eagle manual.
    Scipts generated by this class will be invoked
    and executed within Eagle after returning
    from the invoking Ulp file for your Python
    script.

    The preferred usage of this class is
    with a context manager. When used with a context
    manager, you don't need to remember to
    call the save() method at the end of the script.
    You also don't need to remember to add 'write;'
    as the last command, as the save() function adds it for you.
    Commands can be added with the '+=' operator.
    The Eagle syntax specifies each command ends with
    ';'. If you leave it off of an added command,
    it will be added for you.
    Some script commands are provided as member functions.
    For further script options, refer to the Eagle help menu.

    e.x. Moving the center of the board to (0,0)
    >>> brd = Board()
    >>> with ScriptWriter(brd.path) as scr:
    >>>     center = brd.get_center()
    >>>     scr.group_all() # Adds "group all;" to commands
    >>>     scr += f"move (>0 0) (-{center[0]} -{center[1]})"""

    def __init__(
        self,
        script_name: str = None,
    ):
        """The .scr file will be saved to a "scripts" subfolder within the same
        directory as the eagle_file param.

        :param eagle_file: The path to the Eagle file
        the script is being written for.

        :param script_name: The name of the script creating the instance.
        If None, the inspect module will be used to determine the script name."""
        if not script_name:
            script_name = (Path(inspect.stack()[1].filename)).stem
        scriptsdir = Path(autoeagle_config.load_config()["scriptsdir"])
        self.path = scriptsdir / f"{script_name}.scr"
        self.commands = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.save()

    def __iadd__(self, command: str):
        if not command.endswith(";"):
            command += ";"
        self.commands.append(command)
        return self

    def save(self):
        self += "write"
        self.path.write_text("\n".join(self.commands))

    def group_all(self):
        """Put everything on a visible layer into a group."""
        self += "group all"

    def display_all(self):
        """Make every layer in the design visible."""
        self += "display all"

    def display_layers(self, layers: list[str]):
        """Displays only the layers in 'layers'."""
        self += f"display none {' '.join(layers)}"

    def _coordinate_string(self, coordinates: list[tuple[float, float]]) -> str:
        """Return command snippet for coordinates to be used with draw commands.

        :param coordinates: A list of two-tuples. A string will
        be returned specifying the coordinates in the same order
        as the param."""
        return " ".join(
            f"({coordinate[0]} {coordinate[1]})" for coordinate in coordinates
        )

    def _rectangle_coordinates(
        self, x0: float, xf: float, y0: float, yf: float
    ) -> list[tuple[float, float]]:
        """Return a list of two-tuples that describe
        a rectangle given the coordinates of the sides.

        :param x0,xf,y0,yf: Coordinates describing
        the sides of a rectangle."""

        return [(x0, y0), (x0, yf), (xf, yf), (xf, y0), (x0, y0)]

    def draw_group(self, coordinates: list[tuple[float, float]]):
        """Draw a group bounded by 'coordinates'.

        :param coordinates: A list of two-tuples specifying
        the path to take when drawing the group."""
        self += f"group {self._coordinate_string(coordinates)}"

    def draw_rectangle_group(self, x0: float, xf: float, y0: float, yf: float):
        """Draw a rectangular group whose sides are described by the given coordinates."""
        self.draw_group(self._rectangle_coordinates(x0, xf, y0, yf))

    def draw(
        self,
        coordinates: list[tuple[float, float]],
        layer: str = None,
        width: float = None,
    ):
        """Draw a line throught the given series of coordinate points.

        :param coordinates: A list of two-tuples specifying
        the path to take when drawing the line.

        :param layer: The layer to draw the line on.
        If None, the currently active layer is used.

        :param width: The width of the line.
        If None, the currently active width is used.

        >>> # Draw a line of width 1 on layer "tplace" from (0 0) to (10 0) to (3 5)
        >>> draw([(0, 0), (10, 0), (3,5)], "tPlace", 1)"""

        if layer:
            self += f"layer {layer}"
        if width:
            self += f"width {width}"
        self += f"line {self._coordinate_string(coordinates)}"

    def draw_rectangle(
        self,
        x0: float,
        xf: float,
        y0: float,
        yf: float,
        layer: str = None,
        width: float = None,
    ):
        """Draw a rectangle whose sides are described by the given
        coordinates: x0, xf, y0, yf.

        :param layer: The layer to draw the line on.
        If None, the currently active layer is used.

        :param width: The width of the line.
        If None, the currently active width is used.

        >>> # Draw a 10 x 10 board outline of width 1 centered at (0, 0)
        >>> draw_rectangle(-5, 5, -5, 5, "Dimension", 1)"""
        self += self.draw(self._rectangle_coordinates(x0, xf, y0, yf), layer, width)

    def rats_nest(self, ripup_polygons: bool = True):
        """Run the rats nest command

        :param ripup_polygons: If True, run 'ripup @'
        after running rats nest. Eagle gets real
        slow when polygons are visible."""

        self += "ratsnest"
        if ripup_polygons:
            self += "ripup @"
