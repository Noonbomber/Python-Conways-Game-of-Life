#Authors: Landon Schultz and Andrew Alsip
#Date: February 17th, 2026

import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import RadioButtons

class CellularAutomaton:
    #Initialization of the board setting the rules and connecting files
    def __init__(self, rows, cols, rule_file="rules.json", presets_file="presets.json"):
        #Stores our dimension of the board
        self.rows = rows
        self.cols = cols
        #Default random starting grid, will be replaced if a preset is chosen
        self.grid = np.random.choice([0, 1], size=(rows, cols))
        # loads the rules from the rules file
        with open(rule_file) as f:
            rules = json.load(f)
        self.survive = rules["survive"]
        self.birth = rules["birth"]
        #starts the code in a paused state
        self.paused = True
        #load the presets from the presets file
        self.presets = self.load_presets(presets_file)
        #setup of the board and buttons 
        self.fig, self.ax = plt.subplots()
        self.image = self.ax.imshow(self.grid, cmap="binary")
        self.ax.set_title("Cellular Automaton  (Pause: press 'p' | Quit: press 'q')")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        #allows key presses
        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)
        #sets buttons to work in the window
        self.setup_preset_selector()
        # setting up the animation to change every 200 millisectons (this makes it 5 fps)
        self.anim = animation.FuncAnimation(
            self.fig,
            self.animate,
            interval=200
        )
    # This section helps load the presets from the presets file
    def load_presets(self, presets_file):
        try:
            with open(presets_file, "r") as f:
                data = json.load(f)
            #always have the option to do a random board
            if "Random" not in data:
                data = {"Random": None, **data}
            return data
        except FileNotFoundError:
            # if the preset file gets deleted, game still works with just a random option
            return {"Random": None}
    # creates a button for each preset
    def setup_preset_selector(self):
        names = list(self.presets.keys())
        # creates panel for buttons in the window
        selector_ax = self.fig.add_axes([0.02, 0.25, 0.18, 0.5]) 
        self.radio = RadioButtons(selector_ax, names, active=0)
        self.radio.on_clicked(self.on_preset_change)
        # makes sure random is the defualt selection for the board state
        self.on_preset_change(names[0])
    def on_preset_change(self, label):
       #IF the state gets changed, the code will pause
        self.paused = True  
        preset_data = self.presets.get(label)
        #if random then the board will just be randomized
        if preset_data is None:
            self.grid = np.random.choice([0, 1], size=(self.rows, self.cols))
            return
        # converts arrays in the preset file to binary info for board
        preset_grid = np.array(preset_data, dtype=int)
        preset_grid = (preset_grid != 0).astype(int)  # my code was being angry about it not being binary so this forces it
        #clears the board and slaps the preset in the middle
        new_grid = np.zeros((self.rows, self.cols), dtype=int)
        pr, pc = preset_grid.shape
        r0 = max((self.rows - pr) // 2, 0)
        c0 = max((self.cols - pc) // 2, 0)
        r1 = min(r0 + pr, self.rows)
        c1 = min(c0 + pc, self.cols)
        #if the preset is too big, then it will be cut off to keep from crashing, but the preset also probably wont work right
        pr_use = r1 - r0
        pc_use = c1 - c0
        new_grid[r0:r1, c0:c1] = preset_grid[:pr_use, :pc_use]
        self.grid = new_grid
   #Board logic for counting each piece's neighbors and updating based on the rules
    def count_neighbors(self, row, col):
        total = 0
        # Loops through the surrounding cells for a cell
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue
                r = row + i
                c = col + j
                # ignore cells that arent in bounds
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    total += self.grid[r, c]

        return total
    #Main logic for updating the board based off of the rules
    def update(self):
        new_grid = np.copy(self.grid)
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = self.count_neighbors(r, c)
                if self.grid[r, c] == 1:
                    if neighbors not in self.survive:
                        new_grid[r, c] = 0
                else:
                    if neighbors in self.birth:
                        new_grid[r, c] = 1
        self.grid = new_grid
    #The updating and redrawing of the board based off of the new state we just calculated
    def animate(self, frame):
        if not self.paused:
            self.update()
        self.draw()
    def draw(self):
        self.image.set_data(self.grid)
        plt.draw()

    #sets pause key to p
    def on_key_press(self, event):
        if event.key == "p":
            self.paused = not self.paused
        #sets quit key to q or escape
        elif event.key in ["q", "escape"]:
            #stops the animation loop
            self.anim.event_source.stop()
            #closes the window
            plt.close(self.fig)

if __name__ == "__main__":
    #This lets the user change the size of the board, if they don't put in a number, defaults to 50
    try:
        r_in = input("How many rows do ya want? ").strip()
        c_in = input("How about columns? ").strip()
        rows = int(r_in) if r_in else 50
        cols = int(c_in) if c_in else 50
    except ValueError:
        rows, cols = 50, 50

    #Creates the board and makes the magic happen
    automaton = CellularAutomaton(rows, cols)
    print("Pause: press 'p' | Quit: press 'q'")
    plt.show()