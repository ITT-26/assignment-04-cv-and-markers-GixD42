import cv2
import pyglet
from PIL import Image
from board_and_controls.board_recognizer import BoardRecognizer
from board_and_controls.finger_input import FingerInput
from game_objects.player import Player
from game_objects.enemy import EnemySpawner
from constants import *


# video capture and board / control setup
cap = cv2.VideoCapture(0)
recognizer = BoardRecognizer()
finger_input = FingerInput(recognizer)


# window setup
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

# for starting game
hold_timer = 0
game_running = False
is_warped = False
start_zone = (WINDOW_WIDTH // 2 - START_ZONE_W // 2, WINDOW_HEIGHT //
              2 + START_ZONE_OFFSET_Y, START_ZONE_W, START_ZONE_H)

# score and boolean to check if game is over
score_time = 0
game_over = False

# player character
player = Player(PLAYER_START_X, PLAYER_START_Y)


enemy_spawner = EnemySpawner()

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

    # get size of text -> calcuate x
    text_size = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, scale, THICKNESS)[0]

    # x position based on width of text and the window width
    text_x = (WINDOW_WIDTH - text_size[0]) // 2

    # black background (extra thickness)
    cv2.putText(frame, text, (text_x, y), cv2.FONT_HERSHEY_SIMPLEX,
                scale, TEXT_COLOR_BG, THICKNESS_BG, cv2.LINE_AA)
    # actual text
    cv2.putText(frame, text, (text_x, y), cv2.FONT_HERSHEY_SIMPLEX,
                scale, TEXT_COLOR, THICKNESS, cv2.LINE_AA)


def draw_start_rect(frame):

    # start zone variables
    x, y, width, height = start_zone

    # draw start zone
    cv2.rectangle(frame, (x, y), (x + width, y + height),
                  TEXT_COLOR, THICKNESS)


# to draw text not in cv2 -> everything drawn in pyglet -> order can be changed
def draw_overlay_text(text, y, size=20):
    # label on y axis centered on x axis
    label = pyglet.text.Label(
        text,
        x=WINDOW_WIDTH // 2,
        y=y,
        anchor_x="center",
        anchor_y="center",
        font_size=size,
        color=TEXT_COLOR
    )

    # background for text
    width = label.content_width + 10 * THICKNESS
    height = label.content_height + 10 * THICKNESS

    bg_x = label.x - width // 2

    # try to center background on text (seems pretty centered to me)
    bg_y_correction = 5
    bg_y = label.y - height // 2 - bg_y_correction

    # background rectangle so text is more readable
    background = pyglet.shapes.Rectangle(
        x=bg_x,
        y=bg_y,
        width=width,
        height=height,
        color=TEXT_COLOR_BG
    )
    background.draw()
    label.draw()


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

    display_frame = warped
    if MIRROR_INPUT:
        display_frame = cv2.flip(warped, 1)
        if finger_tip is not None:
            finger_tip = (WINDOW_WIDTH - finger_tip[0], finger_tip[1])

    # set player position to fingertip position
    if finger_tip is not None:
        # cv to pyglet
        x_cv, y_cv = finger_tip
        y_pyglet = WINDOW_HEIGHT - y_cv
        player.set_position(x_cv, y_pyglet)

    # if the game is over -> show game over screen and return early to not draw the game
    if game_over:
        draw_start_rect(display_frame)

    # draw start screen if game is not running
    elif not game_running and is_warped:
        draw_start_rect(display_frame)

    # draw board
    img = cv2glet(display_frame, "BGR")
    img.blit(0, 0, 0)

    # draw player (and bullets)
    player.draw()
    enemy_spawner.draw()

    # text for overlays
    if game_over:
        # game over -> show score
        draw_overlay_text("GAME OVER", 330, size=28)
        draw_overlay_text(f"Time: {int(score_time)}s", 290, size=20)
        # show how to restart if board is detected
        if is_warped:
            remaining = max(0, START_HOLD_SECONDS - hold_timer)
            draw_overlay_text(f"Hold here: {int(remaining)}s", 250, size=20)
        # if board is not detected -> ask to show board to restart
        else:
            draw_overlay_text("Show board to restart", 250, size=20)

    # game is not running
    elif not game_running:
        # board is detected -> show countdown to start
        if is_warped:
            remaining = max(0, START_HOLD_SECONDS - hold_timer)
            draw_overlay_text(
                f"Hold for {int(remaining)} seconds", 250, size=20)
        # if board is not detected -> ask to show board to start
        else:
            draw_overlay_text("Show board to start", 250, size=20)


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
