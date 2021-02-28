import arcade
from main import *

CHARACTER_SCALING = 1.5
UPDATES_PER_FRAME=5
CREATURE_SIGHT = 75
CREATURE_UPKEEP = 100
CREATURE_DRAIN = 0.02

# Constants used to track if the player is facing left or right
RIGHT_FACING = 1
LEFT_FACING = 0

#pictures are 27x14
CREATURE_WIDTH=27*CHARACTER_SCALING
CREATURE_HEIGHT=14*CHARACTER_SCALING

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
    def __init__(self):
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
        for i in range(6):
            texture= arcade.load_texture_pair(f"sprites/walk/frame_{i}_delay-0.1s.gif")
            self.walking_textures.append(texture)

        #attacking
        for i in range(5):
            texture= arcade.load_texture_pair(f"sprites/attack/frame_{i}_delay-0.1s.gif")
            self.attacking_textures.append(texture)
        #dying
        for i in range(15):
            if(i<10):
                texture = arcade.load_texture_pair(f"sprites/die/frame_0{i}_delay-0.1s.gif")
            else:
                texture= arcade.load_texture_pair(f"sprites/die/frame_{i}_delay-0.1s.gif")
            self.dying_textures.append(texture)

        #damaged
        for i in range(6):
            texture= arcade.load_texture_pair(f"sprites/damage/frame_{i}_delay-0.1s.gif")
            self.damaged_textures.append(texture)
        self.set_upkeep()

    def set_upkeep(self):
        average_biome_speed = (self.biome_speed_mod[0] + self.biome_speed_mod[1] + self.biome_speed_mod[2])/3
        self.food_upkeep = ((self.max_food * self.speed_mod * self.sight_mod * average_biome_speed/CREATURE_UPKEEP) + CREATURE_DRAIN)/30

    def upkeep(self):
        self.fullness -= self.food_upkeep
        #print(self.fullness)
        if self.fullness < 0:
            self.kill()

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
            return

        # #change state based on position as test
        # if(self.center_x<=SCREEN_WIDTH/2 and self.center_y<=SCREEN_HEIGHT/2):
        #     self.state=="walking"
        # elif(self.center_x>=SCREEN_WIDTH/2 and self.center_y<=SCREEN_HEIGHT/2):
        #     self.state="attacking"
        # elif(self.center_x<=SCREEN_WIDTH/2 and self.center_y>=SCREEN_HEIGHT/2):
        #     self.state="damaged"
        # else:
        #     self.state="dying"

        #walking animation
        if(self.state=="walking"):
            self.cur_texture+=1
            if(self.cur_texture>5*UPDATES_PER_FRAME):
                self.cur_texture=0
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.walking_textures[frame][direction]
        #attacking
        elif(self.state=="attacking"):
            self.cur_texture += 1
            if (self.cur_texture > 4 * UPDATES_PER_FRAME):
                self.cur_texture = 0
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.attacking_textures[frame][direction]
        #damaged
        elif(self.state=="damaged"):
            self.cur_texture += 1
            if (self.cur_texture > 5 * UPDATES_PER_FRAME):
                self.cur_texture = 0
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.damaged_textures[frame][direction]
        #dying
        elif(self.state=="dying"):
            self.cur_texture += 1
            if (self.cur_texture > 14 * UPDATES_PER_FRAME):
                self.cur_texture = 0
            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.character_face_direction
            self.texture = self.dying_textures[frame][direction]