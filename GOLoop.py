import pygame, random
from pygame.locals import *


class App:
    def __init__(self):
        self._display_surf = None
        self.size = self.width, self.height = 1000, 700
        self._grid = Grid(self.width, self.height)
        self._running = True
        self._game_start = False
        self._colour = False
        self._paused = False
        self._stochastic = False
        self.clock = pygame.time.Clock()
        self._fps = 5


    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        return self._display_surf

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False
                elif event.key == pygame.K_SPACE:
                    if not self._game_start:
                        self._game_start = not self._game_start
                    else:
                        self._display_surf.blit(self._grid.draw_grid(), (0, 0))
                        pygame.display.update()
                        self._grid.cells = self._grid.populate()
                        self.clock.tick(self._fps)
                elif event.key == pygame.K_c:
                    self._colour= not self._colour
                elif event.key == pygame.K_p:
                    self._paused = not self._paused
                elif event.key == pygame.K_r:
                    self._stochastic = not self._stochastic


    def on_loop(self):
        if not self._paused:
            if self._game_start:
                self._display_surf.blit(self._grid.draw_cells(), (0, 0))
            else:
                self._display_surf.blit(self._grid.draw_grid(), (0, 0))
            pygame.display.update()

    def on_render(self):
        if not self._paused:
            if self._game_start:
                self._grid.update()
                # self._grid.random(int(self._grid.total / 200))
                if self._stochastic:
                    self._grid.stochastic(2)
                if self._colour:
                    self._grid.change_colour()

        self.clock.tick(self._fps)

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() is None:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


class Grid:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.grain = 6
        self.x_cells = int(self.width / self.grain)
        self.y_cells = int(self.height / self.grain)
        self.colours = self.colour_cell, self.colour_grid = (0, 255, 65), (0, 143, 17)
        self.total = self.x_cells * self.y_cells
        self.cells = self.populate()

    def change_colour(self):
        self.colour_cell = (self.colour_cell[2], self.colour_cell[0], self.colour_cell[1])
        self.colour_grid = (self.colour_grid[2], self.colour_grid[0], self.colour_grid[1])


    def draw_cells(self):
        grid = self.draw_grid()
        for cell in self.cells:
            if cell.alive:
                rect = pygame.Rect(cell.x * self.grain, cell.y * self.grain, self.grain, self.grain)
                pygame.draw.rect(grid, self.colour_cell, rect)
        return grid

    def draw_grid(self):
        grid = pygame.Surface((self.width, self.height))
        grid.fill((0, 0, 0))
        for y in range(self.y_cells):
            for x in range(self.x_cells):
                rect = pygame.Rect(x * self.grain, y * self.grain, self.grain, self.grain)
                pygame.draw.rect(grid, self.colour_grid, rect, 1)
        return grid

    def populate(self):
        cell_array = []
        num_array = []
        for y in range(self.y_cells):
            for x in range(self.x_cells):
                cell_array.append(Cell(x, y, self.x_cells, self.y_cells))
                num_array.append(random.randint(1, 1000))

        """
        for i in range(int(self.total * 0.3)):
            max_val = max(num_array)
            max_idx = num_array.index(max_val)
            cell_array[max_idx].alive = True
            num_array[max_idx] = 0
        """
        # """
        num = 10
        for cell in cell_array:
            if (cell.x % num) < (num * 0.5):
                cell.alive = True
        for cell in cell_array:
            if (cell.y % num) < (num * 0.5):
                cell.alive = not cell.alive
        # """

        return cell_array

    def stochastic(self, n):
        for i in range(n):
            rando = random.randint(0, self.total - 1)
            if not self.cells[rando].alive:
                self.cells[rando].alive = True

    def update(self):
        [cell.implement_rules(self) for cell in self.cells]
        [cell.check_status() for cell in self.cells]


class Cell:
    def __init__(self, x, y, x_cells, y_cells):
        self.x = x
        self.y = y
        self.alive = False
        self.change = False
        self.neighbours = self.get_neighbours(x_cells, y_cells)

    def check_status(self):
        if self.change:
            if self.alive:
                self.alive = False
                self.change = False
            elif not self.alive:
                self.alive = True
                self.change = False

    def get_neighbours(self, width, height):
        if self.x == 0 and self.y == 0:
            return [[1, self.y], [self.x, 1], [1, 1]]
        elif self.x == width - 1 and self.y == 0:
            return [[width - 2, self.y], [width - 2, 1], [self.x, 1]]
        elif self.x == 0 and self.y == height - 1:
            return [[self.x, height - 2], [1, height - 2], [1, self.y]]
        elif self.x == width - 1 and self.y == height - 1:
            return [[width - 2, height - 2], [self.x, height - 2], [width - 2, self.y]]
        elif self.y == 0:
            return [
                [self.x - 1, self.y], [self.x + 1, self.y],
                [self.x - 1, self.y + 1], [self.x, self.y + 1], [self.x + 1, self.y + 1]
            ]
        elif self.y == height - 1:
            return [
                [self.x - 1, self.y - 1], [self.x, self.y - 1], [self.x + 1, self.y - 1],
                [self.x - 1, self.y], [self.x + 1, self.y]
            ]
        elif self.x == 0:
            return [
                [self.x, self.y - 1], [self.x, self.y + 1],
                [self.x + 1, self.y - 1], [self.x + 1, self.y], [self.x + 1, self.y + 1]
            ]
        elif self.x == width - 1:
            return [
                [self.x - 1, self.y - 1], [self.x - 1, self.y], [self.x - 1, self.y + 1],
                [self.x, self.y - 1], [self.x, self.y + 1],
            ]
        else:
            return [
                [self.x - 1, self.y - 1],   [self.x, self.y - 1],   [self.x + 1, self.y - 1],
                [self.x - 1, self.y],       [self.x + 1, self.y],
                [self.x - 1, self.y + 1],   [self.x, self.y + 1],   [self.x + 1, self.y + 1]
            ]

    def implement_rules(self, grid):
            live_cells = 0

            for cell in self.neighbours:
                if grid.cells[(cell[0] + (cell[1] * grid.x_cells))].alive:
                    live_cells += 1

            if live_cells < 2 and self.alive:
                self.change = True
            elif live_cells > 3 and self.alive:
                self.change = True
            elif live_cells == 3 and not self.alive:
                self.change = True




if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
