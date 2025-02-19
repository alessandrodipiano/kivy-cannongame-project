from kivy.config import Config

Config.set("graphics", "fullscreen", "auto")
import cannon_constants
import random
import time
import numpy as np
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.label import Label
from math import radians, cos, sin, pi
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import os
import json
import builtins

# functions to create the file to save the name for the leaderboard
def get_file_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
    return os.path.join(script_dir, filename)


# display the first 10 line of the file
def read_leaderboard(file_path):
    leaderboard = {}
    if not os.path.exists(file_path):
        open(file_path, 'w').close()  # Create the file if it doesn't exist
        print(f"File {file_path} created.")
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                name, points = line.strip().split(',')
                leaderboard[name] = {'points': float(points)}
    return leaderboard


def write_leaderboard(file_path, leaderboard):
    # Sort leaderboard by points in descending order
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1]['points'], reverse=True)
    with open(file_path, 'w') as file:
        for name, data in sorted_leaderboard:
            file.write(f"{name},{data['points']}\n")


def update_leaderboard(file_path, name, points):
    leaderboard = read_leaderboard(file_path)

    # Check if the name already exists and compare points
    if name in leaderboard:
        if points > leaderboard[name]['points']:
            leaderboard[name]['points'] = points

    else:
        leaderboard[name] = {'points': points, }
    write_leaderboard(file_path, leaderboard)


file_path = "leaderboard_text.txt"


# Creating a class to track keyboard inputs
class Keyboard:
    kb = None
    keys_pressed = []

    def get_keyboard(self):
        self.kb = Window.request_keyboard(self.on_keyboard_closed, None)
        self.kb.bind(on_key_down=self.on_key_down)
        self.kb.bind(on_key_up=self.on_key_up)

    def on_keyboard_closed(self):
        self.kb.unbind()
        self.kb = None

    def on_key_down(self, keyboard, keycode, text, h):
        if keycode[1] not in self.keys_pressed:
            self.keys_pressed.append(keycode[1])

    def on_key_up(self, keyboard, keycode):
        if keycode[1] in self.keys_pressed:
            self.keys_pressed.remove(keycode[1])

    def is_key_pressed(self, letter):
        if letter in self.keys_pressed:
            return True
        return False

    def get_pressed_keys(self):
        return self.keys_pressed


# Defining the other classes used in the game

class Rock(Image):
    pass


class Perpetio(Image):
    pass


class Laser(Image):
    pass


class Bullet(Image):
    pass


class Bombshell(Image):
    pass


class Mirror(Image):
    pass


class Cannon(Image):
    pass


class HelpImage(Image):
    pass


# Creating the background

class Background(Widget):
    # Enabling automatic future updates
    cloud_texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        # Setting the size of the canvas
        self.width = cannon_constants.SCREEN_WIDTH
        self.height = cannon_constants.SCREEN_HEIGHT

        super().__init__(**kwargs)

        # Wrapping the clouds around the screen
        self.cloud_texture = Image(source="cloud.png").texture
        self.cloud_texture.wrap = 'repeat'
        self.cloud_texture.uvsize = (cannon_constants.SCREEN_WIDTH / self.cloud_texture.width, -1)

    def cloud_move(self, time_passed):
        self.cloud_texture.uvpos = (
        (self.cloud_texture.uvpos[0] + time_passed / 2) % cannon_constants.SCREEN_WIDTH, self.cloud_texture.uvpos[1])
        texture = self.property('cloud_texture')
        texture.dispatch(self)


class Explosion(Image):  # add the image of the explosion not defined in kivy for semplicity
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (300, 100)
        self.source = "explosion.png"


class Target(Image):  # add target image not defined in kivy for semplicity
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (60, 60)
        self.source = "target.png"
        self.reset_position()

    def reset_position(self):
        max_x = cannon_constants.SCREEN_WIDTH - self.width
        max_y = cannon_constants.SCREEN_HEIGHT - self.height
        self.pos = (random.randint(0, max_x), random.randint(200, max_y))


# screen to take the user name for the leaderboard
class NameInputScreen(Screen):
    def __init__(self, **kwargs):
        super(NameInputScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=100, spacing=100)

        label = Label(
            text='Enter your name below:',
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.5}
        )

        self.text_input = TextInput(
            hint_text='Enter your name',
            multiline=False,
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.5}
        )
        self.text_input.bind(text=self.on_text)  # Bind the text input event

        start_button = Button(
            text='Start Game',
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.5},
            on_release=self.go_to_menu)

        layout.add_widget(label)
        layout.add_widget(self.text_input)
        layout.add_widget(start_button)
        self.add_widget(layout)

    def on_text(self, instance, value):  # added it to allow a max of letter
        if len(value) > 10:
            instance.text = value[:10]

    def go_to_menu(self, instance):
        name = self.text_input.text
        if name.strip():  # Ensure name is not empty
            self.manager.current = 'menu'  # if the name is valid change screen

            self.manager.get_screen('game').player_name = name
        else:
            self.text_input.hint_text = 'Please enter a valid name'


class MenuScreen(Screen):

    def go_to_game(self, mode='normal'):
        game_screen = self.manager.get_screen('game')
        game_screen.mode = mode  # Set the mode (normal or hard)
        self.manager.current = 'game'
        game_screen.start_game()

    def show_leaderboard(self):
        self.help_button_opacity_0()
        self.leader_board_opacity_0()
        self.load_button_opacity_0()
        self.play_button_opacity_0()
        self.hard_button_opacity_0()
        self.reset_button_opacity_0()
        self.disable_hard_button()
        self.disable_play_button()
        self.disable_leaderboard_button()
        self.disable_help_button()
        self.disable_reset_button()

        with open("leaderboard_text.txt", "r") as file:
            lines = file.readlines()
            top_10_lines = lines[:10]

            # Join the top 10 lines into a single string
            content = "".join(top_10_lines)

        leaderboard_label = self.ids.leaderboard_label
        leaderboard_label.text = content
        self.ids.back_button.opacity = 1
        self.ids.back_button.disabled = False

    def hide_leaderboard(self):
        self.ids.leaderboard_label.text = ""
        self.ids.back_button.opacity = 0
        self.ids.back_button.disabled = True
        self.leader_board_opacity_1()

        self.play_button_opacity_1()
        self.hard_button_opacity_1()
        self.help_button_opacity_1()
        self.reset_button_opacity_1()
        self.enable_hard_button()
        self.enable_play_button()

        self.enable_leaderboard_button()
        self.enable_help_button()
        self.enable_reset_button()

    def show_help(self):
        help_label = self.ids.help_label
        help_label.canvas.before.clear()
        help_text = self.read_help_text()  # Read the help text from the file
        help_label.text = help_text
        help_label.opacity = 1
        self.load_button_opacity_0()
        self.play_button_opacity_0()
        self.hard_button_opacity_0()
        self.help_button_opacity_0()
        self.reset_button_opacity_0()
        self.leader_board_opacity_0()
        self.disable_hard_button()
        self.disable_play_button()

        self.disable_leaderboard_button()
        self.disable_help_button()
        self.disable_reset_button()

    def hide_help(self):
        # hide the text if needed

        help_label = self.ids.help_label
        help_label.text = ""  # Clear the help text
        help_label.opacity = 0

        self.play_button_opacity_1()
        self.hard_button_opacity_1()
        self.leader_board_opacity_1()
        self.help_button_opacity_1()
        self.reset_button_opacity_1()
        self.enable_hard_button()
        self.enable_play_button()

        self.enable_leaderboard_button()
        self.enable_help_button()
        self.enable_reset_button()

    def read_help_text(self):
        help_file_path = get_file_path("help.txt")
        with open("help_text.txt", 'r') as file:
            help_text = file.read()
        return help_text

    # functions to disable or able the button
    def enable_load_button(self):
        self.ids.load_button.disabled = False

    def disable_load_button(self):
        self.ids.load_button.disabled = True

    def enable_hard_button(self):
        self.ids.hard_button.disabled = False

    def disable_hard_button(self):
        self.ids.hard_button.disabled = True

    def enable_play_button(self):
        self.ids.play_button.disabled = False

    def disable_play_button(self):
        self.ids.play_button.disabled = True

    def enable_leaderboard_button(self):
        self.ids.leadership_button.disabled = False

    def disable_leaderboard_button(self):
        self.ids.leadership_button.disabled = True

    def enable_help_button(self):
        self.ids.help_button.disabled = False

    def disable_help_button(self):
        self.ids.help_button.disabled = True

    def enable_reset_button(self):
        self.ids.reset_button.disabled = False

    def disable_reset_button(self):
        self.ids.reset_button.disabled = True

    # function to hide the disabled button
    def play_button_opacity_0(self):
        self.ids.play_button.opacity = 0

    def play_button_opacity_1(self):
        self.ids.play_button.opacity = 1

    def hard_button_opacity_0(self):
        self.ids.hard_button.opacity = 0

    def hard_button_opacity_1(self):
        self.ids.hard_button.opacity = 1

    def load_button_opacity_0(self):
        self.ids.load_button.opacity = 0

    def load_button_opacity_1(self):
        self.ids.load_button.opacity = 1

    def leader_board_opacity_0(self):
        self.ids.leadership_button.opacity = 0

    def leader_board_opacity_1(self):
        self.ids.leadership_button.opacity = 1

    def help_button_opacity_0(self):
        self.ids.help_button.opacity = 0

    def help_button_opacity_1(self):
        self.ids.help_button.opacity = 1

    def reset_button_opacity_0(self):
        self.ids.reset_button.opacity = 0

    def reset_button_opacity_1(self):
        self.ids.reset_button.opacity = 1

    def quit_game(self):  # called quit but it is used to reset the game in the menu
        # Reset game state
        game_screen = self.manager.get_screen('game')
        game_screen.setup_game()


# The main game class
class GameScreen(Screen):
    ### INITIAL SET UP ###

    rocks = []
    obs = []
    keyboard = Keyboard()

    start_time = NumericProperty(0)  # Variable to store the start time
    end_time = NumericProperty(0)  # Variable to store the end time
    # Adding player_name property to store the player's name
    player_name = StringProperty('')

    # Constants for the motion of the projectiles
    cannon_rotation = NumericProperty(0)

    initial_bullet_x = NumericProperty(0)
    initial_bullet_y = NumericProperty(0)
    bullet_start_time = NumericProperty(0)
    projectile_angle = NumericProperty(0)

    initial_bomb_x = NumericProperty(0)
    initial_bomb_y = NumericProperty(0)
    bomb_start_time = NumericProperty(0)

    # constant for tracking the important value
    shots_counter = NumericProperty(0)
    hits_counter = NumericProperty(0)
    power_output = NumericProperty(35)

    # used to store put values
    powerbullet = NumericProperty(0)
    powerbomb = NumericProperty(0)

    mode = StringProperty('normal')  # Add a mode property

    timer_event = None
    time_left = NumericProperty(10)  # Timer set to 60 seconds for hard mode
    remaining_time = NumericProperty(0)
    game_played = BooleanProperty(False)
    loaded_game_from_file = BooleanProperty(False)  # if it is true we do not generate new rock

    # Setting up the main functions once the game starts running
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.fire_event = None
        self.mirror_event = None
        self.laser_event = None
        self.target = None
        self.rocks = []
        self.obs = []
        self.projectile_active = False
        self.r_angle = 10
        self.laser_active = False

    # used to cancel the intervals schedued when you change screen
    def cancel_scheduled_intervals(self):
        for event in [self.on_key_down_cannon, self.ids.background.cloud_move, self.mirror_event]:
            Clock.unschedule(event)

    def on_start(self):
        Clock.schedule_interval(self.ids.background.cloud_move, 1 / cannon_constants.FPS)
        Clock.schedule_interval(self.on_key_down_cannon, 1 / cannon_constants.FPS)
        self.mirror_event = Clock.schedule_interval(self.mirror_movement, 2)

        self.keyboard.get_keyboard()

    def on_enter(self, *args):

        self.cancel_scheduled_intervals()

        self.on_start()

    def on_leave(self, *args):
        self.stop_timer()
        super(GameScreen, self).on_leave(*args)

    def start_game(self):

        if not self.loaded_game_from_file:
            # Remove existing rocks
            for rock in self.rocks:
                self.remove_widget(rock)
            self.rocks.clear()

            # Remove existing obstacles
            for obst in self.obs:
                self.remove_widget(obst)
            self.obs.clear()

            for i in range(random.randint(20, 25)):
                rock = Rock()
                rock.size_hint = (None, None)
                max_x = cannon_constants.SCREEN_WIDTH - 200  # Adjust to ensure rocks are fully visible
                random_x = random.randint(400, max_x)
                random_y = random.randint(10, 200)
                rock.pos = (random_x, random_y)
                rock.size = (118, 91)
                rock.opacity = 1
                rock.source = "rock.png"  # Set the source of the image
                self.rocks.append(rock)  # Keep track of the rocks in a list
                self.add_widget(rock)  # Add the rocks onto the screen

            # Set up random "perpetios" as obstacles
            for i in range(random.randint(5, 10)):
                obst = Perpetio()
                obst.size_hint = (None, None)
                obst.opacity = 1
                obst.source = "un_rock.png"  # Set the source of the image
                max_x = cannon_constants.SCREEN_WIDTH
                obst.pos = (random.randint(400, max_x), random.randint(40, 100))
                self.obs.append(obst)
                self.add_widget(obst)

        if self.mode == 'hard':
            self.ids.timer_label.opacity = 1
            self.start_timer()
        else:
            self.ids.timer_label.opacity = 0
        self.game_played = True

        self.start_time = time.time()  # Record the start time
        self.cancel_scheduled_intervals()  # Cancel any existing scheduled intervals

        # Remove existing target if any
        if self.target:
            self.remove_widget(self.target)

        self.mirror_movement(dt=0)
        self.mirror_event = Clock.schedule_interval(self.mirror_movement, 2)

        # Create and add the target
        self.target = Target()
        self.add_widget(self.target)
        self.move_target()  # Position the target randomly
        self.init_time = 60

    def start_timer(self):
        self.time_left = 60
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            self.ids.timer_label.text = f"Time Left: {self.time_left}"
        else:
            self.timer_event.cancel()
            self.manager.current = 'loser'

    def stop_timer(self):
        if self.timer_event:
            self.timer_event.cancel()

    ### FUNCTIONS OF THE CANNON ###

    # Method to move the cannon according to keyboard input
    def on_key_down_cannon(self, key):
        cannon = self.ids.cannon

        if self.mode == "normal":

            if self.keyboard.is_key_pressed('a'):
                cannon.x = max(0, cannon.x - 20)
            if self.keyboard.is_key_pressed('d'):
                cannon.x = min(Window.width - cannon.width, cannon.x + 20)
        if self.keyboard.is_key_pressed('spacebar') and not self.projectile_active:
            self.fire_bullet_button()
        if self.keyboard.is_key_pressed('b') and not self.projectile_active:
            self.fire_bombshell_button()
        if self.keyboard.is_key_pressed('l') and not self.projectile_active:
            self.fire_laser_button()
            self.hitted=False

        if self.keyboard.is_key_pressed("w"):
            self.turn_up(cannon)
        if self.keyboard.is_key_pressed("s"):
            self.turn_down(cannon)

        # method to charge a power output  (they work here dont touch)
        if self.keyboard.is_key_pressed("m") and self.power_output < 100:
            self.power_output += 1
            self.update_power_output_label(0)
        if self.keyboard.is_key_pressed("n") and self.power_output > 35:
            self.power_output -= 1
            self.update_power_output_label(0)

    # method to turn the muzzle of the cannon upwards
    def turn_up(self, widget):
        cannon = self.ids.cannon
        if cannon.angle <= 55:
            cannon.angle += 2
        anim = Animation(angle=cannon.angle)
        anim.start(widget)

    # method to turn the muzzle of the cannon downwards
    def turn_down(self, widget):
        cannon = self.ids.cannon
        if cannon.angle >= 10:
            cannon.angle -= 2
        anim = Animation(angle=cannon.angle)
        anim.start(widget)

    ### FUNCTIONS TO FIRE THE CANNON / LASER ###

    # Function to call the "fire_bullet" method
    def fire_bullet_button(self):  # called button since at the start it was a button
        self.shots_counter += 1  # Increment bullet count
        self.update_counters(0)  # Increment bullet count
        cannon = self.ids.cannon
        bullet = self.ids.bullet
        self.projectile_angle = radians(cannon.angle)  # store angle
        self.powerbullet = self.power_output / 35  # store power_output

        # Set the initial position of the bullet to the current position of the cannon
        self.initial_bullet_x = cannon.x + 40 + int(int(cannon.width * np.cos(cannon.angle / 180 * np.pi)) * 0.7)
        self.initial_bullet_y = cannon.y + 90 + int(int(cannon.height * np.sin(cannon.angle / 180 * np.pi)) * 0.7)

        # Move the bullet to the cannon's position
        bullet.x = self.initial_bullet_x
        bullet.y = self.initial_bullet_y
        bullet.opacity = 1  # Make the bullet visible

        self.bullet_start_time = Clock.get_time()  # Store the time when the bullet is fired

        self.projectile_active = True  # Set the projectile active flag
        self.fire_event = Clock.schedule_interval(self.fire_bullet, 1 / cannon_constants.FPS)

    # Function to call the "fire_bombshell" method
    def fire_bombshell_button(self):
        self.shots_counter += 3  # Increment bullet count
        self.update_counters(0)

        cannon = self.ids.cannon
        bomb = self.ids.bomb
        self.projectile_angle = radians(cannon.angle)  # store angle
        self.powerbomb = self.power_output / 35  # store power output

        # Set the initial position of the bullet to the current position of the cannon
        self.initial_bomb_x = cannon.x + 40 + int(int(cannon.width * cos(cannon.angle / 180 * pi)) * 0.7)
        self.initial_bomb_y = cannon.y + 90 + int(int(cannon.height * sin(cannon.angle / 180 * pi)) * 0.7)

        # Move the bullet to the cannon's position
        bomb.x = self.initial_bomb_x
        bomb.y = self.initial_bomb_y
        bomb.opacity = 1  # Make the bombshell visible

        self.bomb_start_time = Clock.get_time()  # Store the time when the bullet is fired

        self.projectile_active = True  # Set the projectile active flag
        self.fire_event = Clock.schedule_interval(self.fire_bombshell, 1 / cannon_constants.FPS)

    def fire_laser_button(self):  # the laser is a ball made of plasma
        if len(self.rocks) > 0:
            return  # Laser can only be fired after all rocks are destroyed

        self.shots_counter += 7  # Increment bullet count
        self.update_counters(0)
        cannon = self.ids.cannon
        laser = self.ids.laser
        self.projectile_angle = radians(cannon.angle)  # store angle

        # Set the initial position of the bullet to the current position of the cannon
        self.initial_laser_x = cannon.x + 40 + int(int(cannon.width * cos(cannon.angle / 180 * pi)) * 0.7)
        self.initial_laser_y = cannon.y + 90 + int(int(cannon.height * sin(cannon.angle / 180 * pi)) * 0.7)

        # Move the bullet to the cannon's position
        laser.x = self.initial_laser_x
        laser.y = self.initial_laser_y
        laser.opacity = 1  # Make the bullet visible

        self.laser_start_time = Clock.get_time()  # Store the time when the bullet is fired

        self.projectile_active = True  # Set the projectile active flag
        self.fire_event = Clock.schedule_interval(self.fire_laser, 1 / cannon_constants.FPS)

    ### FUNCTIONS OF THE MIRROR ###
    def mirror_movement(self, dt):
        mirror = self.ids.mirror

        # Define the new random position within the screen bounds
        new_x = random.uniform(300, cannon_constants.SCREEN_WIDTH - 300)
        new_y = random.uniform(0, 600)

        # Create an animation to move the object to the new position
        anim = Animation(x=new_x, y=new_y, duration=2, t='out_quad')
        anim.start(mirror)

    def check_mirror_collision(self, projectile):  # check for collision with bomb and bullet, NOT LASER
        if projectile.collide_widget(self.ids.mirror):
            self.reset_projectile(projectile)

    # FUNCTION FOR THE MOVEMENT OF THE TARGET
    def move_target(self):
        if self.target:
            new_x = random.uniform(600, cannon_constants.SCREEN_WIDTH - 30)
            new_y = random.uniform(200, cannon_constants.SCREEN_HEIGHT - 400)
            self.target.pos = (new_x, new_y)

    def move_target_animation(self):
        new_x = random.uniform(600, cannon_constants.SCREEN_WIDTH - 100)
        new_y = random.uniform(100, cannon_constants.SCREEN_HEIGHT - 600)

        anim = Animation(x=new_x, y=new_y, duration=2, t='out_quad')
        anim.start(self.target)

    def move_target_faster(self):
        new_x = random.uniform(600, cannon_constants.SCREEN_WIDTH - 100)
        new_y = random.uniform(100, cannon_constants.SCREEN_HEIGHT - 400)

        anim = Animation(x=new_x, y=new_y, duration=1, t='out_quad')

        anim.start(self.target)

        ### MOVEMENT OF THE PROJECTILES ###

    # The motion of the bullet when fired
    def fire_bullet(self, time_passed):
        obj = self.ids.bullet

        # Compute the time difference since the bullet was fired
        t = Clock.get_time() - self.bullet_start_time

        u = cannon_constants.BULLET_MAX_VEL
        g = cannon_constants.BULLET_MASS * 9.81
        obj.opacity = 1

        # Calculate the new position of the bullet
        obj.x = int(self.initial_bullet_x + u * t * np.cos(self.projectile_angle + radians(10)) * self.powerbullet)
        obj.y = int(self.initial_bullet_y + u * t * sin(self.projectile_angle + radians(10)) * self.powerbullet) - (
                    (1 / 2) * g * t ** 2)

        if obj.x < 0 or obj.x > cannon_constants.SCREEN_WIDTH or obj.y < 0 or obj.y > cannon_constants.SCREEN_HEIGHT:
            self.reset_projectile(obj)

        self.check_rock_collision(obj)
        self.check_target_collision(obj)
        self.check_mirror_collision(obj)

    def fire_bombshell(self, time_passed):
        obj = self.ids.bomb

        # Compute the time difference since the bullet was fired
        t = Clock.get_time() - self.bomb_start_time

        # Projectile parameters; the launch angle, initial velocity and gravity

        u = cannon_constants.BOMB_MAX_VEL
        g = cannon_constants.BOMB_MASS * 9.81
        obj.opacity = 1

        obj.x = int(self.initial_bomb_x + u * t * cos(self.projectile_angle + radians(10)) * self.powerbomb)
        obj.y = int(self.initial_bomb_y + u * t * sin(self.projectile_angle + radians(10)) * self.powerbomb - ((
                                                                                                                       1 / 2) * g * t ** 2))

        if obj.x < 0 or obj.x > cannon_constants.SCREEN_WIDTH or obj.y < 0 or obj.y > cannon_constants.SCREEN_HEIGHT:
            self.reset_projectile(obj)

        self.check_bombshell_collision(obj)
        self.check_target_collision(obj)
        self.check_mirror_collision(obj)

    def fire_laser(self, time_passed):
        obj = self.ids.laser


        # Compute the time difference since the bullet was fired
        t = Clock.get_time() - self.laser_start_time

        u = cannon_constants.LASER_VEL
        j=cannon_constants.REVERSE_LASER_VEL

        obj.opacity = 1

        if self.laser_mirror_collision(obj) or self.hitted==True:
            obj.x = int(obj.x + j * t * cos(self.projectile_angle + radians(20)))
            obj.y = int( obj.y - j * t * sin(self.projectile_angle + radians(20)))
            self.hitted=True

        if self.hitted==False:
            obj.x = int(self.initial_laser_x + u * t * cos(self.projectile_angle + radians(20)))
            obj.y = int(self.initial_laser_y + u * t * sin(self.projectile_angle + radians(20)))




        if obj.x < 0 or obj.x > cannon_constants.SCREEN_WIDTH or obj.y < 0 or obj.y > cannon_constants.SCREEN_HEIGHT:
            self.reset_projectile(obj)

        self.check_rock_collision(obj)
        self.check_target_collision(obj)

    def laser_mirror_collision(self, projectile):
        if projectile.collide_widget(self.ids.mirror):
            return True
        return False

    def reset_projectile(self, projectile):  # function to resets the projectiles
        self.projectile_active = False
        projectile.opacity = 0
        if self.fire_event:
            self.fire_event.cancel()

    # functions to update the various value
    def update_counters(self, dt):

        self.ids.shots_label.text = f"Shots: {self.shots_counter}"

    def update_power_output_label(self, dt):
        self.ids.power_output_label.text = f'Power Output: {self.power_output}'

    def update_hit_counter(self, dt):
        self.ids.hit_counter_label.text = f"Hits: {self.hits_counter}"

    # FUNCTION TO CHECK THE VARIOUS COLLISION
    def check_rock_collision(self, projectile):
        for rock in self.rocks:
            if projectile.collide_widget(rock):
                self.rocks.remove(rock)
                self.remove_widget(rock)
                self.reset_projectile(projectile)

    def check_bombshell_collision(self, projectile):
        explosion_radius = 200  # Set the explosion radius
        exploded = False
        for rock in self.rocks:
            if self.is_within_explosion_radius(projectile, rock, explosion_radius):
                self.rocks.remove(rock)
                self.remove_widget(rock)
                exploded = True

        if exploded:
            self.create_explosion(projectile.pos)
            self.reset_projectile(projectile)

    def create_explosion(self, position):
        explosion = Explosion()
        explosion.pos = position
        self.add_widget(explosion)
        Clock.schedule_once(lambda dt: self.remove_widget(explosion), 0.5)  # Remove explosion after 0.5 seconds

    def is_within_explosion_radius(self, projectile, rock, radius):
        distance = ((projectile.x - rock.x) ** 2 + (projectile.y - rock.y) ** 2) ** 0.5

        return distance <= radius

    def check_target_collision(self, projectile):

        if projectile.collide_widget(self.target):
            self.move_target()
            self.reset_projectile(projectile)
            self.hits_counter += 1
            self.update_hit_counter(0)
            if self.hits_counter >= 15:

                self.move_target_faster()


            elif self.hits_counter >= 10:

                self.move_target_animation()

            if self.mode == 'hard':
                self.time_left += 2  # Increase timer by 2 seconds in hard mode
                if self.time_left > self.init_time:
                    self.time_left = self.init_time

        if self.hits_counter == 20:    #when the user reaches 20 hits he wins
            self.manager.current = 'game_over'
            final_score = self.calculate_final_score()
            self.manager.get_screen('game_over').set_final_score(final_score)
            update_leaderboard(file_path, self.player_name, self.calculate_final_score())

    def setup_game(self):
        # put the counter back to 0

        self.shots_counter = 0
        self.hits_counter = 0
        self.power_output = 35
        self.time_left = 60

        self.ids.shots_label.text = f"Shots: {self.shots_counter}"
        self.ids.hit_counter_label.text = f"Hits: {self.hits_counter}"

        self.ids.power_output_label.text = f'Power Output: {self.power_output}'
        # Reset the position of the cannon
        cannon = self.ids.cannon
        cannon.x = 0
        cannon.y = 0
        cannon.angle = 0  # Reset the cannon angle if needed
        self.generate_rocks()
        # resets the button
        self.manager.get_screen('menu').enable_hard_button()
        self.manager.get_screen('menu').enable_play_button()
        self.manager.get_screen('menu').disable_load_button()
        self.manager.get_screen('menu').enable_help_button()
        self.manager.get_screen('menu').enable_leaderboard_button()
        self.manager.get_screen('menu').load_button_opacity_0()
        self.manager.get_screen('menu').hard_button_opacity_1()
        self.manager.get_screen('menu').play_button_opacity_1()
        self.manager.get_screen('menu').help_button_opacity_1()
        self.manager.get_screen('menu').leader_board_opacity_1()

    def generate_rocks(self):
        for i in range(random.randint(5, 10)):
            rock = Rock()
            rock.size_hint = (None, None)
            rock.size = (118, 91)
            max_x = cannon_constants.SCREEN_WIDTH - rock.width

            rock.pos = (random.randint(400, max_x), random.randint(10, 30))
            rock.source = "rock.png"
            self.rocks.append(rock)
            self.add_widget(rock)

    def calculate_final_score(self):
        if self.mode=="normal":
            final_score = round(self.hits_counter * 200 - self.shots_counter * 10)
            if final_score < 0:
                final_score = 0


        else:
            final_score = round((self.hits_counter * 200 - self.shots_counter * 10)*1.25)
            if final_score < 0:
                final_score = 0



        return final_score

    def show_menu(self):
        self.setup_game()
        self.mode = "normal"
        self.manager.current = 'menu'

        self.cancel_scheduled_intervals()

    def get_game_state(self):
        if self.mode == 'hard':
            remaining_time = self.time_left  # Directly use the current remaining time in hard mode
        else:
            remaining_time = 0  # No time limit in normal mode

        game_state = {
            "player_name": self.player_name,
            "shots_counter": self.shots_counter,
            "hits_counter": self.hits_counter,
            "power_output": self.power_output,
            "mode": self.mode,  # Save game mode
            "remaining_time": remaining_time,  # Save remaining time for hard mode
            "cannon": {
                "x": self.ids.cannon.x,
                "y": self.ids.cannon.y,
                "angle": self.ids.cannon.angle
            },
            "rocks": [{"x": rock.x, "y": rock.y} for rock in self.rocks],
            "obs": [{"x": obst.x, "y": obst.y} for obst in self.obs],
            "target": {"x": self.target.x, "y": self.target.y} if self.target else None,
        }

        return game_state

    def set_game_state(self, game_state):
        self.loaded_game_from_file = True
        self.player_name = game_state.get("player_name", "")
        self.shots_counter = game_state.get("shots_counter")
        self.hits_counter = game_state.get("hits_counter")
        self.power_output = game_state.get("power_output")
        self.mode = game_state.get("mode", 'normal')  # Load game mode
        self.remaining_time = game_state.get("remaining_time", 0)  # Load remaining time for hard mode

        if self.mode == 'hard':
            self.time_left = self.remaining_time  # Set time_left based on loaded remaining_time

        self.ids.cannon.x = game_state["cannon"]["x"]
        self.ids.cannon.y = game_state["cannon"]["y"]
        self.ids.cannon.angle = game_state["cannon"]["angle"]

        # Clear existing rocks and obstacles

        # Add rocks from the saved state
        for rock_state in game_state["rocks"]:
            rock = Rock(x=rock_state["x"], y=rock_state["y"])
            self.rocks.append(rock)
            self.add_widget(rock)
            rock.opacity = 1
            rock.source = "rock.png"  # Set the source of the image
            rock.size_hint = (None, None)
            rock.size = (118, 91)

        # Add obstacles from the saved state
        for obs_state in game_state["obs"]:
            obst = Perpetio(x=obs_state["x"], y=obs_state["y"])
            self.obs.append(obst)
            self.add_widget(obst)
            obst.opacity = 1
            obst.source = "un_rock.png"  # Set the source of the image
            obst.size_hint = (None, None)
        if game_state["target"]:
            self.target.x = game_state["target"]["x"]
            self.target.y = game_state["target"]["y"]

    def save_game(self):

        self.manager.get_screen('menu').disable_play_button()
        self.manager.get_screen('menu').disable_help_button()
        self.manager.get_screen('menu').disable_leaderboard_button()

        self.manager.get_screen('menu').disable_hard_button()

        game_state = self.get_game_state()
        with open('saved_game.json', 'w') as f:
            json.dump(game_state, f)
        self.manager.get_screen('menu').enable_load_button()  # Enable load button
        cannon = self.ids.cannon
        cannon.x = 0
        cannon.y = 0
        cannon.angle = 0  # Reset the cannon angle if needed
        self.manager.get_screen('menu').hard_button_opacity_0()
        self.manager.get_screen('menu').play_button_opacity_0()
        self.manager.get_screen('menu').load_button_opacity_1()
        self.manager.get_screen('menu').help_button_opacity_0()
        self.manager.get_screen('menu').leader_board_opacity_0()

    def load_game(self):

        self.loaded_game_from_file = BooleanProperty(False)
        if os.path.exists('saved_game.json'):
            with open('saved_game.json', 'r') as f:
                game_state = json.load(f)
                self.set_game_state(game_state)
            self.start_game()
            self.manager.get_screen('menu').disable_load_button()
        self.update_hit_counter(0)
        self.update_counters(0)
        self.time_left = self.remaining_time
        self.update_power_output_label(0)


class GameOverScreen(Screen):
    def set_final_score(self, final_score):
        self.ids.final_score_label.text = f"You Win! Final Score: {final_score}"

    def restart_game(self):
        self.manager.current = 'game'
        self.manager.get_screen('game').start_timer()
        self.manager.get_screen('game').setup_game()

    def return_to_menu(self):
        self.manager.current = 'menu'

        self.manager.get_screen('game').setup_game()

    def change_name(self):
        self.manager.current = 'name_input'

        self.manager.get_screen('game').setup_game()


class LoserScreen(Screen):
    def restart_game(self):
        self.manager.current = 'game'
        self.manager.get_screen('game').setup_game()
        self.manager.get_screen('game').mode = "hard"
        self.manager.get_screen('game').start_timer()

    def return_to_menu(self):
        self.manager.current = 'menu'
        self.manager.get_screen('game').setup_game()
        self.manager.get_screen('game').mode = "normal"

    def change_name(self):
        self.manager.current = 'name_input'
        self.manager.get_screen('game').setup_game()
        self.manager.get_screen('game').mode = "normal"


class MainApp(App):

    def build(self):
        self.sm = ScreenManager()
        self.input_Screen = NameInputScreen(name='name')
        self.menu_screen = MenuScreen(name='menu')
        self.game_screen = GameScreen(name='game')
        self.game_over_screen = GameOverScreen(name='game_over')
        self.loser_screen = LoserScreen(name="loser")
        self.sm.add_widget(NameInputScreen(name='name_input'))
        self.sm.add_widget(self.menu_screen)
        self.sm.add_widget(self.game_screen)
        self.sm.add_widget(self.game_over_screen)
        self.sm.add_widget(self.loser_screen)

        return self.sm

    def start_game(self):
        self.sm.current = 'game'
        self.game_screen.start_game()
        self.sm.get_screen('game').cancel_scheduled_intervals()
        self.menu_screen.hide_leaderboard()
        self.menu_screen.hide_help()


if __name__ == '__main__':
    MainApp().run()

