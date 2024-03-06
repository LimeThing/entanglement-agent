# Project-R-Entanglement-AI
An attempt to teach an AI to play the game [Entanglement - by Gopherwood Studios](https://entanglement.gopherwoodstudios.com/)\
Pre-made entanglement pygame repository cloned from [orez-/entanglement](https://github.com/orez-/entanglement)\
Made with the help of [this freeCodeCamp.org video](https://www.youtube.com/watch?v=L8ypSXwyBds)\
Created as a final project at the FER university under the mentorship of professor Marko Đurasević\

The original repository is positioned in the entanglement-master forlder
And my project and edits are in the Entanglement-AI folder

# Running the project
Install all the needed packages (pygame and torch)\
Open the terminal inside the Entanglement-AI folder\
Run agent.py with python3

# Currently completed functionalities
After running the file, the agent places the tiles on the board with simple heuristics.
Once the game is complete, the agent pauses the game. It needs manual unpausing to continue.
You can quit with Q and pause/unpause with P

# TODO functionalities
Implementing simple heuristics, the agent will not pick the tiles' rotation randomly, but rather base it on the given game state/parametars, such as how can he score the most points, or most simply, how can he avoid hitting a wall. ✓ \
Implement the swapping of the tile in case that every tile rotation of the active tile leads to hitting a wall. ✓ \
Start working on neural networks and optimisation techniques

