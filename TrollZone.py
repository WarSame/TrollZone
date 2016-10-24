import pygame
import random


class Level:
    def __init__(self):
        self.grid = [
            [Human(0, 0), 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 1, 0, 1, 1],
            [1, 1, 0, 1, 1],
            [0, 1, 0, 1, 1],
            [0, 1, 0, 1, 1],
            [0, 1, Creature(2, 6), 1, 1],
            [0, 1, 0, 1, 0],
            [1, 1, 1, 0, Door(4, 8)]
        ]
        self.player = self.grid[0][0]
        self.grid_width = len(self.grid[0])
        self.grid_height = len(self.grid)
        self.done = False
        self.player_dead = False

    def add_creature(self, creature, x, y):
        # Add creature to level list
        self.grid[y][x] = creature(x, y)

    def is_block(self, x, y):
        # Get whether location has a block
        return self.grid[y][x] == 1

    def is_on_screen(self, x, y):
        # Get whether location is on screen
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return False
        return True

    def is_valid_destination(self, x, y):
        # Get whether a creature can move into this space
        return self.is_on_screen(x, y) and not self.is_block(x, y)

    def kill_creature(self, creature):
        # Remove creature from level list. Notify if player died
        self.grid[creature.y][creature.x] = 0
        if isinstance(creature, Human):
            self.player_dead = True

    def move_creature(self, creature):
        # Move NPCs in creature list for level
        self.prowl(creature)

    def prowl(self, creature):
        # Move in random directions
        {
            0: self.move_down,
            1: self.move_left,
            2: self.move_right,
            3: self.move_up
        }[random.randint(0, 3)](creature)

    def move_left(self, creature):
        max_move = self.get_max_distance(creature, -1, 0)
        creature.x -= max_move

    def move_right(self, creature):
        max_move = self.get_max_distance(creature, 1, 0)
        creature.x += max_move

    def move_down(self, creature):
        max_move = self.get_max_distance(creature, 0, 1)
        creature.y += max_move

    def move_up(self, creature):
        max_move = self.get_max_distance(creature, 0, -1)
        creature.y -= max_move

    def get_max_distance(self, creature, direction_x, direction_y):
        # Maximum distance available to move in a certain direction
        move_dist = 0
        for i in range(creature.speed):
            if not self.is_valid_destination(creature.x + (i + 1) * direction_x, creature.y + (i + 1) * direction_y):
                return move_dist
            else:
                move_dist += 1
        return move_dist


class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 500))
        self.game_over = False
        self.level = Level()
        self.cell_width = self.screen.get_width() / self.level.grid_width
        self.cell_height = self.screen.get_height() / self.level.grid_height
        cell_size = int(self.cell_width), int(self.cell_height)
        self.font = pygame.font.Font(None, min(cell_size))

    def handle_events(self):
        # Handle event queue
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.level.player.flip_color()
                if event.key == pygame.K_LEFT:
                    self.level.move_left(self.level.player)
                if event.key == pygame.K_RIGHT:
                    self.level.move_right(self.level.player)
                if event.key == pygame.K_DOWN:
                    self.level.move_down(self.level.player)
                if event.key == pygame.K_UP:
                    self.level.move_up(self.level.player)
            if event.type == pygame.QUIT:
                self.game_over = True

    def draw_creature(self, creature):
        # Draw specific creature at specific location
        pixel_location = self.get_adjusted_pixel_location(creature)
        self.screen.blit(self.get_character(creature), pixel_location)

    def get_character(self, creature):
        # Return surface for text character
        return self.font.render(creature.character, False, creature.color)

    def get_pixel_location(self, x, y):
        # Get location in pixels of block given x, y co-ords
        return self.cell_width * x, self.cell_height * y

    def get_adjusted_pixel_location(self, creature):
        # Get location in pixels of character, adjusted for text size
        text_width, text_height = self.font.size(creature.character)
        pixel_location = self.get_pixel_location(creature.x, creature.y)
        pixel_x = pixel_location[0] + self.cell_width / 2 - text_width / 2
        pixel_y = pixel_location[1] + self.cell_height / 2 - text_height / 2
        return pixel_x, pixel_y

    def draw_blocks(self):
        # Draw all blocks
        padding = 1
        for y, row in enumerate(self.level.grid):
            for x, column in enumerate(row):
                if isinstance(self.level.grid[y][x], Creature):
                    self.draw_creature(self.level.grid[y][x])
                if self.level.is_block(x, y):
                    rect = pygame.Rect(self.get_pixel_location(x, y),
                                       (self.cell_width - padding, self.cell_height - padding))
                    pygame.draw.rect(self.screen, (255, 255, 255), rect)

    def move_creatures(self):
        # Move all AI creatures
        for y, row in enumerate(self.level.grid):
            for x, column in enumerate(row):
                creature = self.level.grid[y][x]
                if isinstance(creature, Creature) and not isinstance(creature, Human):
                    self.level.move_creature(creature)

    def draw_screen(self):
        # Update game visuals
        self.screen.fill((0, 0, 0))
        self.draw_blocks()
        pygame.display.flip()
        self.clock.tick(5)

    def end_game(self):
        # Colour screen and pause movement
        if self.level.player_dead:
            self.screen.fill((166, 16, 30))
            pygame.display.flip()
            pygame.time.wait(2500)

    def run_game(self):
        # Heartbeat
        while not (self.game_over or self.level.player_dead):
            self.handle_events()
            self.move_creatures()
            self.draw_screen()
        self.end_game()


class Creature:
    def __init__(self, x, y, color=(34, 139, 34)):
        self.x = x
        self.y = y
        self.color = color
        self.size = 1
        self.character = "T"
        self.speed = 1


class Human(Creature):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 128, 255))
        self.is_blue = True
        self.character = "P"

    def flip_color(self):
        self.is_blue = not self.is_blue
        if self.is_blue:
            self.color = (0, 128, 255)
        else:
            self.color = (255, 255, 255)


class Door(Creature):
    def __init__(self, x, y):
        super().__init__(x, y, (150, 75, 0))
        self.speed = 0
        self.character = "D"


curr_game = Game()
curr_game.run_game()
