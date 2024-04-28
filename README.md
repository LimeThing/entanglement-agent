# Development of an agent for solving the Entaglement game
Development of an agent for solving the game [Entanglement - by Gopherwood Studios](https://entanglement.gopherwoodstudios.com/)\
Pre-made entanglement pygame repository cloned from [orez-/entanglement](https://github.com/orez-/entanglement)\
Made with the help of [this freeCodeCamp.org video](https://www.youtube.com/watch?v=L8ypSXwyBds)\
Created as a final project at the FER university under the mentorship of professor Marko Đurasević\

# Running the project
Install all the needed packages (pygame and torch)\
Open the terminal and run the selected file with python3.\
File names and what they implement:\
- random_heuristics.py - places tiles randomly
- sofort_heuristics.py - avoids immidiate danger (closed and start pieces)
- reach_heuristics.py - avoids all danger
- depth_heuristics.py - chooses the longest possible path when placing tile

# Currently completed functionalities
After running the file, the agent places the tiles on the board with simple heuristics.
Once the game is complete, the agent pauses the game. It needs manual unpausing to continue.
You can quit with Q and pause/unpause with P

# TODO functionalities
Implementing simple heuristics, the agent will not pick the tiles' rotation randomly, but rather base it on the given game state/parametars, such as how can he score the most points, or most simply, how can he avoid hitting a wall. ✓ \
Implement the swapping of the tile in case that every tile rotation of the active tile leads to hitting a wall. ✓ \
Start working on neural networks and optimisation techniques

