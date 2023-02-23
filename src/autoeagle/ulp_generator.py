import argparse
import sys
from pathlib import Path

from autoeagle import autoeagle_config

root = Path(__file__).parent


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "pyscript_path",
        type=str,
        help=""" The path to the Python script to generate a Ulp file for. """,
    )

    args = parser.parse_args()

    return args


def load_template(script_template: bool = False) -> str:
    """Return a ulp template.

    :param script_template: If True,
    return ulp_script_template.
    If False, return ulp_template."""
    if script_template:
        return (root / "ulp_script_template.txt").read_text()
    else:
        return (root / "ulp_template.txt").read_text()


def create_ulp(pyscript_path: str):
    pyscript = Path(pyscript_path).absolute()
    pyname = pyscript.stem
    ulpdir = Path(autoeagle_config.load_config()["ulpdir"])
    savepath = (ulpdir / pyname).with_suffix(".ulp")
    template = load_template(
        script_template=True if "ScriptWriter" in pyscript.read_text() else False
    )
    for replacer in [
        ("$executable", sys.executable.replace("\\", "/")),
        ("$script_path", str(pyscript).replace("\\", "/")),
        (
            "$script_file",
            pyname,
        ),  # There is no "$script_file" in the ulp_template so this just does nothing for non ScriptWriter scripts
    ]:
        template = template.replace(replacer[0], replacer[1])
    savepath.write_text(template)


def main(args: argparse.Namespace = None):
    if not args:
        args = get_args()
    if not autoeagle_config.is_configured():
        autoeagle_config.prompt_to_configure()
    create_ulp(args.pyscript_path)


if __name__ == "__main__":
    main(get_args())
