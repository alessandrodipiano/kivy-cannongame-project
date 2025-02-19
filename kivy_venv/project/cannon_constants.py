# cannon_constants.py
from kivy.core.window import Window
# The size of the field of the game, in pixels.
SCREEN_WIDTH = Window.width
SCREEN_HEIGHT = Window.height

# The frame rate of the game, in frame/s.
FPS = 30

# Bullet and Bombshell projectiles parameter that affects the muzzle velocity range.
BULLET_MASS = SCREEN_WIDTH / 6
BOMB_MASS  = SCREEN_WIDTH / 4



# Laser muzzle velocity (not controlled by the player)
LASER_VEL = 1000
REVERSE_LASER_VEL= -100

# Bullet and Bombshell projectiles parameter that affects the (spherical) range of the damage.
BULLET_RADIUS = SCREEN_WIDTH / 100



# Additional constants


BOMB_MAX_VEL= 1000
BULLET_MAX_VEL = 1000  # Maximum velocity of the bullet


