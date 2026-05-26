import pyglet

IMAGE_PATH = "ar_game/img/player_big.png"
BULLET_IMAGE_PATH = "ar_game/img/player_bullet.png"


class Bullet:
    def __init__(self, x, y, speed=100):
        self.x = x
        self.y = y
        self.speed = speed
        self.sprite = pyglet.sprite.Sprite(
            pyglet.image.load(BULLET_IMAGE_PATH), x=self.x, y=self.y)

    def update(self, dt):
        self.y += self.speed * dt
        self.sprite.y = self.y

    def draw(self):
        self.sprite.draw()


class Player:
    def __init__(self, x, y, fire_rate=0.5):

        # position
        self.x = x
        self.y = y

        # fire rate and timer for shooting
        self.fire_rate = fire_rate
        self.fire_timer = 0.0

        # all bullets saved
        self.bullets = []

        # load image and set anchor to center
        image = pyglet.image.load(IMAGE_PATH)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2

        self.sprite = pyglet.sprite.Sprite(image, x=self.x, y=self.y)

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.sprite.x = x
        self.sprite.y = y

    def shoot(self):
        bullet_start_y = self.y + self.sprite.height // 2
        self.bullets.append(Bullet(self.x, bullet_start_y))

    def update(self, dt):

        # update fire timer and shoot if possible
        self.fire_timer += dt
        while self.fire_timer >= self.fire_rate:
            self.shoot()
            self.fire_timer -= self.fire_rate

        # update bullets
        for bullet in self.bullets:
            bullet.update(dt)

        # remove bullets that are off-screen
        self.bullets = [bullet for bullet in self.bullets if bullet.y < 480]

    def draw(self):
        self.sprite.draw()
        for bullet in self.bullets:
            bullet.draw()
