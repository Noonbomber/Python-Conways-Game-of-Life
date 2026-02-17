import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class CellularAutomaton:

    def __init__: 
        self.grid = np.zeros((rows, cols), dtype=int)

        with open("rules.json") as f: #imports rules.json as f
        rules = json.load(f) #sets the rules to be used as those in rules.json
        self.survive = rules["survive"] #sets survival rules to those in rules.json
        self.birth = rules["birth"] #sets survival rules to those in rules.json

    def count_neighbors(self, row, col): #defines count_neighors; takes in rows and columns
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


    def update(self):
        new_grid = np.copy(self.grid)

        for r in range(self.rows): #for any row
            for c in range(self.cols): #for any column
                neighbors = self.count_neighbors(r, c) #neighbors is set to be == to r and c passed through count_neighbors 

                if self.grid[r, c] == 1: 
                    if neighbors not in self.survive:
                        new_grid[r, c] = 0
                else:
                    if neighbors in self.birth:
                        new_grid[r, c] = 1

    self.grid = new_grid

    self.fig, self.ax = plt.subplots()
    self.image = self.ax.imshow(self.grid, cmap="binary")

    self.anim = animation.FuncAnimation(
        self.fig,
        self.animate,
        interval=200  # 5 frames/sec
)
    def draw(self):
        self.image.set_data(self.grid)
        plt.draw()

