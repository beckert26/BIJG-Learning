
#from main import *

import arcade
import math

CHARACTER_SCALING = 1.5
UPDATES_PER_FRAME=5
CREATURE_SIGHT = 150
CREATURE_UPKEEP = 100
CREATURE_DRAIN = 0.5

# Constants used to track if the player is facing left or right
RIGHT_FACING = 1
LEFT_FACING = 0

#pictures are 27x14
CREATURE_WIDTH=27*CHARACTER_SCALING
CREATURE_HEIGHT=14*CHARACTER_SCALING

FOODBAR_WIDTH = 25
FOODBAR_HEIGHT = 3
FOODBAR_OFFSET_Y = 3

HEALTHBAR_WIDTH = 25
HEALTHBAR_HEIGHT = 3
HEALTHBAR_OFFSET_Y = 9

FOOD_NUMBER_OFFSET_X = -10
FOOD_NUMBER_OFFSET_Y = -25

BIOME_SIZE=25
BIOME_LENGTH=100
WORLD_LENGTH=BIOME_LENGTH*BIOME_SIZE


#loads two textures on reverse and on normal for left and right animations
def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class Creature(arcade.Sprite):
    def __init__(self, id, textures):
        super().__init__()

        self.cur_texture=0
        self.no_food = False
        self.biome_speed_mod = [1.0,0.5,0.1,1.0]
        self.biome_affinity = [0.0,1.0,0.5]
        self.damage_mod = 1.0
        self.aggro = 0.5
        self.boredom = 0
        self.hp = 100
        self.max_hp = 100
        self.speed_mod = 1.0
        self.speed = 1.0
        self.target = None
        self.attack_targ = None
        self.def_targ = None
        self.running = False
        self.max_food = 100
        self.fullness = 50
        self.sight_mod = 1.0
        self.food_upkeep = 0
        self.prev_target = None
        self.prev_target2 = None
        self.id=id
        self.textures = textures
        self.cur_biome = 3
        self.bstate = []
        self.state_next = []
        self.reward = 0
        self.ignore_list = []
        self.atk_ignore_list = []

        self.wander_angle = math.radians(0)

        self.character_face_direction = RIGHT_FACING

        self.scale=CHARACTER_SCALING

        self.state="walking"

        #counting stats
        self.num_reproduced=0
        self.num_kills=0
        self.num_food_eaten=0;

        #load sprite textures for idle
        self.idle_texture_pair=textures[0]
        self.texture = textures[0][self.character_face_direction]

        #load sprite textures
        self.walking_textures = []
        self.attacking_textures = []
        self.damaged_textures = []
        self.dying_textures = []
        #walking
        for i in range(7):
            texture= self.textures[i+1]
            self.walking_textures.append(texture)

        #attacking
        for i in range(6):
            texture= self.textures[i+8]
            self.attacking_textures.append(texture)
        #dying
        for i in range(16):
            texture= self.textures[i+14]
            self.dying_textures.append(texture)

        #damaged
        for i in range(7):
            texture= self.textures[i+30]
            self.damaged_textures.append(texture)

        self.set_upkeep()


    def set_upkeep(self):
        self.max_hp = self.max_food
        self.hp = self.max_hp
        #self.speed = self.speed_mod * self.biome_speed_mod[self.cur_biome]
        average_biome_speed = (self.biome_speed_mod[0] + self.biome_speed_mod[1] + self.biome_speed_mod[2])/3
        self.food_upkeep = (((self.max_food/10) * (self.speed_mod*3) * (self.sight_mod*1.8) * max(0.5,self.damage_mod) * (average_biome_speed*3)/CREATURE_UPKEEP) + CREATURE_DRAIN)/60


    def upkeep(self):
        #self.speed = self.speed_mod * self.biome_speed_mod[self.cur_biome]
        self.fullness -= self.food_upkeep

        if self.fullness < 0 or self.hp < 0:
            self.state="dying"
            self.speed_mod=0
            #self.kill()
            self.reward = -1 * self.max_food
            return 1
        else:
            if self.hp < self.max_hp:
                self.hp = self.hp + 0.2
            if self.reward <= 0:
                self.reward = -1 * self.food_upkeep
            else:
                self.reward -= self.food_upkeep
            return 0

    def feed(self, amount = 10):
        if(self.fullness+amount <= self.max_food):
            self.fullness += amount
        else:
            self.fullness = self.max_food
        self.num_food_eaten += 1
        self.reward = amount

    def get_speed(self):
        return self.speed_mod * self.biome_speed_mod[self.cur_biome]

    def update_animation(self, delta_time: float = 1/60):
        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        #Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]

        #walking animation
        if(self.state=="walking"):
            self.cur_texture+=1
            if(self.cur_texture>6*UPDATES_PER_FRAME):
                self.cur_texture=0
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.walking_textures[frame][direction]
        #attacking
        elif(self.state=="attacking"):
            self.cur_texture += 1
            if (self.cur_texture > 5 * UPDATES_PER_FRAME):
                self.cur_texture=0
                self.state="walking"
            if(self.state=="attacking"):
                frame = self.cur_texture // UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.attacking_textures[frame][direction]
            else:
                frame = self.cur_texture // UPDATES_PER_FRAME
                direction = self.character_face_direction
                self.texture = self.walking_textures[frame][direction]
        #damaged
        elif(self.state=="damaged"):
            self.cur_texture += 1
            if (self.cur_texture > 6 * UPDATES_PER_FRAME):
                self.cur_texture = 0
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.damaged_textures[frame][direction]
        #dying
        elif(self.state=="dying"):
            self.cur_texture += 1
            if (self.cur_texture > 15 * UPDATES_PER_FRAME):
                #self.cur_texture = 0
                self.kill()
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.dying_textures[frame][direction]

    def draw_health_bar(self):
        """ Draw the health bar """

        # Draw the 'unhealthy' background
        #food bar
        if self.fullness < self.max_food:
            arcade.draw_rectangle_filled(center_x=self.center_x,
                                         center_y=self.center_y + FOODBAR_OFFSET_Y,
                                         width=FOODBAR_WIDTH,
                                         height=3,
                                         color=arcade.color.WHITE)

        # Calculate width based on health
        food_width = FOODBAR_WIDTH * (self.fullness / self.max_food)

        arcade.draw_rectangle_filled(center_x=self.center_x - 0.5 * (FOODBAR_WIDTH - food_width),
                                     center_y=self.center_y + FOODBAR_OFFSET_Y,
                                     width=food_width,
                                     height=FOODBAR_HEIGHT,
                                     color=arcade.color.BROWN)

        #health bar
        # Draw the 'unhealthy' background
        if self.hp < self.max_hp:
            arcade.draw_rectangle_filled(center_x=self.center_x,
                                         center_y=self.center_y + HEALTHBAR_OFFSET_Y,
                                         width=HEALTHBAR_WIDTH,
                                         height=3,
                                         color=arcade.color.WHITE)

        # Calculate width based on health
        health_width = HEALTHBAR_WIDTH * (self.hp / self.max_hp)

        arcade.draw_rectangle_filled(center_x=self.center_x - 0.5 * (HEALTHBAR_WIDTH - health_width),
                                     center_y=self.center_y + HEALTHBAR_OFFSET_Y,
                                     width=health_width,
                                     height=HEALTHBAR_HEIGHT,
                                     color=arcade.color.RED)

    def draw_id(self, font_size):
        arcade.draw_text(str(self.id), self.center_x-10,
                         self.center_y - CREATURE_HEIGHT*2, arcade.color.BLACK, 12)