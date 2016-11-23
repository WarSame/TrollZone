import pygame
import random


class Level:
    def __init__(self):
        self.grid = [
            [0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 1, 0, 1, 1],
            [1, 1, 0, 1, 1],
            [0, 1, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [1, 1, 1, 0, 0]
        ]
        self.grid_width = len(self.grid[0])
        self.grid_height = len(self.grid)
        self.done = False
        self.add_creature(Creature(2, 6))
        self.add_creature(Door(4, 8))
        self.player = Human(0, 0)
        self.add_creature(self.player)

    def add_creature(self, creature):
        # Add creature to level list
        self.grid[creature.y][creature.x] = creature

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
            self.player.is_dead = True

    def move_creature(self, creature):
        # Move NPCs in creature list for level
        self.prowl(creature)

    def prowl(self, creature):
        # Move in random directions
        direction = random.randint(0, 3)
        if direction == 0:
            self.move(creature, -1, 0)
        if direction == 1:
            self.move(creature, 1, 0)
        if direction == 2:
            self.move(creature, 0, -1)
        if direction == 3:
            self.move(creature, 0, 1)

    def move(self, creature, direction_x, direction_y):
        max_move = self.get_max_distance(creature, direction_x, direction_y)
        creature.x += direction_x * max_move
        creature.y += direction_y * max_move

    def get_max_distance(self, creature, direction_x, direction_y):
        # Maximum distance available to move in a certain direction
        move_dist = 0
        for i in range(1, creature.speed + 1):
            next_x = creature.x + i * direction_x
            next_y = creature.y + i * direction_y
            if self.is_valid_destination(next_x, next_y):
                move_dist += 1
            else:
                return move_dist
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
        # Grab first event and then clear queue
        event = pygame.event.poll()
        pygame.event.clear()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.level.move(self.level.player, -1, 0)
            if event.key == pygame.K_RIGHT:
                self.level.move(self.level.player, 1, 0)
            if event.key == pygame.K_UP:
                self.level.move(self.level.player, 0, -1)
            if event.key == pygame.K_DOWN:
                self.level.move(self.level.player, 0, 1)
        if event.type == pygame.QUIT:
            self.game_over = True

    def draw_map_object(self, map_object):
        # Draw specific creature at specific location
        pixel_location = self.get_adjusted_pixel_location(map_object)
        self.screen.blit(self.get_character(map_object), pixel_location)

    def get_character(self, map_object):
        # Return surface for text character
        return self.font.render(map_object.character, False, map_object.color)

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
                if isinstance(self.level.grid[y][x], MapObject):
                    self.draw_map_object(self.level.grid[y][x])
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
        self.clock.tick(60)

    def end_game(self):
        # Colour screen and pause movement
        if self.level.player.is_dead:
            self.screen.fill((166, 16, 30))
            pygame.display.flip()
            pygame.time.wait(2500)

    def run_game(self):
        # Heartbeat
        while not (self.game_over or self.level.player.is_dead):
            self.handle_events()
            self.move_creatures()
            self.draw_screen()
            pygame.time.wait(100)
        self.end_game()


class MapObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (255, 255, 255)
        self.size = 1
        self.character = "T"
        self.speed = 1


class Creature(MapObject):
    def __init__(self, x, y, color=(34, 139, 34)):
        super().__init__(x, y)
        self.color = color


class Human(Creature):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 128, 255))
        self.character = "P"
        self.is_dead = False


class Door(MapObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y
        self.color = (150, 75, 0)
        self.size = 1
        self.speed = 0
        self.character = "D"


curr_game = Game()
curr_game.run_game()
