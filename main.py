"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import arcade
import os
import random
from CreatureCharacter import *

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "BIJG Learning: Evolution Simulation"

CHARACTER_SCALING = 1.5
UPDATES_PER_FRAME=5

CREATURES_TO_SPAWN=20

#Testing movement speed
MOVEMENT_SPEED = 3

class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        #set directory
        file_path=os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # If you have sprite lists, you should create them here,
        # and set them to None

        # hold creature list
        self.creature_list = None

        #set up creature info
        self.creature = None


    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here

        #Sprite List
        self.creature_list=arcade.SpriteList()

        for i in range(CREATURES_TO_SPAWN):
            self.creature = CreatureCharacter()
            #random color
            r=random.randint(0,255)
            g=random.randint(0,255)
            b=random.randint(0,255)
            self.creature._set_color([r,g,b])
            self.creature.center_x=random.randint(20,SCREEN_WIDTH-20)
            self.creature.center_y=random.randint(20,SCREEN_HEIGHT-20)
            self.creature_list.append(self.creature)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        self.creature_list.draw()

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        for i in range(CREATURES_TO_SPAWN):
            self.move_creature(self.creature_list[i])

        self.creature_list.update()

        self.creature_list.update_animation()


    def move_creature(self, creature):
        x=random.randint(0,3)
        if(x==0):
            if(creature.center_y<SCREEN_HEIGHT):
                creature.change_y = MOVEMENT_SPEED
        elif(x==1):
            if(creature.center_y>0):
                creature.change_y = -MOVEMENT_SPEED
        elif(x==2):
            if (creature.center_x > 0):
                creature.change_x = -MOVEMENT_SPEED
        else:
            if (creature.center_x < SCREEN_WIDTH):
                creature.change_x = MOVEMENT_SPEED
    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == arcade.key.UP:
            self.creature.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.creature.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.creature.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.creature.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.creature.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.creature.change_x = 0

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()