import cv2
import pyglet
from board_recognizer import BoardRecognizer
from finger_input import FingerInput
from PIL import Image
import numpy as np
from player import Player
from enemy import EnemySpawner


# video capture and board / control setup
cap = cv2.VideoCapture(0)
recognizer = BoardRecognizer()
finger_input = FingerInput(recognizer)


# window setup
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

# player character
player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)


enemy_spawner = EnemySpawner(spawn_y=WINDOW_HEIGHT - 64, spawn_interval=1.5)

# position of fingertip -> player position
finger_tip = None


# converts OpenCV image to PIL image and then to pyglet texture
# https://gist.github.com/nkymut/1cb40ea6ae4de0cf9ded7332f1ca0d55
def cv2glet(img, fmt):
    '''Assumes image is in BGR color space. Returns a pyimg object'''
    if fmt == 'GRAY':
        rows, cols = img.shape
        channels = 1
    else:
        rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()

    top_to_bottom_flag = -1
    bytes_per_row = channels*cols
    pyimg = pyglet.image.ImageData(width=cols,
                                   height=rows,
                                   fmt=fmt,
                                   data=raw_img,
                                   pitch=top_to_bottom_flag*bytes_per_row)
    return pyimg


# simple check for collision between a bullet and an enemy
def bullet_enemy_collision(bullet, enemy):
    return (
        abs(bullet.x - enemy.x) * 2 < (bullet.sprite.width + enemy.sprite.width)
        and
        abs(bullet.y - enemy.y) *
        2 < (bullet.sprite.height + enemy.sprite.height)
    )


# clean up on close
@window.event
def on_close():
    cap.release()
    cv2.destroyAllWindows()
    pyglet.app.exit()
    return pyglet.event.EVENT_HANDLED


@window.event
def on_draw():
    global finger_tip

    # clear window and read frame
    window.clear()

    ret, frame = cap.read()
    if not ret:
        return

    # get board and finger input
    # TODO: PAUSE IF BOARD NOT DETECTED -> COUNTDONWN AFTER BOARD DETECTED AGAIN
    corners, ids, _ = recognizer.detect_markers(frame)
    warped = recognizer.warp_board(frame, corners, WINDOW_WIDTH, WINDOW_HEIGHT)

    debug, finger_tip, _ = finger_input.process_frame(warped)

    # set player position to fingertip position
    if finger_tip is not None:
        # cv to pyglet
        x_cv, y_cv = finger_tip
        y_pyglet = WINDOW_HEIGHT - y_cv
        player.set_position(x_cv, y_pyglet)

    # draw board
    img = cv2glet(warped, "BGR")
    img.blit(0, 0, 0)

    # draw player (and bullets)
    player.draw()
    enemy_spawner.draw()


# update for game logic
def update_game(dt):
    player.update(dt)
    enemy_spawner.update(dt)

    # bullets and enemies that collided will be removed
    bullets_to_remove = []
    enemies_to_remove = []

    # check every combination for collision
    for bullet in player.bullets:
        for enemy in enemy_spawner.enemies:
            if bullet_enemy_collision(bullet, enemy):
                bullets_to_remove.append(bullet)
                enemies_to_remove.append(enemy)

    # remove bullets
    for bullet in bullets_to_remove:
        if bullet in player.bullets:
            player.bullets.remove(bullet)

    # remove enemies
    for enemy in enemies_to_remove:
        if enemy in enemy_spawner.enemies:
            enemy_spawner.enemies.remove(enemy)


pyglet.clock.schedule_interval(update_game, 1/60.0)
pyglet.app.run()
