import pygame
import random


class Level:
    def __init__(self):
        self.grid = [
        [0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 1],
        [1, 1, 0, 1, 1],
        [0, 1, 0, 1, 1],
        [0, 1, 0, 1, 1],
        [0, 1, 0, 1, 1],
        [0, 1, 0, 1, 0],
        [1, 1, 1, 0, 0]
        ]
        self.grid_width = len(self.grid[0])
        self.grid_height = len(self.grid)
        self.creatures = []
        self.player = Human(2, 0)
        self.add_creature(self.player)
        #self.add_creature(Creature(1, 5))
        self.done = False
        self.player_dead = False

    def add_creature(self, creature):
        # Add creature to level list
        self.creatures.append(creature)

    def is_block(self, x, y):
        # Get whether location has a block
        return self.grid[y][x]

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
        if creature in self.creatures:
            if creature == self.player:
                self.player_dead = True
            self.creatures.remove(creature)

    def move_creatures(self):
        # Move NPCs in creature list for level
        for creature in self.creatures:
            if not creature == self.player:
                self.prowl(creature)

    # Move in random directions
    def prowl(self, creature):
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
            if not self.is_valid_destination(creature.x + (i+1) * direction_x, creature.y + (i+1) * direction_y):
                return move_dist
            else:
                move_dist += 1
        return move_dist


class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 500))
        self.done = False
        self.level = Level()
        self.cell_width = float(self.screen.get_width()) / self.level.grid_width
        self.cell_height = float(self.screen.get_height()) / self.level.grid_height

    def handle_presses(self):
        # Handle user input
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            self.level.move_up(self.level.player)

        if pressed[pygame.K_DOWN]:
            self.level.move_down(self.level.player)

        if pressed[pygame.K_LEFT]:
            self.level.move_left(self.level.player)

        if pressed[pygame.K_RIGHT]:
            self.level.move_right(self.level.player)

    def handle_events(self):
        # Handle event queue
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.level.player.flip_color()
                    self.level.kill_creature(self.level.player)
                if event.key == pygame.K_LEFT:
                    self.level.move_left(self.level.player)
                if event.key == pygame.K_RIGHT:
                    self.level.move_right(self.level.player)
                if event.key == pygame.K_DOWN:
                    self.level.move_down(self.level.player)
                if event.key == pygame.K_UP:
                    self.level.move_up(self.level.player)
            if event.type == pygame.QUIT:
                self.done = True

    def draw_creatures(self):
        # Draw all creatures
        for creature in self.level.creatures:
            pixel_location = self.get_pixel_location(creature.x, creature.y)
            pixel_location = (pixel_location[0] + 20, pixel_location[1] + 20)
            cell_size = int(self.cell_width), int(self.cell_height)
            self.screen.blit(creature.get_character(cell_size), pixel_location)

    def get_pixel_location(self, x, y):
        # Get location in pixels of block given x, y co-ords
        return self.cell_width * x, self.cell_height * y

    def draw_blocks(self):
        # Draw all blocks
        for y, row in enumerate(self.level.grid):
            for x, column in enumerate(row):
                if self.level.is_block(x, y):
                    rect = pygame.Rect(self.get_pixel_location(x, y), (self.cell_width, self.cell_height))
                    pygame.draw.rect(self.screen, (255, 255, 255), rect)

    def draw_screen(self):
        # Update game visuals
        self.screen.fill((0, 0, 0))
        self.draw_blocks()
        self.draw_creatures()
        pygame.display.flip()
        self.clock.tick(5)

    def end_game(self):
        # Colour screen and pause movement
        if self.level.player not in self.level.creatures:
            self.screen.fill((166, 16, 30))
            pygame.display.flip()
            pygame.time.wait(2500)

    def run_game(self):
        # Heartbeat
        while not (self.done or self.level.player_dead):
            #self.handle_presses()
            self.handle_events()
            self.level.move_creatures()
            self.draw_screen()
        self.end_game()


class Creature:
    def __init__(self, x, y, color=(34, 139, 34)):
        self.x = x
        self.y = y
        self.color = color
        self.size = 1
        self.speed = 1

    def get_character(self, cell_size, character="T"):
        return pygame.font.Font(None, min(cell_size)).render(character, False, self.color)


class Human(Creature):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 128, 255))
        self.is_blue = True

    def get_character(self, cell_size, character="P"):
        return super().get_character(cell_size, character)

    def flip_color(self):
        self.is_blue = not self.is_blue
        if self.is_blue:
            self.color = (0, 128, 255)
        else:
            self.color = (255, 255, 255)


curr_game = Game()
curr_game.run_game()
