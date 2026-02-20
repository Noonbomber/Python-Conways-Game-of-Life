#Authors: Landon Schultz and Andrew Alsip
#Date: February 17th, 2026

import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import RadioButtons
from matplotlib.colors import ListedColormap

EMOTIONAL_CMAP = ListedColormap([
    "black",   # 0 dead
    "yellow",  # 1 neutral
    "green",   # 2 happy
    "red"      # 3 angry
])

class CellularAutomaton:
    def __init__(self, rows, cols, rule_file="rules.json", presets_file="presets.json"):
        self.mode = "conway"
        self.rows = rows
        self.cols = cols
        self.grid = np.random.choice([0, 1], size=(rows, cols), p=[0.75, 0.25])
        
        # Default rules will be set later in main
        self.survive = [2, 3]
        self.birth = [3]
        
        self.paused = True
        self.presets = self.load_presets(presets_file)
        
        self.fig, self.ax = plt.subplots()
        self.image = self.ax.imshow(
            self.grid,
            cmap="binary",
            interpolation="nearest",
            vmin=0,
            vmax=3
        )
        self.ax.set_title("Cellular Automaton  (Pause: press 'p' | Quit: press 'q' | Toggle Mode: press 'm')")
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.setup_preset_selector()
        
        self.anim = animation.FuncAnimation(
            self.fig,
            self.animate,
            interval=200,
            cache_frame_data=False
        )

    def load_presets(self, presets_file):
        try:
            with open(presets_file, "r") as f:
                data = json.load(f)
            if "Random" not in data:
                data = {"Random": None, **data}
            return data
        except FileNotFoundError:
            return {"Random": None}

    def setup_preset_selector(self):
        names = list(self.presets.keys())
        selector_ax = self.fig.add_axes([0.02, 0.25, 0.18, 0.5])
        self.radio = RadioButtons(selector_ax, names, active=0)
        self.radio.on_clicked(self.on_preset_change)
        self.on_preset_change(names[0])

    def on_preset_change(self, label):
        self.paused = True
        preset_data = self.presets.get(label)
        if preset_data is None:
            self.grid = np.random.choice([0, 1], size=(self.rows, self.cols))
            return
        preset_grid = np.array(preset_data, dtype=int)
        preset_grid = (preset_grid != 0).astype(int)
        new_grid = np.zeros((self.rows, self.cols), dtype=int)
        pr, pc = preset_grid.shape
        r0 = max((self.rows - pr) // 2, 0)
        c0 = max((self.cols - pc) // 2, 0)
        r1 = min(r0 + pr, self.rows)
        c1 = min(c0 + pc, self.cols)
        pr_use = r1 - r0
        pc_use = c1 - c0
        new_grid[r0:r1, c0:c1] = preset_grid[:pr_use, :pc_use]
        self.grid = new_grid

    def count_neighbors(self, row, col):
        total = 0
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                if i==0 and j==0:
                    continue
                r, c = row+i, col+j
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    total += self.grid[r,c]
        return total

    def count_neighbors_emotional(self, row, col):
        total_alive = 0
        happy_only = 0
        angry_only = 0
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                if i==0 and j==0:
                    continue
                r, c = row+i, col+j
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    val = self.grid[r,c]
                    if val > 0: total_alive += 1
                    if val == 2: happy_only += 1
                    if val == 3: angry_only += 1
        return total_alive, happy_only, angry_only

    def update_conway(self):
        new_grid = np.copy(self.grid)
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = self.count_neighbors(r,c)
                if self.grid[r,c]==1:
                    if neighbors not in self.survive:
                        new_grid[r,c] = 0
                else:
                    if neighbors in self.birth:
                        new_grid[r,c] = 1
        self.grid = new_grid

    def update(self):
        if self.mode=="conway":
            self.update_conway()
        else:
            self.update_emotional()

    def update_emotional(self):
        new_grid = np.copy(self.grid)
        for r in range(self.rows):
            for c in range(self.cols):
                total, happy, angry = self.count_neighbors_emotional(r,c)
                state = self.grid[r,c]

                # Angry kills neighbors
                if state == 3:
                    for i in [-1,0,1]:
                        for j in [-1,0,1]:
                            if i==0 and j==0: continue
                            nr, nc = r+i, c+j
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                new_grid[nr,nc] = 0
                # Alive cells update
                if state > 0:
                    if total <= 1 or total >= 5:
                        new_grid[r,c] = 0
                    elif total == 2:
                        new_grid[r,c] = 2  # happy
                    elif total == 3:
                        new_grid[r,c] = 1  # neutral
                    elif total == 4:
                        new_grid[r,c] = 3  # angry
                else:
                    # Empty cells
                    if happy == 2:
                        new_grid[r,c] = 1  # neutral 
                    if happy == 1 and total == 2:
                        new_grid[r,c] = 1 # neutral
                    if angry == 1:
                        for i in [-1,0,1]:
                            for j in [-1,0,1]:
                                if i==0 and j==0: continue
                                nr, nc = r+i, c+j
                                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                    new_grid[nr,nc] = 0
        self.grid = new_grid

    def animate(self, frame):
        if not self.paused:
            self.update()
        self.draw()

    def draw(self):
        self.image.set_data(self.grid)
        plt.draw()

    def on_key_press(self, event):
        if event.key == "p":
            self.paused = not self.paused
        elif event.key in ["q","escape"]:
            self.anim.event_source.stop()
            plt.close(self.fig)
        elif event.key == "m":
            if self.mode=="conway":
                self.mode="emotional"
                self.image.set_cmap(EMOTIONAL_CMAP)
                self.image.set_clim(0,3)
                print("Mode: Emotional")
            else:
                self.mode="conway"
                self.image.set_cmap("binary")
                self.image.set_clim(0,1)
                print("Mode: Conway")


def parse_rule_input(user_input, default):
    if not user_input or user_input.lower() == "default":
        return default
    try:
        result = [int(x) for x in user_input.split(",")]
    except ValueError:
        print("Invalid input detected. Using default rules:", default)
        return default
    return result if result else default


if __name__=="__main__":
    try:
        r_in = input("How many rows? ").strip()
        c_in = input("How many columns? ").strip()
        rows = int(r_in) if r_in else 50
        cols = int(c_in) if c_in else 50
    except ValueError:
        rows, cols = 50,50

    # Load defaults from JSON
    try:
        with open("rules.json") as f:
            rules = json.load(f)
            default_survive = rules.get("survive", [2,3])
            default_birth = rules.get("birth", [3])
    except FileNotFoundError:
        default_survive = [2,3]
        default_birth = [3]

    survive_input = input(f"Enter survive counts separated by commas (default {default_survive}): ").strip()
    birth_input = input(f"Enter birth counts separated by commas (default {default_birth}): ").strip()

    survive = parse_rule_input(survive_input, default_survive)
    birth = parse_rule_input(birth_input, default_birth)

    automaton = CellularAutomaton(rows, cols)
    automaton.survive = survive
    automaton.birth = birth

    plt.show()