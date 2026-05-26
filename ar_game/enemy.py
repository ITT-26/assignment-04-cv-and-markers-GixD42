import os
import pyglet
import random

BASE_DIR = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(BASE_DIR, "img", "enemy_big.png")


class Enemy:
    def __init__(self, x, y, speed=50):
        self.x = x
        self.y = y
        self.speed = speed

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
    def __init__(self, spawn_y, spawn_interval=2.0, min_spawn_interval=1.0, max_spawn_interval=3.0):

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
        min_x = 32
        max_x = 640 - 32
        x = random.randint(min_x, max_x)

        # enemy spawn
        enemy = Enemy(x=x, y=self.spawn_y, speed=50)
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
