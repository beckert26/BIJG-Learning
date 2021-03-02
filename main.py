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
import math
import numpy
from Creature import *
from Biomes import *
from Food import *

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "BIJG Learning: Evolution Simulation"

CHARACTER_SCALING = 1.5
UPDATES_PER_FRAME=5


#viewport modifiers
VIEW_SPEED=10
ZOOM_SPEED_Y = (SCREEN_HEIGHT*.01)
ZOOM_SPEED_X = (SCREEN_WIDTH*.01)

#how many squares for 2d array of biome
BIOME_SIZE=25
WORLD_LENGTH=BIOME_LENGTH*BIOME_SIZE

CREATURES_TO_SPAWN=100

#Testing movement speed
MOVEMENT_SPEED = 3

#food spawn RATE bigger means less smaller means more
FOOD_SPAWN_RATE = 10

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
        #view port
        # center viewpoint
        self.view_change="none"
        self.view_zoom="none"
        self.view_left=(WORLD_LENGTH-SCREEN_WIDTH)/2
        self.view_right=(WORLD_LENGTH - SCREEN_WIDTH)/2 + SCREEN_WIDTH
        self.view_down=(WORLD_LENGTH - SCREEN_HEIGHT)/2
        self.view_up=(WORLD_LENGTH - SCREEN_HEIGHT)/2 + SCREEN_HEIGHT
        # hold creature list
        self.creature_list = None

        #set up creature info
        self.creature = None

        #set up biome None biome
        self.biome=Biomes(-1)

        #biome list initialize to biome size
        self.biome_sprite_list = arcade.SpriteList(use_spatial_hash=True, is_static=True)
        self.biome_list=[[self.biome for i in range(BIOME_SIZE)] for j in range(BIOME_SIZE)]

        # set up food list
        self.food_list = None
        #set up food
        self.food=None

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here

        #Sprite List
        self.creature_list=arcade.SpriteList()
        self.food_list=arcade.SpriteList()

        #add creatures
        for i in range(CREATURES_TO_SPAWN):
            self.creature = Creature()
            self.creature.max_food = random.randint(10,200)
            self.creature.speed_mod = random.randint(10,200)/100
            self.creature.biome_speed_mod = [random.randint(10,200)/100 for i in range(3)]
            self.creature.fullness = self.creature.max_food/2
            self.creature.sight_mod = random.randint(10,200)/100
            self.creature.set_upkeep()

            #random color
            r=random.randint(0,255)
            g=random.randint(0,255)
            b=random.randint(0,255)
            self.creature._set_color([r,g,b])

            #check overlap
            can_spawn=False
            failed=False
            while(can_spawn==False):
                creature_x = random.randint(0, WORLD_LENGTH - (CREATURE_WIDTH * 4))
                creature_y = random.randint(0, WORLD_LENGTH - (CREATURE_HEIGHT * 4))
                for creature in self.creature_list:
                    if (creature.center_x-CREATURE_WIDTH <= creature_x and creature_x <= creature.center_x+CREATURE_WIDTH
                            and creature.center_y-CREATURE_HEIGHT <= creature_y and creature_y <= creature.center_y+CREATURE_HEIGHT ):
                        failed=True
                if(failed==False):
                    can_spawn=True
                failed=False
            self.creature.center_x=creature_x
            self.creature.center_y=creature_y
            self.creature_list.append(self.creature)

        #set up world
        self.setup_biomes()

        #food test
        self.food=Food()
        self.food.center_x=400
        self.food.center_y=400
        self.food_list.append(self.food)

    def setup_biomes(self):
        # add biomes
        # random number assignment for 3 biome squares
        plain_random_x1 = random.randint(1, BIOME_SIZE-1)
        plain_random_y1 = random.randint(1, BIOME_SIZE-1)
        plain_random_x2 = random.randint(1, BIOME_SIZE - 1)
        plain_random_y2 = random.randint(1, BIOME_SIZE - 1)
        plain_random_x3 = random.randint(1, BIOME_SIZE - 1)
        plain_random_y3 = random.randint(1, BIOME_SIZE - 1)
        desert_random_x1 = random.randint(1, BIOME_SIZE - 1)
        desert_random_y1 = random.randint(1, BIOME_SIZE - 1)
        desert_random_x2 = random.randint(1, BIOME_SIZE - 1)
        desert_random_y2 = random.randint(1, BIOME_SIZE - 1)
        desert_random_x3 = random.randint(1, BIOME_SIZE - 1)
        desert_random_y3 = random.randint(1, BIOME_SIZE - 1)
        mountain_random_x1 = random.randint(1, BIOME_SIZE - 1)
        mountain_random_y1 = random.randint(1, BIOME_SIZE - 1)
        mountain_random_x2 = random.randint(1, BIOME_SIZE - 1)
        mountain_random_y2 = random.randint(1, BIOME_SIZE - 1)
        mountain_random_x3 = random.randint(1, BIOME_SIZE - 1)
        mountain_random_y3 = random.randint(1, BIOME_SIZE - 1)
        # add biomes
        #plain
        self.biome=Biomes(0)
        self.biome_list[plain_random_x1][plain_random_y1]=self.biome
        self.biome = Biomes(0)
        self.biome_list[plain_random_x2][plain_random_y2] = self.biome
        self.biome = Biomes(0)
        self.biome_list[plain_random_x3][plain_random_y3] = self.biome
        #mountain
        self.biome = Biomes(1)
        self.biome_list[mountain_random_x1][mountain_random_y1] = self.biome
        self.biome = Biomes(1)
        self.biome_list[mountain_random_x2][mountain_random_y2] = self.biome
        self.biome = Biomes(1)
        self.biome_list[mountain_random_x3][mountain_random_y3] = self.biome
        #desert
        self.biome = Biomes(2)
        self.biome_list[desert_random_x1][desert_random_y1] = self.biome
        self.biome = Biomes(2)
        self.biome_list[desert_random_x2][desert_random_y2] = self.biome
        self.biome = Biomes(2)
        self.biome_list[desert_random_x3][desert_random_y3] = self.biome

        #expand algorithm
        is_filled=False
        #fill conditions
        fill_plain=True
        fill_mountain=True
        fill_desert=True
        while(is_filled==False):
            #number of biomes
            i=random.randint(0,BIOME_SIZE-1)
            j=random.randint(0,BIOME_SIZE-1)
            if self.biome_list[i][j].type=="plain" and fill_plain==True:
                #up
                if(j>0):
                    if(self.biome_list[i][j-1].type=="none"):
                        self.biome=Biomes(0)
                        self.biome_list[i][j-1]=self.biome
                #down
                if(j<BIOME_SIZE-1):
                    if (self.biome_list[i][j+1].type=="none"):
                        self.biome = Biomes(0)
                        self.biome_list[i][j + 1] = self.biome
                #left
                if(i>0):
                    if (self.biome_list[i-1][j].type=="none"):
                        self.biome = Biomes(0)
                        self.biome_list[i-1][j] = self.biome
                #right
                if(i<BIOME_SIZE-1):
                    if (self.biome_list[i+1][j].type=="none"):
                        self.biome = Biomes(0)
                        self.biome_list[i+1][j] = self.biome
                fill_plain=False
            #expand mountain
            if self.biome_list[i][j].type=="mountain" and fill_mountain==True:
                #up
                if (j>0):
                    if(self.biome_list[i][j-1].type=="none"):
                        self.biome=Biomes(1)
                        self.biome_list[i][j-1]=self.biome
                #down
                if (j < BIOME_SIZE-1):
                    if (self.biome_list[i][j+1].type=="none"):
                        self.biome = Biomes(1)
                        self.biome_list[i][j + 1] = self.biome
                #left
                if (i > 0):
                    if (self.biome_list[i-1][j].type=="none"):
                        self.biome = Biomes(1)
                        self.biome_list[i-1][j] = self.biome
                #right
                if (i < BIOME_SIZE-1):
                    if (self.biome_list[i+1][j].type=="none"):
                        self.biome = Biomes(1)
                        self.biome_list[i+1][j] = self.biome
                fill_mountain=False
            #expand desert
            if self.biome_list[i][j].type=="desert" and fill_desert==True:
                #up
                if (j > 0):
                    if(self.biome_list[i][j-1].type=="none"):
                        self.biome=Biomes(2)
                        self.biome_list[i][j-1]=self.biome
                #down
                if (j < BIOME_SIZE-1):
                    if (j < BIOME_SIZE and self.biome_list[i][j+1].type=="none"):
                        self.biome = Biomes(2)
                        self.biome_list[i][j + 1] = self.biome
                #left
                if (i > 0):
                    if (self.biome_list[i-1][j].type=="none"):
                        self.biome = Biomes(2)
                        self.biome_list[i-1][j] = self.biome
                #right
                if (i < BIOME_SIZE-1):
                    if (self.biome_list[i+1][j].type=="none"):
                        self.biome = Biomes(2)
                        self.biome_list[i+1][j] = self.biome
                fill_desert=False
            #allow them to be filled after all have done a fill
            if(fill_plain==False and fill_desert==False and fill_mountain==False):
                fill_plain = True
                fill_mountain = True
                fill_desert = True
            is_filled=self.check_biome_fill()
        # set center location for biomes
        for i in range(BIOME_SIZE):
            for j in range(BIOME_SIZE):
                #attempted to manually center might need to be readjusted if map size changes
                self.biome_list[i][j].center_x = (i)*BIOME_SCALING*100
                self.biome_list[i][j].center_y = (j)*BIOME_SCALING*100
        #add all biomes to biome sprite list
        for i in range(BIOME_SIZE):
            for j in range(BIOME_SIZE):
                self.biome_sprite_list.append(self.biome_list[i][j])
    def check_biome_fill(self):
        for i in range(BIOME_SIZE):
            for j in range(BIOME_SIZE):
                if self.biome_list[i][j].type=="none":
                    return False
        return True
    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()


        self.biome_sprite_list.draw()
        self.creature_list.draw()
        self.food_list.draw()

        for creature in self.creature_list:
            creature.draw_health_bar()

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        #spawn food
        self.spawn_food()



        self.creature_list.update()

        self.creature_list.update_animation()
        #view port
        if (self.view_change=="left" and self.view_left>-500):
            self.view_left -= VIEW_SPEED
            self.view_right -= VIEW_SPEED
        if (self.view_change=="right" and self.view_right<WORLD_LENGTH+500):
            self.view_left += VIEW_SPEED
            self.view_right += VIEW_SPEED
        if (self.view_change=="up" and self.view_up<WORLD_LENGTH+500):
            self.view_up += VIEW_SPEED
            self.view_down += VIEW_SPEED
        if (self.view_change=="down" and self.view_down>-500):
            self.view_up -= VIEW_SPEED
            self.view_down -= VIEW_SPEED
        #zoom out
        if(self.view_zoom=="zoom_out" and self.view_up-self.view_down<=WORLD_LENGTH*1.3):
            self.view_up += ZOOM_SPEED_Y
            self.view_down -= ZOOM_SPEED_Y
            self.view_right += ZOOM_SPEED_X
            self.view_left -=ZOOM_SPEED_X
        #zoom in
        if (self.view_zoom == "zoom_in" and self.view_up-self.view_down>=200):
            self.view_up -= ZOOM_SPEED_Y
            self.view_down += ZOOM_SPEED_Y
            self.view_right -= ZOOM_SPEED_X
            self.view_left += ZOOM_SPEED_X
        arcade.set_viewport(self.view_left,self.view_right, self.view_down, self.view_up)


        for creature in self.creature_list:
            self.move_creature(creature)
            creature.upkeep()



    def spawn_food(self):
        for biome in self.biome_sprite_list:
            x = random.randint(1,math.floor((FOOD_SPAWN_RATE*BIOME_SIZE*BIOME_SIZE)/biome.food_spawn))
            if(x==1):
                self.food=Food()
                can_spawn = False
                failed = False
                while(can_spawn == False):
                    food_x = random.randint(biome.center_x - math.floor(BIOME_LENGTH/2), biome.center_x + math.floor(BIOME_LENGTH/2))
                    food_y = random.randint(biome.center_y - math.floor(BIOME_LENGTH/2), biome.center_y + math.floor(BIOME_LENGTH/2))
                    for food in self.food_list:
                        if (
                                food.center_x - FOOD_WIDTH <= food_x and food_x <= food.center_x + FOOD_WIDTH
                                and food.center_y - FOOD_HEIGHT <= food_y and food_y <= food.center_y + FOOD_HEIGHT):
                            failed = True
                    if (failed == False):
                        can_spawn = True
                    failed = False
                self.food.center_x = food_x
                self.food.center_y = food_y
                self.food_list.append(self.food)


        """
        #% chance of spawning food every tick
        x=random.randint(1,FOOD_SPAWN_RATE)
        if(x==1):
            self.food=Food()
            #check overlap
            can_spawn = False
            failed = False
            while (can_spawn == False):
                food_x = random.randint(0, WORLD_LENGTH - math.ceil(FOOD_WIDTH)*4)
                food_y = random.randint(0, WORLD_LENGTH - math.ceil(FOOD_HEIGHT)*4)
                for food in self.food_list:
                    if (
                            food.center_x - FOOD_WIDTH <= food_x and food_x <= food.center_x + FOOD_WIDTH
                            and food.center_y - FOOD_HEIGHT <= food_y and food_y <= food.center_y + FOOD_HEIGHT):
                        failed = True
                if (failed == False):
                    can_spawn = True
                failed = False
            self.food.center_x = food_x
            self.food.center_y = food_y
            self.food_list.append(self.food)
            """
    def breed(self, creature):
        print("new creature")
        self.creature = Creature()
        self.creature.max_food = creature.max_food * 1.0 + float((random.randint(-50, 50)/2000))
        self.creature.biome_speed_mod[0] = creature.biome_speed_mod[0] * 1.0 + float((random.randint(-50, 50) / 2000))
        self.creature.biome_speed_mod[1] = creature.biome_speed_mod[1] * 1.0 + float((random.randint(-50, 50) / 2000))
        self.creature.biome_speed_mod[2] = creature.biome_speed_mod[2] * 1.0 + float((random.randint(-50, 50) / 2000))
        self.creature.sight_mod = creature.sight_mod * 1.0 + float((random.randint(-50, 50) / 2000))
        self.creature.fullness = self.creature.max_food/2
        self.creature.set_upkeep
        # set color to parent color-------
        color_tup = creature._get_color()
        color = [color_tup[0], color_tup[1], color_tup[2]]
        color[0] = math.floor(color[0] * 1.0 + float((random.randint(-50, 50) / 2000)))
        color[1] = math.floor(color[1] * 1.0 + float((random.randint(-50, 50) / 2000)))
        color[1] = math.floor(color[1] * 1.0 + float((random.randint(-50, 50) / 2000)))
        for i in range(3):
            if color[i] < 0:
                color[i] = 0
            elif color[i] > 255:
                color[i] = 255
        self.creature._set_color((color[0], color[1], color[2]))

        # check overlap
        can_spawn = False
        failed = False
        while (can_spawn == False):
            creature_x = random.randint(0, WORLD_LENGTH - (CREATURE_WIDTH * 4))
            creature_y = random.randint(0, WORLD_LENGTH - (CREATURE_HEIGHT * 4))
            for creature in self.creature_list:
                if (
                        creature.center_x - CREATURE_WIDTH <= creature_x and creature_x <= creature.center_x + CREATURE_WIDTH
                        and creature.center_y - CREATURE_HEIGHT <= creature_y and creature_y <= creature.center_y + CREATURE_HEIGHT):
                    failed = True
            if (failed == False):
                can_spawn = True
            failed = False
        self.creature.center_x = creature_x
        self.creature.center_y = creature_y
        self.creature_list.append(self.creature)
        self.creature_list.update()
        self.creature_list.update_animation()
        creature.fullness = creature.fullness/2

    def move_creature(self, creature):
        target_tuple = arcade.get_closest_sprite(creature,self.food_list)
        if(target_tuple):
            target = target_tuple[0]
            dist = target_tuple[1]
            if(target and dist <= CREATURE_SIGHT * creature.sight_mod):
                creature.target = target
        if(not creature.target):
            if(len(self.food_list)>0):
                i = random.randint(0, len(self.food_list)-1)
                creature.target = self.food_list[i]

        if(creature.target):
            biome = arcade.get_sprites_at_point(creature.position,self.biome_sprite_list)
            direct = self.get_target_direction(creature, creature.target)
            if (biome):
                creature.change_x = MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[biome[0].biome] * direct[0]
                creature.change_y = MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[biome[0].biome] * direct[1]
            else:
                creature.change_x = MOVEMENT_SPEED * creature.speed_mod * direct[0]
                creature.change_y = MOVEMENT_SPEED * creature.speed_mod * direct[1]
            eat_list = arcade.check_for_collision_with_list(creature, self.food_list)
            for food in eat_list:
                if(creature.target == food):
                    creature.target = None
                    for creature in self.creature_list:
                        if creature.target == food:
                            creature.target = None
                food.kill()
                creature.feed()
                if(creature.fullness==creature.max_food):
                    self.breed(creature)


        """
        #target = self.get_nearest_food(creature)
        target=self.get_nearest_food(creature, creature.prev_target)
        if(creature.target != target and target):
            #print("test")
            creature.prev_target2 = creature.prev_target
            creature.prev_target = creature.target
            creature.target = target
        if(creature.target):
            creature_collision = arcade.check_for_collision_with_list(creature,self.creature_list)
            if(creature_collision):
                creature.prev_target = creature.target
                creature.target = self.get_nearest_food(creature, creature.prev_target)

       # else:
        #print(creature_collision)
        #    target_tuple = arcade.get_closest_sprite(creature, self.food_list)
        #    if(target_tuple):
        #        creature.target = target_tuple[0]
        if(creature.target):
            direct = self.get_target_direction(creature, creature.target)
            creature.change_x = MOVEMENT_SPEED * creature.speed_mod * direct[0]
            creature.change_y = MOVEMENT_SPEED * creature.speed_mod * direct[1]
            eat_list = arcade.check_for_collision_with_list(creature,self.food_list)
            for food in eat_list:
                food.kill()
        """

        """
        if(x==0):
            if(creature.center_y<WORLD_LENGTH):
                creature.change_y = MOVEMENT_SPEED*creature.speed_mod
        elif(x==1):
            if(creature.center_y>0):
                creature.change_y = -MOVEMENT_SPEED*creature.speed_mod
        elif(x==2):
            if (creature.center_x > 0):
                creature.change_x = -MOVEMENT_SPEED*creature.speed_mod
        else:
            if (creature.center_x < WORLD_LENGTH):
                creature.change_x = MOVEMENT_SPEED*creature.speed_mod
        """

    def get_target_direction(self, creature: arcade.Sprite, target: arcade.Sprite):
        x_dist = creature.center_x - target.center_x
        y_dist = creature.center_y - target.center_y
        return [numpy.sign(x_dist)*(-1), numpy.sign(y_dist)*(-1)]



    def get_nearest_food(self, creature, previous = None):
        if len(self.food_list) == 0:
            return None

        min_pos = 0
        min_distance = arcade.get_distance_between_sprites(creature, self.food_list[min_pos])
        for i in range(1, len(self.food_list)):
            if(self.food_list[i]!=previous and self.food_list[i]!=creature.prev_target2):

                distance = arcade.get_distance_between_sprites(creature, self.food_list[i])
                if distance < min_distance:
                    min_pos = i
                    min_distance = distance

        return self.food_list[min_pos]
        """
        smallest_dist = 99999.0
        nearest = self.food_list[0]
        for food in self.food_list:
            if(food!=previous):
                x_dist = math.fabs(creature.center_x - food.center_x)
                y_dist = math.fabs(creature.center_y - food.center_y)
                dist = math.sqrt(math.pow(x_dist,2) + math.pow(y_dist,2))
                if(dist < smallest_dist):
                    smallest_dist = dist
                    nearest = food
        return nearest
        """

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == arcade.key.UP or key==arcade.key.W:
            self.view_change="up"
        elif key == arcade.key.DOWN or key==arcade.key.S:
            self.view_change="down"
        elif key == arcade.key.LEFT or key==arcade.key.A:
            self.view_change="left"
        elif key == arcade.key.RIGHT or key==arcade.key.D:
            self.view_change="right"
        #zoom in and out when -/= key hit
        if( key == arcade.key.MINUS):
            self.view_zoom="zoom_out"
        if (key == arcade.key.EQUAL):
            self.view_zoom = "zoom_in"

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == arcade.key.UP or key == arcade.key.W:
            self.view_change = "none"
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.view_change = "none"
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.view_change = "none"
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.view_change = "none"
        elif (key == arcade.key.MINUS or key == arcade.key.EQUAL):
            self.view_zoom="none"

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        if(x>10 and x<100):
            self.view_change="left"
        elif(x>SCREEN_WIDTH-100 and x<SCREEN_WIDTH-10):
            self.view_change="right"
        elif(y>10 and y<100):
            self.view_change="down"
        elif(y>SCREEN_HEIGHT-100 and y<SCREEN_HEIGHT-10):
            self.view_change="up"
        else:
            self.view_change="none"

        if( delta_x<-10 or delta_x>10 or delta_y<-10 or delta_y>10):
            self.view_change="none"

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