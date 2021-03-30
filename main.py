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
import time


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

CREATURES_TO_SPAWN=75

#Testing movement speed
MOVEMENT_SPEED = 3

#food spawn RATE bigger means less smaller means more
FOOD_SPAWN_RATE = 10

#array to hold message center messages
message_center=[]

class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BRIGHT_NAVY_BLUE)

        self.updates=0

        #set directory
        file_path=os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # If you have sprite lists, you should create them here,
        # and set them to None
        #view port
        #zoom controls
        self.view_zoom="none"
        #camera controls
        self.hold_up=False
        self.hold_down=False
        self.hold_left=False
        self.hold_right=False
        # center viewpoint
        self.view_left=(WORLD_LENGTH-SCREEN_WIDTH)/2
        self.view_right=(WORLD_LENGTH - SCREEN_WIDTH)/2 + SCREEN_WIDTH
        self.view_down=(WORLD_LENGTH - SCREEN_HEIGHT)/2
        self.view_up=(WORLD_LENGTH - SCREEN_HEIGHT)/2 + SCREEN_HEIGHT

        #controls simulation speed
        self.simulation_speed=1

        #font size
        self.font_size=20

        self.update_rate=1/60

        self.hide_ui=False

        #time stuff
        self.total_runtime=0

        #total creatures generated
        self.total_creatures_generated=CREATURES_TO_SPAWN
        # simulation statistics
        self.total_kills = 0

        #index for which creature to display
        self.creature_display_stats_index=-1
        self.new_creature_index=False

        # hold creature list
        self.creature_list = None
        #track creature id's that have died
        self.dead_creatures_list=[]

        #set up creature info
        self.creature = None
        self.creature_displayed=None

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
        """ Set up the game variables. Call to re-start the game. """

        #set update rate to 60fps
        self.set_update_rate(1/60)


        #Sprite List
        self.creature_list=arcade.SpriteList()
        self.food_list=arcade.SpriteList()

        #add creatures
        for i in range(CREATURES_TO_SPAWN):
            self.creature = Creature(i)
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
                self.biome_list[i][j].center_x = (i)*BIOME_SCALING*BIOME_LENGTH
                self.biome_list[i][j].center_y = (j)*BIOME_SCALING*BIOME_LENGTH
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
            creature.draw_id(self.font_size)

        self.display_message_center()
        self.display_creature_stats()
        self.display_simulation_speed()

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        for i in range(self.simulation_speed):
            #spawn food
            self.spawn_food()
            self.food_list.update()
            self.creature_list.update()




            for creature in self.creature_list:
                self.move_creature(creature)
                creature.upkeep()
                #check for death
                if (creature.state == "dying" and creature.id not in self.dead_creatures_list):
                    message_center.append("Creature " + str(creature.id) + " has died")
                    self.dead_creatures_list.append(creature.id)

        #increment run time by 1/60
            self.total_runtime+=delta_time
            #self.total_runtime += 1

        self.creature_list.update_animation()
        if(self.hold_up==True and self.view_up<WORLD_LENGTH+500):
            self.view_up += VIEW_SPEED
            self.view_down += VIEW_SPEED
        if(self.hold_down==True and self.view_down>-500):
            self.view_up -= VIEW_SPEED
            self.view_down -= VIEW_SPEED
        if(self.hold_left==True and self.view_left>-500):
            self.view_left -= VIEW_SPEED
            self.view_right -= VIEW_SPEED
        if(self.hold_right==True and self.view_right<WORLD_LENGTH+500):
            self.view_left += VIEW_SPEED
            self.view_right += VIEW_SPEED
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
        message_center.append("Creature " + str(creature.id) + " has reproduced.")
        creature.num_reproduced+=1
        self.total_creatures_generated += 1
        self.creature = Creature(self.total_creatures_generated)
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
            #biome = arcade.get_sprites_at_point(creature.position,self.biome_sprite_list)
            biome=self.biome_list[0]
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
                    for c in self.creature_list:
                        if c.target == food:
                            c.target = None
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

    def display_simulation_speed(self):
        self.update_font_size()
        top_margin = self.font_size * 17
        scale=1
        if self.hide_ui==False:
            #display controls
            #box
            arcade.draw_rectangle_filled(center_x=self.view_left + self.font_size * 6,
                                         center_y=self.view_up - (self.font_size * 6) - top_margin,
                                         width=self.font_size * 19,
                                         height=self.font_size * 13,
                                         color=arcade.color.WHITE)
            arcade.draw_text("Simulation Controls: ", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale+=1
            arcade.draw_text("---------------------", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size*1.2)
            scale+=1
            arcade.draw_text("Zoom (in/out): =/- ", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Camera: WASD/Arrow Keys ", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Play/Pause: P/K ", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Speed up: L ", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Slow down: J ", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Hide Controls: H", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)


    def display_message_center(self):
        global message_center
        scaling=0

        #font size
        self.update_font_size()
        # draw white box around message center
        arcade.draw_rectangle_filled(center_x=self.view_left+20,
                                     center_y=self.view_down,
                                     width=self.font_size*35,
                                     height=self.font_size*20,
                                     color=arcade.color.WHITE)
        if(len(message_center)<10):
            size=-1
        else:
            size=len(message_center)-10
        for i in range(len(message_center)-1, size, -1):
            arcade.draw_text(message_center[i], self.view_left+self.font_size, self.view_down+(scaling*self.font_size), arcade.color.BLACK, self.font_size)
            scaling+=1

        # display simulation speed
        scaling=11
        arcade.draw_text("Simulation Speed: " + str(self.simulation_speed), self.view_left + self.font_size,
                         self.view_down+(scaling*self.font_size), arcade.color.BLACK,
                         self.font_size)
        #display simulation stats in bottom right corner
        #draw white box in bottom right corner
        arcade.draw_rectangle_filled(center_x=self.view_right - 20,
                                     center_y=self.view_down,
                                     width=self.font_size * 25,
                                     height=self.font_size * 22,
                                     color=arcade.color.WHITE)
        scaling=0

        arcade.draw_text("Total Runtime: " + self.convert_time(), self.view_right - self.font_size * 12,
                         self.view_down + self.font_size * 1.5 * scaling, arcade.color.BLACK, self.font_size)
        scaling += 1
        arcade.draw_text("Total Kills: " + str(self.total_kills), self.view_right - self.font_size * 12,
                         self.view_down + self.font_size * 1.5 * scaling, arcade.color.BLACK, self.font_size)
        scaling += 1
        arcade.draw_text("Total Deaths: " + str(self.total_creatures_generated - len(self.creature_list)),
                         self.view_right - self.font_size * 12,
                         self.view_down + self.font_size * 1.5 * scaling, arcade.color.BLACK, self.font_size)
        scaling += 1
        arcade.draw_text("Current population: "+str(len(self.creature_list)), self.view_right-self.font_size*12, self.view_down+self.font_size*1.5*scaling, arcade.color.BLACK, self.font_size)
        scaling+=1
        arcade.draw_text("Total Creatures: " + str(self.total_creatures_generated),
                         self.view_right - self.font_size * 12,
                         self.view_down + self.font_size * 1.5 * scaling, arcade.color.BLACK, self.font_size)
        scaling += 1
        arcade.draw_text("-----------------------------", self.view_right - self.font_size * 12,
                         self.view_down + self.font_size * 1.5 * scaling, arcade.color.BLACK, self.font_size)
        scaling += 1
        arcade.draw_text("Simulation Statistics:", self.view_right - self.font_size * 12,
                         self.view_down + self.font_size * 1.5 * scaling, arcade.color.BLACK, self.font_size)
        scaling += 1

    def display_creature_stats(self):
        #maintain same creature in display
        i=self.creature_display_stats_index
        if self.creature_displayed!=None:
            if self.new_creature_index:
                self.creature_displayed=self.creature_list[i]
        else:
            self.creature_displayed=self.creature_list[i]
        self.new_creature_index=False
        scale=1
        top_margin=self.font_size*5
        if(i!=-1 and i<len(self.creature_list)):
            creature=self.creature_displayed
            # draw white box around message center
            arcade.draw_rectangle_filled(center_x=self.view_right - self.font_size*7,
                                         center_y=self.view_up-(self.font_size*8)-top_margin,
                                         width=self.font_size * 13,
                                         height=self.font_size * 18,
                                         color=arcade.color.WHITE)

            # font size

            self.update_font_size()
            # writetext to right side of screen
            arcade.draw_text("Creature Information: ", self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale+=1
            arcade.draw_text("-----------------------", self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size * 1.2)
            scale += 1
            arcade.draw_text("Creature id: " + str(creature.id), self.view_right-(self.font_size*12),
                             self.view_up-(self.font_size*1.5*scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale+=1
            arcade.draw_text("Speed: " + str(creature.speed_mod), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5 * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("Food: " + str(int(round(creature.fullness,0)))+"/"+str(int(round(creature.max_food,0))), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5 * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("Sight: " + str(round(creature.sight_mod,3)), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5  * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("Food Upkeep: " + str(int(round(creature.food_upkeep*100, 0)))+"%", self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5  * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("State: " + str(creature.state), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5 * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("# Reproduced: " + str(creature.num_reproduced), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Total Kills: " + str(creature.num_kills), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Food Consumed: " + str(creature.num_food_eaten), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1

    def convert_time(self):
        m, s = divmod(self.total_runtime, 60)
        h, m = divmod(m, 60)

        return "%d:%02d:%02d" % (h, m, s)

    def update_font_size(self):
        segments = (WORLD_LENGTH * 1.3 + 500) / 12
        size = self.view_up - self.view_down
        for i in range(1, 13):
            if (size <= segments * i):
                self.font_size = i * 5
                break

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == arcade.key.UP or key==arcade.key.W:
            self.hold_up=True
        elif key == arcade.key.DOWN or key==arcade.key.S:
            self.hold_down=True
        elif key == arcade.key.LEFT or key==arcade.key.A:
            self.hold_left=True
        elif key == arcade.key.RIGHT or key==arcade.key.D:
            self.hold_right=True
        #zoom in and out when -/= key hit
        if( key == arcade.key.MINUS):
            self.view_zoom="zoom_out"
        if (key == arcade.key.EQUAL):
            self.view_zoom = "zoom_in"

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if (key == arcade.key.MINUS or key == arcade.key.EQUAL):
            self.view_zoom="none"
        elif key == arcade.key.UP or key == arcade.key.W:
            self.hold_up = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.hold_down = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.hold_left = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.hold_right = False
        elif key == arcade.key.P or key==arcade.key.K:
            #pause/play
            if self.update_rate==1/60:
                self.update_rate=0
                self.set_update_rate(self.update_rate)
            else:
                self.update_rate=1/60
                self.set_update_rate(self.update_rate)
        elif key == arcade.key.L:
            if self.simulation_speed<10:
                self.simulation_speed+=1
        elif key == arcade.key.J:
            if self.simulation_speed>1:
                self.simulation_speed-=1
        elif key == arcade.key.H:
            if self.hide_ui==False:
                self.hide_ui=True
            else:
                self.hide_ui=False



    def on_mouse_motion(self, x, y, delta_x, delta_y):
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

        for i in range(0, len(self.creature_list)):
            # click on creature
            #adjust x and y for view port
            x_adjusted=(x/SCREEN_WIDTH)*(self.view_right-self.view_left)+self.view_left
            y_adjusted=(y/SCREEN_HEIGHT)*(self.view_up-self.view_down)+self.view_down
            if (self.creature_list[i].center_x-CREATURE_WIDTH <= x_adjusted <= self.creature_list[i].center_x+CREATURE_WIDTH
                    and self.creature_list[i].center_y - CREATURE_HEIGHT <= y_adjusted <= self.creature_list[i].center_y + CREATURE_HEIGHT):
                self.creature_display_stats_index = i
                self.new_creature_index=True


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()