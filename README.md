[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5NorvP5a)

# 0 Requirements and installation

- Python (3.13 used to code this)
- Install requirements using pip install -r requirements.txt

# 1 Perspective Transformation

This script applies Perspective Transformation based on 4 points selected on a chosen image and desired output dimensions.

## Usage:

start the script by using this command line input (in the perspective_transformation folder):<br>
```python image_extractor.py --input path/to/image.jpg --output path/to/output.jpg --outwidth width --outheight height```

## Controls:
Use your mouse to select 4 points with the left mouse button.
If you click your mouse again the transformation will start.
<br>I chose this design to let the user see all 4 points before the transformation starts. (In the assignment it should be shown after all 4 points have been selected but I wanted to see the points that will be used before)
<br><br>
To quit the script press 'Q'
<br><br>
To reset the points and return to the initial Image after the transformed one is displayed press 'ESC'
<br><br>
To save the transformed image to the desired output path press 'S'
<br>
Note that this can only be used when looking at the transformed picture

# 2 AR Game

In this game you control a spacecraft and need to defend yourself from invading alien spaceships. If one of the enemies can get past you and exit the screen on the bottom you lost.

## Starting the game

start the game by entering this into your command line (in the ar_game folder):<br>
```python ar_game.py```

## Configuration

The file constants.py (in the ar_game folder) can be edited to change the game experience.
If you have trouble with the finger recognition try running finger_input.py (in the boards_and_controls folder) and adjust the WIHITE_MASK_LOWER and WHITE_MASK_UPPER constants. Note that those values are not in rgb but in hsv to isolate the brightness.

Try to change the window size to your cameras dimensions for the best experience.

All the other constants are explained in the file and can be changed to alter gameplay a bit.

## Controls

This game is fully controlled by your finger. To properly play it is important to note that your finger should come in from below your aruco paper.<br>
I decided to handle it that way because the enemies will come down and you have to defend from the bottom.<br>

## Guide

First you need to let the camera recognize the board.<br>
Then you should point to the starting area for 3 seconds to start the game.<br>
If the camera loses focus on the points for too long the game will pause and return to the start screen but the game itself will just be paused.<br>
To control the spaceship just move your finger around and it will shoot automatically. Try to hit the enemies before they can get to the ground.<br>
Once one enemy reached the ground it will be a game over.<br>
You will see the time that you lasted as your score.<br>
To restart the game do the first two steps again. They will work in the game over screen as well.