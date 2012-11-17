ENTANGLEMENT IS NOT MY IDEA

I'm reimplementing http://entanglement.gopherwoodstudios.com (poorly) so others may make AIs to find an optimal strategy.

This is only for fun: no profit is or will be associated with this project.

If the creators of Entanglement want this repo taken down I will take it down.

Usage: run main.py with any of the following commands:
* `--nogui`  to suppress the GUI (should allow you to avoid the pygame requirement)
* `--nocmd`  to suppress the commandline input: this allows you to play the game through the pygame window
* `-s <string>`  to seed the random generation of tiles

For playing through the gui:
* `left` and `right` rotate the piece
* `space` places the piece
* `tab` swaps with your reserve

For playing through the command line:

Commands are of the form `/(swap )?rotate -?[0-5]/`, that is to say:
* the swap command is optional, and will swap the current piece with your reserve
* the rotate command is required, and rotates the current piece clockwise by the set number of times. It will then place the piece.

Tiles are conveyed textually by displaying the exits that connect: 0-1 means exit 0 is connected to exit 1 and vice versa.
Exits are numbered from 0 to 11, starting on the leftmost exit on top edge on the hexagon and enumerating clockwise.
Tiles enumerate their connections delimited by commas.

On startup the swap tile is output first, separated from the current tile by a `|`. On proper input, either the next
current tile or the message `You lose. Final score: <integer>` is output, where <integer> is your score.
