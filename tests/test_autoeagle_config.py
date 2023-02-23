from pathlib import Path

import pytest
import tomlkit

from autoeagle import autoeagle_config

root = Path(__file__).parent
config_path = root.parent / "src" / "autoeagle" / "autoeagle.toml"


def clear_config():
    config_path.write_text(tomlkit.dumps({"eagledir": "", "ulpdir": ""}))


def test__autoeagle_config__load_config():
    assert len(autoeagle_config.load_config()) > 0


def test__autoeagle_config__configure():
    autoeagle_config.configure(str(root / "EAGLE"))
    config = autoeagle_config.load_config()
    assert config["eagledir"] == str(root / "EAGLE")
    assert config["ulpdir"] == str(root / "EAGLE" / "ulps")
    assert config["scriptsdir"] == str(root / "EAGLE" / "scripts")


def test__autoeagle_config__is_configured():
    assert autoeagle_config.is_configured()


def test__autoeagle_config__get_args():
    ...


def test__autoeagle_config__main():
    clear_config()

    class MockArgs:
        def __init__(self):
            self.eagledir = root / "EAGLE"
            self.ulpdir = root / "EAGLE" / "ulps"
            self.scriptsdir = root / "EAGLE" / "scripts"

    args = MockArgs()
    autoeagle_config.main(args)
    config = autoeagle_config.load_config()
    assert config["eagledir"] == str(args.eagledir)
    assert config["ulpdir"] == str(args.ulpdir)
    assert config["scriptsdir"] == str(args.scriptsdir)
    clear_config()


def test__autoeagle_config__prompt_to_configure():
    ...
