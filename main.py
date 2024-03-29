"""
Creature Simulations

By BIJG Learning

Created for Capstone II
"""

import arcade
import os
import random
import math
import numpy
from Creature import *
from Biomes import *
from Brain import *
from Food import *
import ctypes
#from sklearn import preprocessing
#import time

import arcade.gui
from arcade.gui import UIFlatButton, UIGhostFlatButton, UIManager


# Screen constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "BIJG Learning: Evolution Simulation"

# For creature size
CHARACTER_SCALING = 1.5

# viewport modifiers
VIEW_SPEED=10
ZOOM_SPEED_Y = (SCREEN_HEIGHT*.01)
ZOOM_SPEED_X = (SCREEN_WIDTH*.01)

# how many squares for 2d array of biome
BIOME_SIZE=25
WORLD_LENGTH=BIOME_LENGTH*BIOME_SIZE

# default spawn size
CREATURES_TO_SPAWN=75

# how full a creature needs to be to reproduce this should be between .51 and 1
REPRODUCTION_RATE=.5

# rate food spawns
FOOD_SPAWN_RATE=5

# default mutation rate
MUTATION_RATE=1

#Testing movement speed
MOVEMENT_SPEED = 3

#seed
SEED = 10

#array to hold message center messages
message_center=[]

#window
window=None

#inputs
population_input=None
mutation_input=None
reproduction_input=None
food_input=None

class MyGame(arcade.View):
    """
    Main application class.
    """

    # initialize with user input
    def __init__(self, umode=1, atk='t', uspeed=5, ubiome=5, ufood=5, udmg=5, usight=5, biome_spawn=[1.5,1.1,0.8], upkeep_mod=5 ):
        super().__init__()

        #set directory
        file_path=os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        #player set stuff
        self.umode = umode
        self.atk = atk
        self.uspeed = uspeed
        self.ubiome = ubiome
        self.udmg = udmg
        self.usight = usight
        self.biome_spawn = biome_spawn
        self.upkeep_mod = upkeep_mod
        self.ufood = ufood

        #view port
        #zoom controls
        self.view_zoom="none"
        #camera controls
        self.hold_up=False
        self.hold_down=False
        self.hold_left=False
        self.hold_right=False
        # center viewpoint
        self.view_left=-65
        self.view_right=self.view_left+SCREEN_WIDTH*2
        self.view_down=400
        self.view_up=self.view_down+SCREEN_HEIGHT*2

        #controls simulation speed
        self.simulation_speed=1

        #font size
        self.font_size=20

        #variables for arcade lib
        self.update_rate=1/60
        self.hide_ui=False

        #time stuff
        self.total_runtime=0
        self.sim_time=0

        #total creatures generated
        self.total_creatures_generated=CREATURES_TO_SPAWN
        # simulation statistics
        self.total_kills = 0

        #index for which creature to display
        self.creature_display_stats_index=-1
        self.new_creature_index=False

        # hold creature list
        self.creature_list = arcade.SpriteList()
        #track creature id's that have died
        self.dead_creatures_list=[]

        #set up creature info
        self.creature: Creature = None
        self.creature_displayed=None
        self.creature_textures = []

        #set up biome None biome
        self.biome_textures = [arcade.load_texture(f"sprites/biome/plain.png"),
                               arcade.load_texture(f"sprites/biome/mountain.png"),
                               arcade.load_texture(f"sprites/biome/desert.png")]
        self.biome: Biomes=Biomes(-1,self.biome_textures)

        #biome list initialize to biome size
        self.biome_sprite_list = arcade.SpriteList(use_spatial_hash=True, is_static=True)
        self.biome_list=[[self.biome for i in range(BIOME_SIZE)] for j in range(BIOME_SIZE)]

        # set up food list
        self.food_list = arcade.SpriteList(use_spatial_hash=True, is_static=True)
        self.food_texture = arcade.load_texture(f"sprites/food/apple.png")
        #set up food
        self.food=None

        # This is for machine learning, but not functional
        #self.brain = Brain()

        # seed the game
        random.seed(SEED)

        # set up creature textures
        self.creature_textures.append(load_texture_pair(f"sprites/slimeIdle.gif"))
        #walking
        for i in range(7):
            texture = arcade.load_texture_pair(f"sprites/walk/frame_{i}_delay-0.1s.gif")
            self.creature_textures.append(texture)
        #attacking
        for i in range(6):
            texture= arcade.load_texture_pair(f"sprites/attack/frame_{i}_delay-0.1s.gif")
            self.creature_textures.append(texture)
        #dying
        for i in range(16):
            if(i<10):
                texture = arcade.load_texture_pair(f"sprites/die/frame_0{i}_delay-0.1s.gif")
            else:
                texture= arcade.load_texture_pair(f"sprites/die/frame_{i}_delay-0.1s.gif")
            self.creature_textures.append(texture)

        #damaged
        for i in range(7):
            texture= arcade.load_texture_pair(f"sprites/damage/frame_{i}_delay-0.1s.gif")
            self.creature_textures.append(texture)

        # add creatures
        for i in range(CREATURES_TO_SPAWN):
            # initialize creature
            self.creature = Creature(i,self.creature_textures,creature_upkeep = self.upkeep_mod,
                                 ufood = self.ufood, usight = self.usight, uspeed = self.uspeed, udmg = self.udmg,
                                 ubiome = self.ubiome, umode = self.umode)
            # set creature variables
            self.creature.max_food = random.randint(40, 200)
            self.creature.speed_mod = random.randint(10, 200) / 100
            self.creature.biome_speed_mod = [random.randint(10, 200) / 100 for i in range(3)]
            self.creature.biome_affinity = [random.randint(0, 100) / 100 for i in range(3)]
            self.creature.fullness = self.creature.max_food / 2
            self.creature.sight_mod = random.randint(50, 200) / 100
            self.creature.aggro = random.randint(0, 100) / 100
            self.creature.damage_mod = random.randint(0, 100) / 100

            # random color
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)

            self.creature._set_color([r, g, b])

            # spawn and check overlap
            can_spawn = False
            failed = False
            # while overlap choose new location
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

            #get current biome
            i = int((self.creature.center_x + 50) / 100)
            if (i < 0):
                i = 0
            if (i > 24):
                i = 24
            j = int((self.creature.center_y + 50) / 100)
            if (j < 0):
                j = 0
            if (j > 24):
                j = 24
            self.creature.cur_biome = self.biome_list[i][j].biome
            self.creature.set_upkeep()
            self.creature_list.append(self.creature)

        # set up world
        self.setup_biomes()

        # food test
        self.food = Food(self.food_texture)
        self.food.center_x = 400
        self.food.center_y = 400
        self.food_list.append(self.food)


    def on_show_view(self):
        """ Called once when view is activated. """
        arcade.set_background_color(arcade.color.BRIGHT_NAVY_BLUE)

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
        self.biome=Biomes(0,self.biome_textures)
        self.biome_list[plain_random_x1][plain_random_y1]=self.biome
        self.biome = Biomes(0,self.biome_textures)
        self.biome_list[plain_random_x2][plain_random_y2] = self.biome
        self.biome = Biomes(0,self.biome_textures)
        self.biome_list[plain_random_x3][plain_random_y3] = self.biome
        #mountain
        self.biome = Biomes(1,self.biome_textures)
        self.biome_list[mountain_random_x1][mountain_random_y1] = self.biome
        self.biome = Biomes(1,self.biome_textures)
        self.biome_list[mountain_random_x2][mountain_random_y2] = self.biome
        self.biome = Biomes(1,self.biome_textures)
        self.biome_list[mountain_random_x3][mountain_random_y3] = self.biome
        #desert
        self.biome = Biomes(2,self.biome_textures)
        self.biome_list[desert_random_x1][desert_random_y1] = self.biome
        self.biome = Biomes(2,self.biome_textures)
        self.biome_list[desert_random_x2][desert_random_y2] = self.biome
        self.biome = Biomes(2,self.biome_textures)
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
                        self.biome=Biomes(0,self.biome_textures)
                        self.biome_list[i][j-1]=self.biome
                #down
                if(j<BIOME_SIZE-1):
                    if (self.biome_list[i][j+1].type=="none"):
                        self.biome = Biomes(0,self.biome_textures)
                        self.biome_list[i][j + 1] = self.biome
                #left
                if(i>0):
                    if (self.biome_list[i-1][j].type=="none"):
                        self.biome = Biomes(0,self.biome_textures)
                        self.biome_list[i-1][j] = self.biome
                #right
                if(i<BIOME_SIZE-1):
                    if (self.biome_list[i+1][j].type=="none"):
                        self.biome = Biomes(0,self.biome_textures)
                        self.biome_list[i+1][j] = self.biome
                fill_plain=False
            #expand mountain
            if self.biome_list[i][j].type=="mountain" and fill_mountain==True:
                #up
                if (j>0):
                    if(self.biome_list[i][j-1].type=="none"):
                        self.biome=Biomes(1,self.biome_textures)
                        self.biome_list[i][j-1]=self.biome
                #down
                if (j < BIOME_SIZE-1):
                    if (self.biome_list[i][j+1].type=="none"):
                        self.biome = Biomes(1,self.biome_textures)
                        self.biome_list[i][j + 1] = self.biome
                #left
                if (i > 0):
                    if (self.biome_list[i-1][j].type=="none"):
                        self.biome = Biomes(1,self.biome_textures)
                        self.biome_list[i-1][j] = self.biome
                #right
                if (i < BIOME_SIZE-1):
                    if (self.biome_list[i+1][j].type=="none"):
                        self.biome = Biomes(1,self.biome_textures)
                        self.biome_list[i+1][j] = self.biome
                fill_mountain=False
            #expand desert
            if self.biome_list[i][j].type=="desert" and fill_desert==True:
                #up
                if (j > 0):
                    if(self.biome_list[i][j-1].type=="none"):
                        self.biome=Biomes(2,self.biome_textures)
                        self.biome_list[i][j-1]=self.biome
                #down
                if (j < BIOME_SIZE-1):
                    if (j < BIOME_SIZE and self.biome_list[i][j+1].type=="none"):
                        self.biome = Biomes(2,self.biome_textures)
                        self.biome_list[i][j + 1] = self.biome
                #left
                if (i > 0):
                    if (self.biome_list[i-1][j].type=="none"):
                        self.biome = Biomes(2,self.biome_textures)
                        self.biome_list[i-1][j] = self.biome
                #right
                if (i < BIOME_SIZE-1):
                    if (self.biome_list[i+1][j].type=="none"):
                        self.biome = Biomes(2,self.biome_textures)
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
                #self.biome_list[i][j].set_texture(0)
                self.biome_list[i][j].update_spawn(self.biome_spawn)
                self.biome_sprite_list.append(self.biome_list[i][j])


    def check_biome_fill(self):
        """
        Function checks all biomes to see if any are not filled
        returns True/False if filled
        """
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

        #draw sprites
        self.biome_sprite_list.draw()
        self.creature_list.draw()
        self.food_list.draw()

        #draw health bars
        for creature in self.creature_list:
            creature.draw_health_bar()
            creature.draw_id(self.font_size)

        #all message centers/stats
        self.display_message_center()
        self.display_creature_stats()
        self.display_simulation_controls()


    def on_update(self, delta_time):

        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        #runtime count
        self.total_runtime += delta_time

        #updates per frame update
        for i in range(self.simulation_speed):
            #spawn food
            #adjsut lower bounds for less spawning
            x = random.randint(-10, FOOD_SPAWN_RATE)
            for j in range(0,x):
                self.spawn_food()
            if(len(self.food_list)>150):
                i = random.randint(0,len(self.food_list)-1)
                self.food_list[i].kill()
            self.food_list.update()
            self.creature_list.update()

            # do movement for each creature
            for creature in self.creature_list:
                # if creature is not dying do the movement
                if creature.state != "dying":
                    # If no target just wander
                    if creature.target == None and ((creature.attack_targ == None and creature.def_targ == None) or self.atk == 'f'):
                        self.wander(creature)
                    # if attack target do attack behavior
                    elif creature.attack_targ != None and self.atk == 't':
                        self.attack_creature(creature)
                    # if def target do defence behavior
                    elif creature.def_targ != None and self.atk == 't':
                        self.defend_creature(creature)
                    # if target and no def or attack target then just move to the target
                    else:
                        self.move_creature(creature)
                    creature.upkeep()

                #check for death if speed high don't do animation just kill directly
                if(creature.id not in self.dead_creatures_list):
                    if(creature.state == "dying" and self.simulation_speed>2):
                        message_center.append("Creature " + str(creature.id) + " has died")
                        # no_food is a variable used to prevent food spawn when creature dies in combat because that is calculated seperately
                        if creature.no_food == False:
                            # spawn new food from dead creature
                            new_food = Food(self.food_texture,creature.max_food/4)
                            new_food.center_x = creature.center_x
                            new_food.center_y = creature.center_y
                            self.food_list.append(new_food)
                        creature.kill()

                    # if speed not high
                    elif (creature.state == "dying"):
                        message_center.append("Creature " + str(creature.id) + " has died")
                        self.dead_creatures_list.append(creature.id)
                        # no_food is a variable used to prevent food spawn when creature dies in combat because that is calculated seperately
                        if creature.no_food == False:
                            # spawn new food from dead creature
                            new_food = Food(self.food_texture,creature.max_food/3)
                            new_food.center_x = creature.center_x
                            new_food.center_y = creature.center_y
                            self.food_list.append(new_food)
                            creature.no_food = True
                        # Nullify movement
                        creature.change_x = 0
                        creature.change_y = 0

            """
            #this code was from out machine learning implementation
            for creature in self.creature_list:
                if creature.state != "dying":
                    if creature.state_next:
                        creature.bstate = creature.state_next
                    else:
                        creature.bstate = self.get_inputs(creature)
                        #arr = np.array(creature.bstate)
                        #print(arr.shape)
                    #action=0
                    action = self.brain.decision(creature.bstate)
                    self.do_action(creature,action)
                    done = creature.upkeep()
                    creature.state_next = self.get_inputs(creature)
                    self.brain.update(action,creature.bstate,creature.state_next,creature.reward,done)
                    creature.reward = 0
                    #creature.upkeep()

                #for creature in self.creature_list:
                #check for death
                if(creature.state == "dying" and self.simulation_speed>2):
                    message_center.append("Creature " + str(creature.id) + " has died")
                    self.dead_creatures_list.append(creature.id)
                    creature.change_x = 0
                    creature.change_y = 0
                    creature.kill()
                elif (creature.state == "dying" and creature.id not in self.dead_creatures_list):
                    message_center.append("Creature " + str(creature.id) + " has died")
                    self.dead_creatures_list.append(creature.id)
                    creature.change_x = 0
                    creature.change_y = 0
            """
            # increment sim time once each update cycle
            self.sim_time += 1

            #spawn random creature for every 10 creatures reproduced
            if((self.total_creatures_generated-CREATURES_TO_SPAWN)%10 == 0 and self.total_creatures_generated-CREATURES_TO_SPAWN != 0):
                # creature init
                self.creature = Creature(self.total_creatures_generated,self.creature_textures,creature_upkeep = self.upkeep_mod,
                                 ufood = self.ufood, usight = self.usight, uspeed = self.uspeed, udmg = self.udmg,
                                 ubiome = self.ubiome, umode = self.umode)
                # set variables
                self.total_creatures_generated += 1
                self.creature.max_food = random.randint(40, 200)
                self.creature.speed_mod = random.randint(10, 200) / 100
                self.creature.biome_speed_mod = [random.randint(10, 200) / 100 for i in range(3)]
                self.creature.biome_affinity = [random.randint(0,100) / 100 for i in range(3)]
                self.creature.fullness = self.creature.max_food / 2
                self.creature.sight_mod = random.randint(50, 200) / 100
                self.creature.aggro = random.randint(0,100)/100
                self.creature.damage_mod = random.randint(0,100)/100

                # random color
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)

                self.creature._set_color([r, g, b])

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

                #get biome
                i = int((self.creature.center_x + 50) / 100)
                if (i < 0):
                    i = 0
                if (i > 24):
                    i = 24
                j = int((self.creature.center_y + 50) / 100)
                if (j < 0):
                    j = 0
                if (j > 24):
                    j = 24
                self.creature.cur_biome = self.biome_list[i][j].biome
                self.creature.set_upkeep()
                self.creature_list.append(self.creature)

        # update animation
        self.creature_list.update_animation()

        # change view
        if(self.hold_up==True and self.view_up<WORLD_LENGTH+700):
            self.view_up += VIEW_SPEED
            self.view_down += VIEW_SPEED
        if(self.hold_down==True and self.view_down>-700):
            self.view_up -= VIEW_SPEED
            self.view_down -= VIEW_SPEED
        if(self.hold_left==True and self.view_left>-1000):
            self.view_left -= VIEW_SPEED
            self.view_right -= VIEW_SPEED
        if(self.hold_right==True and self.view_right<WORLD_LENGTH+1000):
            self.view_left += VIEW_SPEED
            self.view_right += VIEW_SPEED
        #zoom out
        if(self.view_zoom=="zoom_out" and self.view_up-self.view_down<=WORLD_LENGTH*1.3):
            self.view_up += ZOOM_SPEED_Y
            self.view_down -= ZOOM_SPEED_Y
            self.view_right += ZOOM_SPEED_X
            self.view_left -=ZOOM_SPEED_X
        #zoom in
        if (self.view_zoom == "zoom_in" and self.view_up-self.view_down>=500):
            self.view_up -= ZOOM_SPEED_Y
            self.view_down += ZOOM_SPEED_Y
            self.view_right -= ZOOM_SPEED_X
            self.view_left += ZOOM_SPEED_X
        arcade.set_viewport(self.view_left,self.view_right, self.view_down, self.view_up)

    def spawn_food(self):
        """
        Spawns food based on spawn rates and adds food to food list

        """
        # do food spawn for each biome sqaure
        for biome in self.biome_sprite_list:
            # random food chance
            if(biome.food_spawn == 0):
                x = 0
            else:
                x = random.randint(1,math.floor((FOOD_SPAWN_RATE*BIOME_SIZE*BIOME_SIZE)/biome.food_spawn))
            # if food will spawn
            if(x==1):
                # init
                self.food=Food(self.food_texture)

                #make sure no overlap
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


    def breed(self, creature):
        """
        Function breeds the passed creature and spawns a mutated copy of the creature at a nearby spot
        :param creature:
        """

        # update simulation params
        creature.reward = creature.max_food/2
        creature.num_reproduced+=1
        message_center.append("Creature " + str(creature.id) + " has reproduced (" + str(creature.num_reproduced) + ").")
        self.total_creatures_generated += 1

        # spawn in creature
        self.creature = Creature(self.total_creatures_generated,self.creature_textures,creature_upkeep = self.upkeep_mod,
                                 ufood = self.ufood, usight = self.usight, uspeed = self.uspeed, udmg = self.udmg,
                                 ubiome = self.ubiome, umode = self.umode)
        self.creature.max_food = min(200,max(40,creature.max_food * 1.0 + float((random.randint(-50, 50) * MUTATION_RATE/200))))
        self.creature.biome_speed_mod[0] = min(2.0,max(0.1,creature.biome_speed_mod[0] * 1.0 + float((random.randint(-50, 50)  * MUTATION_RATE/ 1000))))
        self.creature.biome_speed_mod[1] = min(2.0,max(0.1,creature.biome_speed_mod[1] * 1.0 + float((random.randint(-50, 50)  * MUTATION_RATE/ 1000))))
        self.creature.biome_speed_mod[2] = min(2.0,max(0.1,creature.biome_speed_mod[2] * 1.0 + float((random.randint(-50, 50)  * MUTATION_RATE/ 1000))))
        self.creature.sight_mod = min(2.0,max(0.5,creature.sight_mod * 1.0 + float((random.randint(-50, 50)  * MUTATION_RATE/ 1000))))
        self.creature.speed_mod = min(2.0,max(0.1,creature.speed_mod * 1.0 + float((random.randint(-50, 50)  * MUTATION_RATE/ 1000))))
        self.creature.biome_affinity[0] = min(1.0,max(0,creature.biome_affinity[0] * 1.0 + float((random.randint(-50, 50)  * MUTATION_RATE/ 2000))))
        self.creature.biome_affinity[1] = min(1.0,max(0,creature.biome_affinity[1] * 1.0 + float((random.randint(-50, 50)  * MUTATION_RATE/ 2000))))
        self.creature.biome_affinity[2] = min(1.0,max(0,creature.biome_affinity[2] * 1.0 + float((random.randint(-50, 50)  * MUTATION_RATE/ 2000))))
        self.creature.fullness = self.creature.max_food/2
        self.creature.aggro = min(1.0, max(0, creature.aggro * 1.0 + float((random.randint(-50, 50) * MUTATION_RATE / 2000))))
        self.creature.damage_mod = min(1.0, max(0, creature.damage_mod * 1.0 + float((random.randint(-50, 50) * MUTATION_RATE / 2000))))

        # add parent and child to eachother's ignore list
        self.creature.atk_ignore_list.append(creature)
        creature.atk_ignore_list.append(self.creature)
        if(len(creature.atk_ignore_list) > 10):
            creature.atk_ignore_list.pop(0)

        # set color to parent color-------
        color_tup = creature._get_color()
        color = [color_tup[0], color_tup[1], color_tup[2]]
        color[0] = min(255,max(0,math.floor(color[0] * 1.0 + float((random.randint(-50, 50) * MUTATION_RATE / 1000)))))
        color[1] = min(255,max(0,math.floor(color[1] * 1.0 + float((random.randint(-50, 50) * MUTATION_RATE / 1000)))))
        color[1] = min(255,max(0,math.floor(color[1] * 1.0 + float((random.randint(-50, 50) * MUTATION_RATE / 1000)))))
        self.creature._set_color((color[0], color[1], color[2]))

        # check overlap
        can_spawn = False
        failed = False
        while (can_spawn == False):
            creature_x = creature.center_x + random.randint(-100,100)
            creature_y = creature.center_y + random.randint(-100,100)
            for c in self.creature_list:
                if (
                        c.center_x - CREATURE_WIDTH <= creature_x and creature_x <= c.center_x + CREATURE_WIDTH
                        and c.center_y - CREATURE_HEIGHT <= creature_y and creature_y <= c.center_y + CREATURE_HEIGHT):
                    failed = True
            if (failed == False):
                can_spawn = True
            failed = False
        self.creature.center_x = creature_x
        self.creature.center_y = creature_y

        # get biome
        i = int((self.creature.center_x + 50) / 100)
        if (i < 0):
            i = 0
        if (i > 24):
            i = 24
        j = int((self.creature.center_y + 50) / 100)
        if (j < 0):
            j = 0
        if (j > 24):
            j = 24
        self.creature.cur_biome = self.biome_list[i][j].biome
        self.creature.set_upkeep()
        self.creature_list.append(self.creature)
        self.creature_list.update()
        self.creature_list.update_animation()
        if REPRODUCTION_RATE < 1:
            creature.fullness = creature.max_food * REPRODUCTION_RATE
        else:
            creature.fullness = creature.max_food * 0.999

    def get_biomes(self, creature, x, y):
        """
        gets the biomes near a creature at position x,y
        :param creature:
        :param x:
        :param y:
        :return: 2d array of nearby biome type index
        """
        #2d array for biome type index
        biomes = [[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]]
        # get y index of biome in the biome list
        j = int((y + 50) / 100)
        # manually set edge cases for border
        if (j <= 0):
            j = 0
            biomes[0][0] = 3
            biomes[1][0] = 3
            biomes[2][0] = 3
        if (j >= 24):
            j = 24
            biomes[0][2] = 3
            biomes[1][2] = 3
            biomes[2][2] = 3
        # get x index of biome in the biome list
        i = int((x + 50) / 100)
        # manually set edge cases for border
        if (i <= 0):
            i = 0
            biomes[0][0] = 3
            biomes[0][1] = 3
            biomes[0][2] = 3
        if (i >= 24):
            i = 24
            biomes[2][0] = 3
            biomes[2][1] = 3
            biomes[2][2] = 3
        # set currect biome
        if creature != None:
            creature.cur_biome = self.biome_list[i][j].biome
        # populate the array to be returned
        for k in range(len(biomes)):
            for p in range(len(biomes[0])):
                if biomes[k][p] == -1:
                    biomes[k][p] = self.biome_list[i+k-1][j+p-1].biome
        # return the biomes
        return (biomes)


    def get_inputs(self, creature):
        """
        Function not used in final implementation was for machine learning
        Function gets all the inputs needed for machine learning
        :param creature:
        :return: input array
        """
        food_tuple = self.get_nearest_sprite(creature, self.food_list)
        inputs = []
        if (food_tuple):
            inputs.append(1.0)
            inputs.append((creature.center_x - food_tuple[0].center_x)/400)
            inputs.append((creature.center_y - food_tuple[0].center_y)/400)
            inputs.append(food_tuple[1]/400)
        else:
            for i in range(4):
                inputs.append(0.0)
        food = None
        if (len(self.food_list)>0):
            test = 0
            for f in self.food_list:
                if creature.target == f:
                    test = 1
            if test != 1:
                i = random.randint(0, len(self.food_list) - 1)
                food = self.food_list[i]
                creature.target = food
            else:
                food = creature.target
        if food:
            inputs.append(1.0)
            inputs.append((creature.center_x - food.center_x)/2500)
            inputs.append((creature.center_y - food.center_y)/2500)
            inputs.append(arcade.get_distance_between_sprites(creature, food)/2500)
        else:
            for i in range(4):
                inputs.append(0.0)
        creature_tuple = self.get_nearest_sprite(creature,self.creature_list)
        if (creature_tuple):
            inputs.append(1.0)
            inputs.append((creature.center_x - creature_tuple[0].center_x)/400)
            inputs.append((creature.center_y - creature_tuple[0].center_y)/400)
            inputs.append(creature_tuple[1]/400)
        else:
            for i in range(4):
                inputs.append(0.0)
        biomes = [[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]]
        j = int((creature.center_y + 50) / 100)
        if (j <= 0):
            j = 0
            biomes[0][0] = 3
            biomes[1][0] = 3
            biomes[2][0] = 3
        if (j >= 24):
            j = 24
            biomes[0][2] = 3
            biomes[1][2] = 3
            biomes[2][2] = 3
        i = int((creature.center_x + 50) / 100)
        if (i <= 0):
            i = 0
            biomes[0][0] = 3
            biomes[0][1] = 3
            biomes[0][2] = 3
        if (i >= 24):
            i = 24
            biomes[2][0] = 3
            biomes[2][1] = 3
            biomes[2][2] = 3
        creature.cur_biome = self.biome_list[i][j].biome
        for k in range(len(biomes)):
            for p in range(len(biomes[0])):
                if biomes[k][p] == -1:
                    biomes[k][p] = self.biome_list[i+k-1][j+p-1].biome
                inputs.append(float(biomes[k][p])/3.0)

        inputs.append((creature.center_x - self.biome_list[i][j].center_x)/50)
        inputs.append((creature.center_y - self.biome_list[i][j].center_y)/50)
        inputs.append(arcade.get_distance_between_sprites(creature,self.biome_list[i][j])/50)
        for b in creature.biome_speed_mod:
            inputs.append(b)
        inputs.append(creature.speed_mod/2)
        inputs.append(creature.sight_mod/2)
        inputs.append(creature.max_food/200)
        inputs.append(creature.fullness/200)
        inputs.append(creature.fullness/creature.max_food)
        #print(inputs)
        return (inputs)


    def do_action(self, creature, action):
        """
        Function not used in final implementation
        Preforms one of 9 actions (one for each direction and a stop action)
        :param creature:
        :param action:
        :return:
        """
        if action == 0:
            creature.change_y = MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
        elif action == 1:
            creature.change_y = MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
            creature.change_x = MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
        elif action == 2:
            creature.change_x = MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
        elif action == 3:
            creature.change_y = -1 * MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
            creature.change_x = MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
        elif action == 4:
            creature.change_y = -1 * MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
        elif action == 5:
            creature.change_y = -1 * MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
            creature.change_x = -1 * MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
        elif action == 6:
            creature.change_x = -1 * MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
        elif action == 7:
            creature.change_y = MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
            creature.change_x = -1 * MOVEMENT_SPEED * creature.speed_mod * creature.biome_speed_mod[creature.cur_biome]
        elif action == 8:
            creature.change_y = 0
            creature.change_x = 0

        if creature.center_x > BIOME_SIZE * BIOME_LENGTH - 50:
            creature.center_x = BIOME_SIZE * BIOME_LENGTH - 50
        elif creature.center_x < -50:
            creature.center_x = -50
        if creature.center_y > BIOME_SIZE * BIOME_LENGTH - 50:
            creature.center_y = BIOME_SIZE * BIOME_LENGTH - 50
        elif creature.center_y < -50:
            creature.center_y = -50

        eat_list = arcade.check_for_collision_with_list(creature, self.food_list)
        for food in eat_list:
            creature.feed(food.food)
            food.kill()
        # breed if needed
        if (creature.fullness >= creature.max_food * REPRODUCTION_RATE):
            self.breed(creature)

    def wander(self, creature):
        """
        Preforms a basic wander algorithm for the creature
        Has a biome affinity applied as well
        Also selects targets as needed
        :param creature:
        :return:
        """
        speed = MOVEMENT_SPEED * creature.get_speed() #speed of creature

        # apply biome affinity
        # get biomes
        biomes = self.get_biomes(creature, creature.center_x, creature.center_y)
        # vector array showing the direction away from each biome returned from get_biomes function
        biomes_direct = [[[1,1],[1,0],[1,-1]],[[0,1],[0,0],[0,-1]],[[-1,1],[-1,0],[-1,-1]]]
        #for each biome in the array
        for i in range(3):
            for j in range(3):
                # apply a velocity change away from the biome
                # if biome is the border apply a negative affinity
                if biomes[i][j] == 3:
                    creature.change_y = creature.change_y + biomes_direct[i][j][1] * (1.3-creature.biome_affinity[creature.cur_biome]) * 0.2 * MOVEMENT_SPEED * creature.get_speed()
                    creature.change_x = creature.change_x + biomes_direct[i][j][0] * (1.3-creature.biome_affinity[creature.cur_biome]) * 0.2 * MOVEMENT_SPEED * creature.get_speed()
                else:
                    creature.change_y = creature.change_y + biomes_direct[i][j][1] * (1-creature.biome_affinity[biomes[i][j]]) * 0.2 * MOVEMENT_SPEED * creature.get_speed()
                    creature.change_x = creature.change_x + biomes_direct[i][j][0] * (1-creature.biome_affinity[biomes[i][j]]) * 0.2 * MOVEMENT_SPEED * creature.get_speed()

        # virtual circle used for wander algorithm
        circleCenter = [creature.change_x,creature.change_y]
        circleCenter = np.array(circleCenter)
        cnorm = np.linalg.norm(circleCenter)
        if cnorm == 0:
            cnorm = 1
        circleCenter = circleCenter/cnorm
        circleCenter = circleCenter * 2.5 * speed

        # displacement used for wander algorithm
        displacement = [0, 1]
        displacement = np.array(displacement)
        dnorm = np.linalg.norm(displacement)
        if dnorm == 0:
            dnorm = 1
        displacement = displacement/dnorm
        displacement = speed * displacement

        # set displacement based off the creature wander angle
        dnorm = np.linalg.norm(displacement)
        displacement[0] = math.cos(creature.wander_angle) * dnorm
        displacement[1] = math.sin(creature.wander_angle) * dnorm

        #update the wander angle
        creature.wander_angle = creature.wander_angle + ((random.random() * math.radians(45 * speed)) - (math.radians(45 * speed) * 0.5))
        creature.wander_angle = math.radians(math.degrees(creature.wander_angle) % 360)
        creature.wander_angle = math.radians(math.degrees(creature.wander_angle) % 360)

        #get the wander force
        wander_force = circleCenter + displacement

        # set the velocity using the wander force
        wfnorm = np.linalg.norm(wander_force)
        if wfnorm > 0.5 * speed:
            wander_force = wander_force*5/wfnorm
        velocity = np.array([creature.change_x,creature.change_y])
        velocity = velocity + wander_force
        vnorm = np.linalg.norm(velocity)
        if vnorm > speed:
            velocity = velocity*MOVEMENT_SPEED * creature.get_speed()/vnorm

        #update creature vector
        creature.change_x = velocity[0]
        creature.change_y = velocity[1]

        # Code to reduce time spent on edge
        if creature.center_x > BIOME_SIZE * BIOME_LENGTH - 50:
            creature.center_x = BIOME_SIZE * BIOME_LENGTH - 50

            if creature.change_y > 0:
                creature.wander_angle += math.radians(20)
            else:
                creature.wander_angle -= math.radians(20)
        elif creature.center_x < -50:
            creature.center_x = -50
            if creature.change_y > 0:
                creature.wander_angle -= math.radians(20)
            else:
                creature.wander_angle += math.radians(20)
        if creature.center_y > BIOME_SIZE * BIOME_LENGTH - 50:
            creature.center_y = BIOME_SIZE * BIOME_LENGTH - 50
            if creature.change_x > 0:
                creature.wander_angle -= math.radians(20)
            else:
                creature.wander_angle += math.radians(20)
        elif creature.center_y < -50:
            creature.center_y = -50
            if creature.change_x > 0:
                creature.wander_angle += math.radians(20)
            else:
                creature.wander_angle -= math.radians(20)
                #print(creature.wander_angle)

        # food target selection
        target_tuple = self.get_nearest_sprite(creature,self.food_list)
        # if a target found
        if(target_tuple):
            target = target_tuple[0]
            dist = target_tuple[1]
            # if target in sight range
            if(target and dist <= CREATURE_SIGHT * creature.sight_mod and target != creature.target):
                ignore = False
                # check if in ignore list
                for t in creature.ignore_list:
                    if target == t:
                        creature.ignore_list.remove(t)
                        creature.ignore_list.append(t)
                        ignore = True
                # if not in ignore list
                if ignore == False:
                    # get biome
                    i = int((target.center_x + 50) / 100)
                    if (i < 0):
                        i = 0
                    if (i > 24):
                        i = 24
                    j = int((target.center_y + 50) / 100)
                    if (j < 0):
                        j = 0
                    if (j > 24):
                        j = 24
                    biome = [self.biome_list[i][j]]
                    b = biome[0].biome
                    # use affinity to decide if it should ignore
                    if(creature.biome_affinity[b] < float(random.randint(10,85))/100):
                        creature.ignore_list.append(target)
                        if len(creature.ignore_list) > 5:
                            creature.ignore_list.pop(0)
                    else:
                        creature.target = target

        # check if creature can eat a food
        eat_list = arcade.check_for_collision_with_list(creature, self.food_list)
        for food in eat_list:
            creature.feed(food.food)
            food.kill()
        # breed if needed
        if (creature.fullness >= creature.max_food):
            self.breed(creature)

        # get attack targets
        target_tuple = self.get_nearest_sprite(creature,self.creature_list)
        # if possible target exits
        if(target_tuple):
            target = target_tuple[0]
            dist = target_tuple[1]
            # if in sight range and not already target
            if(target and dist <= CREATURE_SIGHT * creature.sight_mod and creature.attack_targ != target):
                ignore = False
                # check if in ignore list
                for t in creature.atk_ignore_list:
                    if target == t:
                        creature.atk_ignore_list.remove(t)
                        creature.atk_ignore_list.append(t)
                        ignore = True
                # if not in ignore list
                if ignore == False:
                    # get biome
                    i = int((target.center_x + 50) / 100)
                    if (i < 0):
                        i = 0
                    if (i > 24):
                        i = 24
                    j = int((target.center_y + 50) / 100)
                    if (j < 0):
                        j = 0
                    if (j > 24):
                        j = 24
                    biome = [self.biome_list[i][j]]
                    b = biome[0].biome
                    dm = max(0.01, creature.damage_mod)
                    hp = max(0.01, creature.hp)
                    # add to ignore list or target based on creature aggro and other stats
                    if(creature.biome_affinity[b] < float(random.randint(10,85))/100 or creature.aggro < target.hp/hp * target.damage_mod/dm * float(random.randint(0,200)/100)):
                        creature.atk_ignore_list.append(target)
                        if len(creature.atk_ignore_list) > 10:
                            creature.atk_ignore_list.pop(0)
                    else:
                        creature.attack_targ = target
                        target.def_targ = creature
                        creature.target = None


    def defend_creature(self, creature):
        """
        Function either has creature run away or start attacking back based on aggro and other stats
        :param creature:
        :return:
        """
        # make sure attacking creature still exists
        test = 0
        for c in self.creature_list:
            if creature.def_targ == c:
                test = 1
        if test != 1:
            creature.def_targ = None
            creature.running = False
            return

        # make sure creature has a defence target
        if (creature.def_targ == None):
            creature.running = False
            return

        # make sure defence target is attacking this creature
        if (creature.def_targ.attack_targ != creature):
            creature.def_targ = None
            creature.running = False
            return

        # calculate run or attack based off creature stats
        targ = creature.def_targ
        dm = max(0.01,targ.damage_mod)
        hp = max(0.01,targ.hp)
        if creature.aggro > creature.damage_mod/dm * creature.hp/hp * random.randint(0,100) / 100 and creature.running == False:
            creature.attack_targ = creature.def_targ
            creature.def_targ = None
            creature.running = False
            return
        # if decide run then set the running = True so it will keep running
        else:
            creature.running = True


        # if creature is running then move way from target
        if creature.running == True:
            # get direction
            direct = self.get_target_direction(creature, creature.def_targ)

            # get biome for speed calc
            i = int((creature.center_x + 50) / 100)
            if (i < 0):
                i = 0
            if (i > 24):
                i = 24
            j = int((creature.center_y + 50) / 100)
            if (j < 0):
                j = 0
            if (j > 24):
                j = 24
            biome = [self.biome_list[i][j]]
            creature.cur_biome = biome[0].biome
            # move away from target
            creature.change_x = MOVEMENT_SPEED * creature.get_speed() * (-1) * direct[0]
            creature.change_y = MOVEMENT_SPEED * creature.get_speed() * (-1) * direct[1]

        # make sure doesn't exit map
        if creature.center_x > BIOME_SIZE * BIOME_LENGTH - 50:
            creature.center_x = BIOME_SIZE * BIOME_LENGTH - 50
        elif creature.center_x < -50:
            creature.center_x = -50
        if creature.center_y > BIOME_SIZE * BIOME_LENGTH - 50:
            creature.center_y = BIOME_SIZE * BIOME_LENGTH - 50
        elif creature.center_y < -50:
            creature.center_y = -50

        # check for any food the creature might pick up while running
        eat_list = arcade.check_for_collision_with_list(creature, self.food_list)
        for food in eat_list:
            if (creature.target == food):
                creature.target = None
                for c in self.creature_list:
                    if c.target == food:
                        c.target = None
            creature.feed(food.food)
            food.kill()
            if (creature.fullness >= creature.max_food ):
                self.breed(creature)

    def move_creature(self, creature):

        # get target incase a new food spawns
        target_tuple = self.get_nearest_sprite(creature,self.food_list)
        if(target_tuple):
            target = target_tuple[0]
            dist = target_tuple[1]
            # if target in sight then update target
            if(target and dist <= CREATURE_SIGHT * creature.sight_mod):
                creature.target = target
        # test to make sure target still exists
        test = 0
        for f in self.food_list:
            if creature.target == f:
                test = 1
        if test != 1:
            creature.target = None

        # if creature has a target do movement
        if(creature.target):
            # get direction
            direct = self.get_target_direction(creature, creature.target)

            # get biome
            i = int((creature.center_x + 50)/100)
            if(i<0):
                i=0
            if(i>24):
                i=24
            j = int((creature.center_y + 50)/100)
            if(j<0):
                j=0
            if(j>24):
                j=24
            biome = [self.biome_list[i][j]]
            creature.cur_biome = biome[0].biome
            #do movement
            creature.change_x = MOVEMENT_SPEED * creature.get_speed() * direct[0]
            creature.change_y = MOVEMENT_SPEED * creature.get_speed() * direct[1]

            # check for any food to eat
            eat_list = arcade.check_for_collision_with_list(creature, self.food_list)
            for food in eat_list:
                if(creature.target == food):
                    creature.target = None
                    for c in self.creature_list:
                        if c.target == food:
                            c.target = None
                creature.feed(food.food)
                food.kill()
                # breed if needed
                if(creature.fullness>=creature.max_food):
                    self.breed(creature)


    def attack_creature(self, creature):
        # make sure target still exists
        test = 0
        for c in self.creature_list:
            if creature.attack_targ == c:
                test = 1
        if test != 1:
           # if creature.attack_targ.def_targ == creature:
           #     creature.attack_targ.def_targ = None
           # if creature.attack_targ.attack_targ == creature:
           #     creature.def_targ = creature.
           #remove attack target
            creature.attack_targ = None
            creature.boredom = 0
           # see if there is a food target nearby since no longer attacking
            target_tuple = self.get_nearest_sprite(creature, self.food_list)
            if (target_tuple):
                target = target_tuple[0]
                dist = target_tuple[1]
                if (target and dist <= CREATURE_SIGHT * creature.sight_mod):
                    creature.target = target
            return

        # get distance and chase value
        dist = arcade.get_distance_between_sprites(creature,creature.attack_targ)
        chase = creature.aggro * creature.biome_affinity[creature.attack_targ.cur_biome]
        # if target outside of set distance and chase lower than random value then remove creature from target
        if (chase < random.randint(0,50)/100 and dist > CREATURE_WIDTH + 10) or creature.attack_targ.state == "dying":
            if creature.attack_targ.def_targ == creature:
                creature.attack_targ.def_targ = None
                creature.attack_targ.running = False
            if creature.attack_targ.attack_targ == creature:
                creature.def_targ = creature.attack_targ
            creature.attack_targ = None
            creature.boredom = 0
            return
        # bordom value to prevent long chases
        creature.boredom = creature.boredom + 1
        # if bordom too high then remove target
        if creature.boredom > 35:
            if creature.attack_targ.def_targ == creature:
                creature.attack_targ.def_targ = None
                creature.attack_targ.running = False
            if creature.attack_targ.attack_targ == creature:
                creature.def_targ = creature.attack_targ
            creature.attack_targ = None
            creature.boredom = 0
            return
        # if too far out of sight range then stop chasing
        if dist > CREATURE_SIGHT * creature.sight_mod * 1.3:
            if creature.attack_targ.def_targ == creature:
                creature.attack_targ.def_targ = None
                creature.attack_targ.running = False
            if creature.attack_targ.attack_targ == creature:
                creature.def_targ = creature.attack_targ
            creature.attack_targ = None
            creature.boredom = 0
            return

        if(creature.attack_targ == None):
            creature.boredom = 0
            return

        # if inside attack range
        if dist < CREATURE_WIDTH + 10:
            creature.state = "attacking"
            # deal damage
            if creature.attack_targ.hp > 0:
                creature.attack_targ.hp = creature.attack_targ.hp - 1.5 * creature.damage_mod
                # if creature dies feed off creature
                if creature.attack_targ.hp < 0:
                    creature.feed(creature.attack_targ.max_food/3)
                    creature.num_kills = creature.num_kills + 1
                    message_center.append("Creature "+str(creature.id)+" has killed creature "+ str(creature.attack_targ.id)+" ("+str(creature.num_kills)+").")
                    creature.attack_targ.no_food = True
                    # breed if needed
                    if (creature.fullness >= creature.max_food):
                        self.breed(creature)
            creature.boredom = 0

        # if not in attack range move to target
        else:
            # get direction
            direct = self.get_target_direction(creature, creature.attack_targ)

            #get biome
            i = int((creature.center_x + 50)/100)
            if(i<0):
                i=0
            if(i>24):
                i=24
            j = int((creature.center_y + 50)/100)
            if(j<0):
                j=0
            if(j>24):
                j=24
            biome = [self.biome_list[i][j]]
            creature.cur_biome = biome[0].biome
            # do movement
            creature.change_x = MOVEMENT_SPEED * creature.get_speed() * direct[0]
            creature.change_y = MOVEMENT_SPEED * creature.get_speed() * direct[1]
        # make sure in bounds
        if creature.center_x > BIOME_SIZE * BIOME_LENGTH - 50:
            creature.center_x = BIOME_SIZE * BIOME_LENGTH - 50
        elif creature.center_x < -50:
            creature.center_x = -50
        if creature.center_y > BIOME_SIZE * BIOME_LENGTH - 50:
            creature.center_y = BIOME_SIZE * BIOME_LENGTH - 50
        elif creature.center_y < -50:
            creature.center_y = -50
        # check to see if ate any food
        eat_list = arcade.check_for_collision_with_list(creature, self.food_list)
        for food in eat_list:
            if(creature.target == food):
                creature.target = None
                for c in self.creature_list:
                    if c.target == food:
                        c.target = None
            creature.feed(food.food)
            food.kill()
            if(creature.fullness>=creature.max_food):
                self.breed(creature)





    def get_target_direction(self, creature: arcade.Sprite, target: arcade.Sprite):
        """
        Get direction vector to target sprite
        :param creature:
        :param target:
        :return: direction vector
        """
        x_dist = creature.center_x - target.center_x
        y_dist = creature.center_y - target.center_y
        return [numpy.sign(x_dist)*(-1), numpy.sign(y_dist)*(-1)]



    def get_nearest_sprite(self, creature, list):
        """
        rewrite of aracde version that takes into acount sight to limit number of distances checked
        :param creature:
        :param list:
        :return:
        """
        if len(list) == 0:
            return None
        indecies = []
        sight = CREATURE_SIGHT*creature.sight_mod
        for i in range(0, len(list)):
            if abs(creature.center_x - list[i].center_x) <= sight and abs(creature.center_y - list[i].center_y) <= sight:
                indecies.append(i)
        min_pos = -1
        min_distance = 99999
        for i in indecies:
            if(list[i]!=creature):

                distance = arcade.get_distance_between_sprites(creature, list[i])
                if distance < min_distance:
                    min_pos = i
                    min_distance = distance
        if min_pos == -1:
            return None
        return (list[min_pos],min_distance)


    def display_simulation_controls(self):
        """
        displays the simulation controls
        :return:
        """
        self.update_font_size()
        top_margin = self.font_size * 14
        scale=1
        if self.hide_ui==False:
            #display controls
            #box
            arcade.draw_rectangle_filled(center_x=self.view_left + self.font_size * 6,
                                         center_y=self.view_up - (self.font_size * 7) - top_margin,
                                         width=self.font_size * 19,
                                         height=self.font_size * 15,
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
            arcade.draw_text("Menu: ESC", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Hide Controls: H", self.view_left + (self.font_size),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)


    def display_message_center(self):
        """
        displays the message center
        :return:
        """
        global message_center
        scaling=0

        #font size
        self.update_font_size()
        # draw white box around message center
        arcade.draw_rectangle_filled(center_x=self.view_left+20,
                                     center_y=self.view_down,
                                     width=self.font_size*43,
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
        arcade.draw_text("Sim Cycles: " + str(self.sim_time), self.view_right - self.font_size * 12,
                         self.view_down + self.font_size * 1.5 * scaling, arcade.color.BLACK, self.font_size)
        scaling += 1
        arcade.draw_text("Total Deaths: " + str(self.total_creatures_generated - len(self.creature_list)),
                         self.view_right - self.font_size * 12,
                         self.view_down + self.font_size * 1.5 * scaling, arcade.color.BLACK, self.font_size)
        scaling += 1
        arcade.draw_text("Population: "+str(len(self.creature_list)), self.view_right-self.font_size*12, self.view_down+self.font_size*1.5*scaling, arcade.color.BLACK, self.font_size)
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
        """
        displays creature stats
        :return:
        """
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
                                         center_y=self.view_up-(self.font_size*14.5)-top_margin,
                                         width=self.font_size * 14,
                                         height=self.font_size * 33,
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

            arcade.draw_text("Speed: " + str(round(creature.speed_mod,2)), self.view_right - (self.font_size * 12),

                             self.view_up - (self.font_size*1.5 * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("Plain Speed: " + str(round(creature.biome_speed_mod[0], 2)),
                             self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Mountain Speed: " + str(round(creature.biome_speed_mod[1], 2)),
                             self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Desert Speed: " + str(round(creature.biome_speed_mod[2], 2)),
                             self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Plain Affinity: " + str(round(creature.biome_affinity[0], 2)),
                             self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Mountain Affinity: " + str(round(creature.biome_affinity[1], 2)),
                             self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Desert Affinity: " + str(round(creature.biome_affinity[2], 2)),
                             self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size * 1.5 * scale) - top_margin, arcade.color.BLACK,
                             self.font_size)
            scale += 1
            arcade.draw_text("Food: " + str(int(round(creature.fullness,0)))+"/"+str(int(round(creature.max_food,0))), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5 * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("Hp: " + str(int(round(creature.hp,0)))+"/"+str(int(round(creature.max_hp,0))), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5 * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("Damage Mod: " + str(round(creature.damage_mod,3)), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5  * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("Aggro: " + str(round(creature.aggro,3)), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5  * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("Sight: " + str(round(creature.sight_mod,3)), self.view_right - (self.font_size * 12),
                             self.view_up - (self.font_size*1.5  * scale)-top_margin, arcade.color.BLACK, self.font_size)
            scale += 1
            arcade.draw_text("Food Upkeep: " + str(float(round(creature.food_upkeep*100, 3))), self.view_right - (self.font_size * 12),

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



    #loads two textures on reverse and on normal for left and right animations
    def load_texture_pair(self, filename):
        """
        Load a texture pair, with the second being a mirror image.
        """
        return [
            arcade.load_texture(filename),
            arcade.load_texture(filename, flipped_horizontally=True)
        ]

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
        Controls camera movement
        """
        # camera movement
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
        # zoom
        if (key == arcade.key.MINUS or key == arcade.key.EQUAL):
            self.view_zoom="none"
        # movement
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
            if self.simulation_speed>0:
                self.simulation_speed=0
                for c in self.creature_list:
                    if(c.state!="dying"):
                        c.state="idle"
            else:
                self.simulation_speed=1
                for c in self.creature_list:
                    if(c.state!="dying"):
                        c.state="walking"
        # other controls
        elif key == arcade.key.L:
            if self.simulation_speed<100:
                self.simulation_speed+=1
                for c in self.creature_list:
                    if(c.state!="dying"):
                        c.state="walking"
        elif key == arcade.key.J:
            if self.simulation_speed>1:
                self.simulation_speed-=1
        elif key == arcade.key.H:
            if self.hide_ui==False:
                self.hide_ui=True
            else:
                self.hide_ui=False
        elif key == arcade.key.ESCAPE:
            global window
            menu_view = MainMenuView()
            window.show_view(menu_view)



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
        Used to select creature
        """

        #select creatues whos stats to show
        for i in range(0, len(self.creature_list)):
            # click on creature
            #adjust x and y for view port
            x_adjusted=(x/SCREEN_WIDTH)*(self.view_right-self.view_left)+self.view_left
            y_adjusted=(y/SCREEN_HEIGHT)*(self.view_up-self.view_down)+self.view_down
            if (self.creature_list[i].center_x-CREATURE_WIDTH <= x_adjusted <= self.creature_list[i].center_x+CREATURE_WIDTH
                    and self.creature_list[i].center_y - CREATURE_HEIGHT <= y_adjusted <= self.creature_list[i].center_y + CREATURE_HEIGHT):
                self.creature_display_stats_index = i
                self.new_creature_index=True

# main menu
class MainMenuView(arcade.View):
    def __init__(self):
        """ Set up this view """
        super().__init__()
        # reset viewport
        arcade.set_viewport(0, 1280, 0, 720)

        self.ui_manager = UIManager()

    def on_show(self):
        arcade.set_background_color(arcade.color.BRIGHT_NAVY_BLUE)
        self.setup()

    def setup(self):
        self.ui_manager.purge_ui_elements()
        new = NewFlatButton('New Simulation', center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT / 1.7, width=250, height=50)
        new.set_style_attrs(
            font_color=arcade.color.WHITE,
            font_color_hover=arcade.color.WHITE,
            font_color_press=arcade.color.WHITE,
            bg_color=(105, 105, 105),
            bg_color_hover=(128,128,128),
            bg_color_press=(0,0,0),
            border_color=(0,0,0),
            border_color_hover=arcade.color.BLACK,
            border_color_press=arcade.color.BLACK
        )
        self.ui_manager.add_ui_element(new)
        load = LoadFlatButton('Default Simulation', center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT / 3, width=250,
                           height=50)
        load.set_style_attrs(
            font_color=arcade.color.WHITE,
            font_color_hover=arcade.color.WHITE,
            font_color_press=arcade.color.WHITE,
            bg_color=(105, 105, 105),
            bg_color_hover=(128, 128, 128),
            bg_color_press=(0, 0, 0),
            border_color=(0, 0, 0),
            border_color_hover=arcade.color.BLACK,
            border_color_press=arcade.color.BLACK
        )
        self.ui_manager.add_ui_element(load)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("BIJG Learning: Evolution Simulation", SCREEN_WIDTH/2, SCREEN_HEIGHT/1.3,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

#handles on click for new
class NewFlatButton(arcade.gui.UIFlatButton):

    #go to modifer page
    def on_click(self):
        global window
        #for starting game window
        # game_view = MyGame()
        # window.show_view(game_view)
        modification_view=ModificationMenuView()
        window.show_view(modification_view)

#handles on click for load
class LoadFlatButton(arcade.gui.UIFlatButton):
    """
    To capture a button click, subclass the button and override on_click.
    """
    def on_click(self):
        """ Called when user lets off button """
        global window
        game_view = MyGame()
        window.show_view(game_view)


#modification view
class ModificationMenuView(arcade.View):
    def __init__(self):
        """ Set up this view """
        super().__init__()

        self.ui_manager = UIManager()

    def on_show(self):
        arcade.set_background_color(arcade.color.BRIGHT_NAVY_BLUE)
        self.setup()

    def setup(self):
        global population_input
        global mutation_input
        global reproduction_input
        global food_input
        global seed_input
        global atk_input
        global umode_input
        global upkeep_input
        global speed_input
        global biome_input
        global ufood_input
        global dmg_input
        global sight_input
        global biome0_input
        global biome1_input
        global biome2_input

        self.ui_manager.purge_ui_elements()

        #population input
        population_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH/3,
            center_y=SCREEN_HEIGHT/1.3,
            width=175
        )
        population_input.text = '75'
        population_input.cursor_index = len(population_input.text)
        self.ui_manager.add_ui_element(population_input)

        # mutation input
        mutation_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 3 ,
            center_y=SCREEN_HEIGHT / 1.3 - 75,
            width=175
        )
        mutation_input.text = '1'
        mutation_input.cursor_index = len(mutation_input.text)
        self.ui_manager.add_ui_element(mutation_input)

        # reproduction input
        reproduction_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 3,
            center_y=SCREEN_HEIGHT / 1.3 - 150,
            width=175
        )
        reproduction_input.text = '.5'
        reproduction_input.cursor_index = len(reproduction_input.text)
        self.ui_manager.add_ui_element(reproduction_input)

        # food input
        food_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 3,
            center_y=SCREEN_HEIGHT / 1.3 - 225,
            width=175
        )
        food_input.text = '5'
        food_input.cursor_index = len(food_input.text)
        self.ui_manager.add_ui_element(food_input)


        # seed input
        seed_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 3,
            center_y=SCREEN_HEIGHT / 1.3 - 300,
            width=175
        )
        seed_input.text = '10'
        seed_input.cursor_index = len(seed_input.text)
        self.ui_manager.add_ui_element(seed_input)

        # attack on/off input
        atk_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 3,
            center_y=SCREEN_HEIGHT / 1.3 - 375,
            width=175
        )
        atk_input.text = 't'
        atk_input.cursor_index = len(atk_input.text)
        self.ui_manager.add_ui_element(atk_input)

        # upkeep mode
        umode_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 3,
            center_y=SCREEN_HEIGHT / 1.3 - 450,
            width=175
        )
        umode_input.text = '1'
        umode_input.cursor_index = len(umode_input.text)
        self.ui_manager.add_ui_element(umode_input)



        #upkeep modifier
        upkeep_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH/1.2,
            center_y=SCREEN_HEIGHT/1.3,
            width=175
        )
        upkeep_input.text = '5'
        upkeep_input.cursor_index = len(upkeep_input.text)
        self.ui_manager.add_ui_element(upkeep_input)

        # speed upkeep modifier
        speed_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 1.2 ,
            center_y=SCREEN_HEIGHT / 1.3 - 75,
            width=175
        )
        speed_input.text = '5'
        speed_input.cursor_index = len(speed_input.text)
        self.ui_manager.add_ui_element(speed_input)

        # biome speed upkeep modifier
        biome_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 1.2,
            center_y=SCREEN_HEIGHT / 1.3 - 150,
            width=175
        )
        biome_input.text = '5'
        biome_input.cursor_index = len(biome_input.text)
        self.ui_manager.add_ui_element(biome_input)

        # max food upkeep modifier
        ufood_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 1.2,
            center_y=SCREEN_HEIGHT / 1.3 - 225,
            width=175
        )
        ufood_input.text = '5'
        ufood_input.cursor_index = len(ufood_input.text)
        self.ui_manager.add_ui_element(ufood_input)


        # damage upkeep modifer
        dmg_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 1.2,
            center_y=SCREEN_HEIGHT / 1.3 - 300,
            width=175
        )
        dmg_input.text = '5'
        dmg_input.cursor_index = len(dmg_input.text)
        self.ui_manager.add_ui_element(dmg_input)

        # sight modifer
        sight_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 1.2,
            center_y=SCREEN_HEIGHT / 1.3 - 375,
            width=175
        )
        sight_input.text = '5'
        sight_input.cursor_index = len(sight_input.text)
        self.ui_manager.add_ui_element(sight_input)

        # plains food spawn mod
        biome0_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 1.2 - 60,
            center_y=SCREEN_HEIGHT / 1.3 - 450,
            width=50
        )
        biome0_input.text = '1.5'
        biome0_input.cursor_index = len(biome0_input.text)
        self.ui_manager.add_ui_element(biome0_input)

        # mountain food spawn mod
        biome1_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 1.2,
            center_y=SCREEN_HEIGHT / 1.3 - 450,
            width=50
        )
        biome1_input.text = '1.1'
        biome1_input.cursor_index = len(biome1_input.text)
        self.ui_manager.add_ui_element(biome1_input)

        # desert food spawn mod
        biome2_input = arcade.gui.UIInputBox(
            center_x=SCREEN_WIDTH / 1.2 + 60,
            center_y=SCREEN_HEIGHT / 1.3 - 450,
            width=50
        )
        biome2_input.text = '0.8'
        biome2_input.cursor_index = len(biome2_input.text)
        self.ui_manager.add_ui_element(biome2_input)


        new = StartFlatButton('Start Simulation', center_x=SCREEN_WIDTH / 2, center_y=50, width=250, height=50)
        new.set_style_attrs(
            font_color=arcade.color.WHITE,
            font_color_hover=arcade.color.WHITE,
            font_color_press=arcade.color.WHITE,
            bg_color=(105, 105, 105),
            bg_color_hover=(128,128,128),
            bg_color_press=(0,0,0),
            border_color=(0,0,0),
            border_color_hover=arcade.color.BLACK,
            border_color_press=arcade.color.BLACK
        )
        self.ui_manager.add_ui_element(new)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Simulation Modifications", SCREEN_WIDTH/2, SCREEN_HEIGHT/1.2,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

        arcade.draw_text("Starting Population:", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Integer between 0 and 200)", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Mutation Rate:", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 75,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Float between 0 and 10)", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 75 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Reproduction Cost:", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 -150,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Float between .1 and .9)", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 150 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")
        arcade.draw_text("Higher is less cost to reproduce", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 150 - 40,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Food Spawn Rate:", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 225,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Integer between 1 and 10)", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 225 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Seed:", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 300,
                         arcade.color.BLACK, font_size=18, anchor_x="center")

        arcade.draw_text("Combat Enabled:", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 375,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(t or f)", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 375 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Upkeep Mode:", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 450,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(1 or 2)", SCREEN_WIDTH / 7.5, SCREEN_HEIGHT / 1.3 - 450 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")




        arcade.draw_text("Upkeep Mod:", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(multiplies food upkeep)", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Speed Upkeep:", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 75,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Float between 0 and 10)", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 75 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Biome Upkeep:", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 -150,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Float between 0 and 10)", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 150 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Food Upkeep:", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 225,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Float between 0 and 10)", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 225 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Damage Upkeep:", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 300,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Float between 0 and 10)", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 300 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Sight Upkeep:", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 375,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Float between 0 and 10)", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 375 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")

        arcade.draw_text("Biome Food Rate:", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 450,
                         arcade.color.BLACK, font_size=18, anchor_x="center")
        arcade.draw_text("(Plains, Mountain, Desert)", SCREEN_WIDTH / 1.6, SCREEN_HEIGHT / 1.3 - 450 - 20,
                         arcade.color.BLACK, font_size=12, anchor_x="center")



    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

#handles on click for start
class StartFlatButton(arcade.gui.UIFlatButton):

    #go to game page
    def on_click(self):
        global CREATURES_TO_SPAWN
        global REPRODUCTION_RATE
        global FOOD_SPAWN_RATE
        global MUTATION_RATE
        global SEED

        #values from input field
        MessageBox = ctypes.windll.user32.MessageBoxW

        # error checking
        if(self.is_float(upkeep_input.text)==False):
            MessageBox(None, 'Upkeep input must be float', 'Error', 0)
        elif(self.is_float(dmg_input.text)==False):
            MessageBox(None, 'damage cost input must be float', 'Error', 0)
        elif(self.is_float(speed_input.text)==False):
            MessageBox(None, 'speed cost input must be float', 'Error', 0)
        elif(self.is_float(biome_input.text)==False):
            MessageBox(None, 'biome speed cost input must be float', 'Error', 0)
        elif(self.is_float(sight_input.text)==False):
            MessageBox(None, 'Sight cost input must be float', 'Error', 0)
        elif(self.is_float(ufood_input.text)==False):
            MessageBox(None, 'Food cost input must be float', 'Error', 0)
        elif(self.is_float(biome0_input.text)==False or self.is_float(biome1_input.text)==False or self.is_float(biome2_input.text)==False):
            MessageBox(None, 'Biome spawn input must be float', 'Error', 0)
        elif(umode_input.text != '1'  and umode_input.text != '2'):
            MessageBox(None, 'Upkeep mode input must be 1 or 2', 'Error', 0)
        elif(atk_input.text != 't' and atk_input.text != 'f'):
            MessageBox(None, 'Upkeep mode input must be t or f', 'Error', 0)
        #use is float instead of isnumberic for floats
        elif(seed_input.text.isnumeric()==False or population_input.text.isnumeric()==False or self.is_float(mutation_input.text)==False or self.is_float(reproduction_input.text)==False or food_input.text.isnumeric()==False ):
            MessageBox(None, 'Input must be numeric', 'Error', 0)
        else:
            population=int(population_input.text)
            reproduction=float(reproduction_input.text)
            mutation=float(mutation_input.text)
            food=int(food_input.text)
            seed=int(seed_input.text)
            #these can be adjusted
            if (population < 1 or population>200):
                MessageBox(None, 'Starting population out of bounds', 'Error', 0)
            elif (reproduction < .1 or reproduction>.9):
                MessageBox(None, 'Reproduction rate out of bounds', 'Error', 0)
            elif (food < 1 or food>10):
                MessageBox(None, 'Food spawn rate out of bounds', 'Error', 0)
            elif (mutation < 0 or mutation>10):
                MessageBox(None, 'Mutation rate out of bounds', 'Error', 0)
            elif (seed<0 or seed>999999):
                MessageBox(None, 'Seed out of bounds', 'Error', 0)
            else:
                CREATURES_TO_SPAWN=population
                REPRODUCTION_RATE=reproduction
                FOOD_SPAWN_RATE=food
                MUTATION_RATE=mutation
                SEED=seed
                global window
                game_view = MyGame(int(umode_input.text),atk_input.text,float(speed_input.text),float(biome_input.text),
                                   float(ufood_input.text),float(dmg_input.text),float(sight_input.text),
                                   [float(biome0_input.text),float(biome1_input.text),float(biome2_input.text)],
                                   float(upkeep_input.text))
                window.show_view(game_view)



    #used to check for floats
    def is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False




def main():
    """ Main method """
    global window
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    main_menu_view=MainMenuView()
    window.show_view(main_menu_view)
    arcade.run()


if __name__ == "__main__":
    main()

