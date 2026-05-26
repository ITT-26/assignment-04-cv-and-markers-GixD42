import os
import pyglet
import random
from constants import *

BASE_DIR = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(BASE_DIR, "img", "enemy_big.png")


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = ENEMY_SPEED

        # load image and set anchor to center
        image = pyglet.image.load(IMAGE_PATH)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2

        self.sprite = pyglet.sprite.Sprite(image, x=self.x, y=self.y)

    def update(self, dt):
        # move downwards
        self.y -= self.speed * dt
        self.sprite.y = self.y

    def draw(self):
        self.sprite.draw()


class EnemySpawner:
    def __init__(self, spawn_y=ENEMY_SPAWN_Y, spawn_interval=ENEMY_SPAWN_INTERVAL, min_spawn_interval=ENEMY_MIN_SPAWN_INTERVAL, max_spawn_interval=ENEMY_MAX_SPAWN_INTERVAL):

        # y position
        self.spawn_y = spawn_y

        # spawn interval with max and min for randomization
        self.spawn_interval = spawn_interval
        self.min_spawn_interval = min_spawn_interval
        self.max_spawn_interval = max_spawn_interval

        # randomize first spawn interval
        self.next_spawn_interval = random.uniform(
            self.min_spawn_interval, self.max_spawn_interval)

        # timer for spawning
        self.spawn_timer = 0.0

        # list of all enemies
        self.enemies = []

    def spawn_enemy(self):
        # spawn enemy at random x position
        min_x = ENEMY_SIZE // 2
        max_x = WINDOW_WIDTH - ENEMY_SIZE // 2
        x = random.randint(min_x, max_x)

        # enemy spawn
        enemy = Enemy(x=x, y=self.spawn_y)
        self.enemies.append(enemy)

    def update(self, dt):
        # spawn based on timer
        self.spawn_timer += dt

        while self.spawn_timer >= self.next_spawn_interval:
            self.spawn_timer -= self.next_spawn_interval
            self.spawn_enemy()
            # randomize next spawn interval
            self.next_spawn_interval = random.uniform(
                self.min_spawn_interval, self.max_spawn_interval)

        # enemy gets moved
        for enemy in self.enemies:
            enemy.update(dt)

    def draw(self):
        # draw all enemies
        for enemy in self.enemies:
            enemy.draw()
