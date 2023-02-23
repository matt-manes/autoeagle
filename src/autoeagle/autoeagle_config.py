import argparse
from pathlib import Path

import tomlkit


def is_configured() -> bool:
    config = load_config()
    return config["eagledir"] != ""


def configure(eagledir: str, ulpdir: str = None, scriptsdir: str = None):
    """Configure autoeagle configuration file.

    :param eagledir: Path to user's Eagle directory.
    (Not the executable installation directory, but the one containing
    projects, libraries, ulps, etc.)

    :param ulpdir: Path to user's ulp directory.
    Only necessary if different from the standard ulp
    directory path.

    :param scriptsdir: Path to user's scripts directory.
    Only necessary if different from the standard scripts
    directory path."""
    config = load_config()
    eagledir = Path(eagledir)
    ulpdir = Path(ulpdir) if ulpdir else Path(eagledir) / "ulps"
    scriptsdir = Path(scriptsdir) if scriptsdir else Path(eagledir) / "scripts"
    configpath = Path(__file__).parent / "autoeagle.toml"
    # tomlkit doesn't like Path objects
    config["eagledir"] = str(eagledir)
    config["ulpdir"] = str(ulpdir)
    config["scriptsdir"] = str(scriptsdir)
    configpath.write_text(tomlkit.dumps(config))
    print("Autoeagle configuration updated.")
    print(f"Manual adjustments can be made here: {configpath}")


def load_config() -> dict:
    """Load autoeagle configuration file."""
    config = tomlkit.loads((Path(__file__).parent / "autoeagle.toml").read_text())
    return config


def prompt_to_configure() -> str:
    """Prompt user to provide their EAGLE
    directory path and configure autoeagletoml."""
    print("Autoeagle config file is not configured.")
    eagledir = input(
        "Enter path to your 'EAGLE' directory (contains projects, libraries, etc.): "
    )
    configure(eagledir)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-e",
        "--eagledir",
        type=str,
        help=""" Path to user's Eagle directory.
    (Not the executable installation directory, but the one containing
    projects, libraries, ulps, etc.) """,
    )

    parser.add_argument(
        "-u",
        "--ulpdir",
        type=str,
        default=None,
        help=""" Path to user's ulp directory.
    Only necessary if different from the standard ulp
    directory path. """,
    )

    parser.add_argument(
        "-s",
        "--scriptsdir",
        type=str,
        default=None,
        help=""" Path to user's scripts directory.
    Only necessary if different from the standard scripts
    directory path. """,
    )

    args = parser.parse_args()

    return args


def main(args: argparse.Namespace = None):
    if not args:
        args = get_args()
    configure(args.eagledir, args.ulpdir, args.scriptsdir)


if __name__ == "__main__":
    main(get_args())
