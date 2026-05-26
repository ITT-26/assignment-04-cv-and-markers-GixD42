# All constants

# for detection of the finger tip -> try out finger_input.py to find good values for your lighting
WHITE_MASK_LOWER = (0, 0, 100)
WHITE_MASK_UPPER = (180, 40, 255)

# mirror input from camera -> change depending on your camera setup
MIRROR_INPUT = True

# window dimensions -> best if the same as the camera resolution
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# starting the game
START_HOLD_SECONDS = 3
START_ZONE_W = 180
START_ZONE_H = 120
START_ZONE_OFFSET_X = -90
START_ZONE_OFFSET_Y = 50

# Player position at start (off-screen)
PLAYER_START_X = -100
PLAYER_START_Y = -100

# fire rate of player bullets (seconds between shots)
PLAYER_FIRE_RATE = 0.5
BULLET_SPEED = 100

# Enemy behavior and spawn settings
ENEMY_SIZE = 64
ENEMY_SPAWN_Y = WINDOW_HEIGHT + ENEMY_SIZE
ENEMY_SPEED = 150
# spawn interval with minimum and maximum for randomization
ENEMY_SPAWN_INTERVAL = 1.0
ENEMY_MIN_SPAWN_INTERVAL = 0.5
ENEMY_MAX_SPAWN_INTERVAL = 1.5

# Text settings
TEXT_COLOR = (0, 255, 0, 255)
TEXT_COLOR_BG = (0, 0, 0, 255)

THICKNESS = 2
THICKNESS_BG = THICKNESS + 4
