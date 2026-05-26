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

# for starting game
START_HOLD_SECONDS = 3
hold_timer = 0
game_running = False
is_warped = False
start_zone = (WINDOW_WIDTH // 2 - 90, WINDOW_HEIGHT // 2 + 50, 180, 120)

# score and boolean to check if game is over
score_time = 0
game_over = False

# player character
player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2)


enemy_spawner = EnemySpawner(spawn_y=WINDOW_HEIGHT + 64, spawn_interval=1.5,
                             min_spawn_interval=1.0, max_spawn_interval=2.0)

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


# check if a point is in the start zone
def point_in_start_zone(point):
    if point is None:
        return False
    x, y = point
    return (start_zone[0] <= x <= start_zone[0] + start_zone[2] and
            start_zone[1] <= y <= start_zone[1] + start_zone[3])


# put text centered with bachground (background logic by ai)
def put_centered_text(frame, text, y, scale=1.0):

    color = (0, 255, 0)
    thickness = 2

    # get size of text -> calcuate x
    text_size = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)[0]

    # x position based on width of text and the window width
    text_x = (WINDOW_WIDTH - text_size[0]) // 2

    # black background
    cv2.putText(frame, text, (text_x, y), cv2.FONT_HERSHEY_SIMPLEX,
                scale, (0, 0, 0), thickness + 4, cv2.LINE_AA)
    # actual text
    cv2.putText(frame, text, (text_x, y), cv2.FONT_HERSHEY_SIMPLEX,
                scale, color, thickness, cv2.LINE_AA)


def draw_start_screen(frame):

    # no board detected -> tell player to show the board
    if not is_warped:
        put_centered_text(frame, "Show board to start", 240, scale=1.0)
        return

    # will only be called if is_warped is goes to True and will display a small area where the player needs to focus on to start the game
    x, y, width, height = start_zone

    # draw start zone
    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

    # remaining seconds to start the game
    remaining = max(0, START_HOLD_SECONDS - hold_timer)

    # instruction to start the game
    text = f"Hold for {int(remaining)} seconds"
    put_centered_text(frame, text, y - 10, scale=1.0)


def draw_game_over_screen(frame):
    # headline + score
    t = max(0, int(score_time))
    text1 = "GAME OVER"
    text2 = f"Time: {t}s"
    text3 = "Show board + hold to restart"

    put_centered_text(frame, text1, 150, scale=0.9)
    put_centered_text(frame, text2, 190, scale=0.9)
    put_centered_text(frame, text3, 240, scale=0.7)

    # if board is not detected, do not show restart zone
    if not is_warped:
        put_centered_text(frame, "Show board to restart", 270, scale=0.8)
        return

    # draw same restart zone as start zone
    x, y, width, height = start_zone
    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

    # restart countdown text
    remaining = max(0, START_HOLD_SECONDS - hold_timer)
    zone_text = f"Hold here: {int(remaining)}s"

    put_centered_text(frame, zone_text, y + height + 30, scale=0.7)


# clean up on close
@window.event
def on_close():
    cap.release()
    cv2.destroyAllWindows()
    pyglet.app.exit()
    return pyglet.event.EVENT_HANDLED


@window.event
def on_draw():
    global finger_tip, is_warped, game_running, game_over

    # clear window and read frame
    window.clear()

    ret, frame = cap.read()
    if not ret:
        return

    # get board and finger input
    corners, ids, _ = recognizer.detect_markers(frame)
    warped, is_warped = recognizer.warp_board(
        frame, corners, WINDOW_WIDTH, WINDOW_HEIGHT)

    debug, finger_tip, _ = finger_input.process_frame(warped)

    # set player position to fingertip position
    if finger_tip is not None:
        # cv to pyglet
        x_cv, y_cv = finger_tip
        y_pyglet = WINDOW_HEIGHT - y_cv
        player.set_position(x_cv, y_pyglet)

    # if the game is over -> show game over screen and return early to not draw the game
    if game_over:
        draw_game_over_screen(warped)

    # draw start screen if game is not running
    elif not game_running:
        draw_start_screen(warped)

    # draw board
    img = cv2glet(warped, "BGR")
    img.blit(0, 0, 0)

    # draw player (and bullets)
    player.draw()
    enemy_spawner.draw()


# update for game logic
def update_game(dt):
    global hold_timer, game_running, finger_tip, score_time, game_over

    if game_over:
        enemy_spawner.enemies.clear()
        player.bullets.clear()
        if not is_warped:
            return
        if point_in_start_zone(finger_tip):
            hold_timer += dt
            if hold_timer >= START_HOLD_SECONDS:
                game_over = False
                game_running = True
                hold_timer = 0
                score_time = 0
        else:
            hold_timer = 0
        return

    # if the board is not detected -> game isnt running -> reset game and timers
    if not is_warped:
        game_running = False
        hold_timer = 0
        return

    # if the game is not running -> check if player holds finger in start zone -> adjust timer accourdingly -> start game if countdown complete
    if not game_running:
        if point_in_start_zone(finger_tip):
            hold_timer += dt
            if hold_timer >= START_HOLD_SECONDS:
                game_running = True
                hold_timer = 0

        # restart timer if player leaves the start zone
        else:
            hold_timer = 0
        return

    # update game objects and score time
    player.update(dt)
    enemy_spawner.update(dt)
    score_time += dt

    # check if any enemy reached the bottom of the screen -> game over
    for enemy in enemy_spawner.enemies:
        if enemy.y < -enemy.sprite.height / 2:
            game_over = True
            game_running = False
            hold_timer = 0
            enemy_spawner.enemies.clear()
            player.bullets.clear()
            break

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
