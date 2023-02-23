import json
from pathlib import Path

import pytest

from autoeagle import autoeagle_config, core

root = Path(__file__).parent
dummypath = root / "EAGLE" / "projects" / "dummy"

expected_items = json.loads((root / "expected.json").read_text())


def load_schem() -> core.Schematic:
    """Create and return Schematic object."""
    schempath = dummypath / "dummy.sch"
    return core.Schematic(schempath)


def load_board() -> core.Board:
    """Create and return Board object."""
    boardpath = dummypath / "dummy.brd"
    return core.Board(boardpath)


def assert_expected(attribute_name: str, found_elements: list):
    """Assert that 'expected_items[attribute_name]' is the same as
    'found_elements'."""
    assert all(item in found_elements for item in expected_items[attribute_name])
    assert len(expected_items[attribute_name]) == len(found_elements)


def test__autoeagle__save():
    ...


def test__autoeagle__Schematic_libraries():
    schem = load_schem()
    assert_expected("libraries", schem.get_attribute("name", schem.libraries))


def test__autoeagle__Schematic_parts():
    schem = load_schem()
    assert_expected("parts", schem.get_attribute("name", schem.parts))


def test__autoeagle__Board__get_packages():
    board = load_board()
    assert_expected("packages", board.get_packages("name"))


def test__autoeagle__Board__get_smd_packages():
    board = load_board()
    assert_expected("smd_packages", board.get_smd_packages("name"))


def test__autoeagle__Board__part_values():
    board = load_board()
    assert_expected("part_values", board.get_attribute("value", board.parts))


def test__autoeagle__Board__smd_part_values():
    board = load_board()
    assert_expected("smd_part_values", board.get_smd_parts("value"))


def test__autoeagle__Board__get_bounds():
    board = load_board()
    assert board.get_bounds() == {"x0": 0, "xf": 30, "y0": 0, "yf": 30}


def test__autoeagle__Board__get_dimensions():
    board = load_board()
    assert board.get_dimensions() == (30, 30)


def test__autoeagle__Board__get_center():
    board = load_board()
    assert board.get_center() == (15, 15)


def test__autoeagle__Board__get_area():
    board = load_board()
    assert board.get_area() == 900
