# Autoeagle

Automate tasks in Autodesk's Eagle software by invoking Python scripts from the program's command line.<br>

## Installation

Install with:

<pre>
pip install autoeagle
</pre>

## Setup

Before using Autoeagle, you should run the command line tool `autoeagle_config`.<br>
The tool's help display is:
<pre>
>autoeagle_config -h
usage: autoeagle_config [-h] [-e EAGLEDIR] [-u ULPDIR] [-s SCRIPTSDIR]

options:
  -h, --help            show this help message and exit
  -e EAGLEDIR, --eagledir EAGLEDIR
                        Path to user's Eagle directory. (Not the executable installation directory, but the one containing projects, libraries, ulps, etc.)
  -u ULPDIR, --ulpdir ULPDIR
                        Path to user's ulp directory. Only necessary if different from the standard ulp directory path.
  -s SCRIPTSDIR, --scriptsdir SCRIPTSDIR
                        Path to user's scripts directory. Only necessary if different from the standard scripts directory path.
</pre>

Standard Eagle installations should only need to provide the `-e/--eagledir` argument.

## Basic Usage
The basic workflow is to write a Python script that you would want to invoke from within Eagle,
then pass the path to the script as an argument to the included `generate_ulp` tool.<br>
This tool will create a ulp file named after your Python file.<br>
Then, inside Eagle, invoke it with the `run` command from the editor's command line like you would any other ulp.<br>
Because the ulp launches your Python file, you only need to use this tool for a script once unless
you move the Python file to a different location or start using the `ScriptWriter` class in the script when you didn't before.

There are three main components to use in this package: `autoeagle.core.Schematic`, `autoeagle.core.Board`, and `autoeagle.core.ScriptWriter`.<br>
The Schematic and Board classes are used to parse and manipulate the Eagle `.sch` and `.brd` xml files, respectively.<br>
The ScriptWriter class is used to generate `.scr` files that can be executed by Eagle when returning from the ulp invocation.<br>
<br>
When creating a Schematic or Board object, the file will be parsed during initialization.<br>
For example, all the parts used in the `dummy.sch` schematic (located in `autoeagle/tests/EAGLE/projects/dummy`) and their values can be printed out using
<pre>
>>> import autoeagle
>>> schem = autoeagle.core.Schematic("dummy.sch")
>>> parts = schem.get_attribute("name", schem.parts)
>>> values = schem.get_attribute("value", schem.parts)
>>> print(*[f"{part}: {value} for part,value in zip(parts,values)], sep="\n")
</pre>
The output:
<pre>
R1 1meg
R2 10k
R3 1meg
C1 1u
GND1 None
U$1 None
IC1 TL072
R4 100k
C2 100p
C3 100p
R5 10k
GND2 None
R6 10k
C4 1u
R7 100k
GND4 None
POWER None
GND5 None
GND6 None
V1 None
V2 None
V3 None
R8 10k
R9 10k
GND7 None
C5 10u
GND3 None
U$2 None
INPUT generic
GND8 None
OUTPUT generic
GND9 None
</pre>

<br>
When launching a Python script from Eagle with the generated ulp, the schematic or board file
will be passed to the Schematic or Board constructor without needing to be specified like the above example.<br>
<br>

## Walkthrough

In the 'sample_scripts' folder included with this package are some simple examples of how to use this package.<br>
We'll walk through the basics and the process with one of them.<br>
Create and open a file called `shrink_board.py`, then copy and paste the following:
<pre>
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

</pre>

This script will prompt the user for a clearance value, then
write a `.scr` file to move the board dimensions so that they are that amount
of distance away from the nearest component.<br>

Let's look closer at the `shrink_board` function.<br>
As mentioned earlier, the ulp file that invokes this script will pass the
`.brd` file path to the Board object for us, so we can instantiate it
with an empty constructor like `brd = autoeagle.core.Board()`.<br>

The next section
<pre>
get_coordinates = lambda n: list(float(part.get(n)) for part in brd.parts)
xs = get_coordinates("x")
ys = get_coordinates("y")
</pre>

iterates over the part elements and stores all the 'x' coordinates in 
one list and all the 'y' coordinates in another.

These lists are used, with the clearance value supplied by the user,
to determine the new board perimeter in the following lines:
<pre>
left = min(xs) - clearance
right = max(xs) + clearance
bottom = min(ys) - clearance
top = max(ys) + clearance
</pre>

Then we can obtain the current board perimeter with
<pre>
x0, xf, y0, yf = brd.get_bounds().values()
</pre>

`brd.get_bounds()` returns a dictionary so we can just use `.values()` to unpack values.

The final block of the function creates a ScriptWriter object.<br>
The ScriptWriter class is used to create a `.scr` file that can be run by Eagle.<br>
When generating the ulp file for our script, if it sees 'ScriptWriter' in the Python file,
it will tell Eagle to run the `.scr` file upon returning from the executing the ulp.<br>
Here's the ScriptWriter block:
<pre>
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
</pre>

The script this will write will first change the visible layers to only
show the 'Dimension' layer.<br>
It will then execute a series of four `move` commands.<br>
Each one will move a corner of the board from its current location to its new location,
as determined by the components and the user supplied clearance value.<br>
Finally, it will then reset the visible layers to whatever they were when the script was invoked.<br>
The `.scr` doesn't get generated until we invoke the ulp, but once we do, the generated script
will look something like the following:

<pre>
display none Dimension;
move (0.0 80.0) (-0.2999999999999998 25.7);
move (100.0 80.0) (19.9 25.7);
move (100.0 0.0) (19.9 0.04999999999999982);
move (0.0 0.0) (-0.2999999999999998 0.04999999999999982);
display none Top Bottom Pads Vias Dimension tPlace;
write;
</pre>

We didn't need to manually add the `write;` statement at the end,
because using the ScriptWriter class with a context manager will do that for us automatically.

Now that we've finished our script, it's time to generate the ulp.<br>
From the command line, navigate to the folder where you put the Python script we just wrote.<br>
Run the command `>generate_ulp shrink_board.py`.<br>
Now you should be able run the script in Eagle by entering `run shrink_board` in the editor's command line.<br>

To sum up, `run shrink_board` invokes the ulp file named `shrink_board.ulp` that was generated by the `generate_ulp` tool.<br>
That ulp then launches our Python script and passes the currently open file name to it.<br>
`shrink_board.py` parses the board file, prompts us for a minimum clearance, and generates a `.scr` file with the Eagle editor commands to 
appropriately shrink our board outline.<br>
Finally, upon exiting the ulp, it returns a command to Eagle to execute our new `.scr` file.
<br>

For further reference on editor commands that can be used in an `.scr` file, see the Eagle help documentation.