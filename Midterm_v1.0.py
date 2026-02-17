import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class CellularAutomaton:

    def __init__(self, rows, cols, rule_file="rules.json"):
        self.rows = rows
        self.cols = cols
        self.grid = np.random.choice([0, 1], size=(rows, cols))

        with open(rule_file) as f:
            rules = json.load(f)

        self.survive = rules["survive"]
        self.birth = rules["birth"]

        self.paused = False

        # Create plot
        self.fig, self.ax = plt.subplots()
        self.image = self.ax.imshow(self.grid, cmap="binary")

        self.anim = animation.FuncAnimation(
            self.fig,
            self.animate,
            interval=200
        )

    def count_neighbors(self, row, col):
        total = 0

        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue

                r = row + i
                c = col + j

                if 0 <= r < self.rows and 0 <= c < self.cols:
                    total += self.grid[r, c]

        return total

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

    def animate(self, frame):
        if not self.paused:
            self.update()
            self.draw()

    def draw(self):
        self.image.set_data(self.grid)
        plt.draw()

if __name__ == "__main__":
    automaton = CellularAutomaton(50, 50)
    plt.show()

