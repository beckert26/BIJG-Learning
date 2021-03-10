
from main import *


CHARACTER_SCALING = 1.5
UPDATES_PER_FRAME=5
CREATURE_SIGHT = 75
CREATURE_UPKEEP = 100
CREATURE_DRAIN = 0.1

# Constants used to track if the player is facing left or right
RIGHT_FACING = 1
LEFT_FACING = 0

#pictures are 27x14
CREATURE_WIDTH=27*CHARACTER_SCALING
CREATURE_HEIGHT=14*CHARACTER_SCALING

FOODBAR_WIDTH = 25
FOODBAR_HEIGHT = 3
FOODBAR_OFFSET_Y = 3

FOOD_NUMBER_OFFSET_X = -10
FOOD_NUMBER_OFFSET_Y = -25

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
    def __init__(self, id):
        super().__init__()

        self.cur_texture=0

        self.biome_speed_mod = [1.0,0.5,0.1]
        self.speed_mod = 1.0
        self.target = None
        self.max_food = 100
        self.fullness = 50
        self.sight_mod = 1.0
        self.food_upkeep = 0
        self.prev_target = None
        self.prev_target2 = None
        self.id=id

        self.character_face_direction = RIGHT_FACING

        self.scale=CHARACTER_SCALING

        self.state="walking"

        #load sprite textures for idle
        self.idle_texture_pair=load_texture_pair(f"sprites/slimeIdle.gif")

        #load sprite textures
        self.walking_textures = []
        self.attacking_textures = []
        self.damaged_textures = []
        self.dying_textures = []
        #walking
        for i in range(7):
            texture= arcade.load_texture_pair(f"sprites/walk/frame_{i}_delay-0.1s.gif")
            self.walking_textures.append(texture)

        #attacking
        for i in range(6):
            texture= arcade.load_texture_pair(f"sprites/attack/frame_{i}_delay-0.1s.gif")
            self.attacking_textures.append(texture)
        #dying
        for i in range(16):
            if(i<10):
                texture = arcade.load_texture_pair(f"sprites/die/frame_0{i}_delay-0.1s.gif")
            else:
                texture= arcade.load_texture_pair(f"sprites/die/frame_{i}_delay-0.1s.gif")
            self.dying_textures.append(texture)

        #damaged
        for i in range(7):
            texture= arcade.load_texture_pair(f"sprites/damage/frame_{i}_delay-0.1s.gif")
            self.damaged_textures.append(texture)
        self.set_upkeep()

    def set_upkeep(self):
        average_biome_speed = (self.biome_speed_mod[0] + self.biome_speed_mod[1] + self.biome_speed_mod[2])/3
        self.food_upkeep = ((self.max_food * self.speed_mod * self.sight_mod * average_biome_speed/CREATURE_UPKEEP) + CREATURE_DRAIN)/30


    def upkeep(self):
        self.fullness -= self.food_upkeep
        if self.fullness < 0:
            self.state="dying"
            self.speed_mod=0

    def feed(self):
        if(self.fullness+10 <= self.max_food):
            self.fullness += 10
        else:
            self.fullness = self.max_food

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
                self.cur_texture = 0
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.attacking_textures[frame][direction]
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

                self.kill()
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.dying_textures[frame][direction]

    def draw_health_bar(self):
        """ Draw the health bar """

        # Draw the 'unhealthy' background
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
    def draw_id(self, font_size):
        arcade.draw_text(str(self.id), self.center_x-10,
                         self.center_y - CREATURE_HEIGHT*2, arcade.color.BLACK, 12)