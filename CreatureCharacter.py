import arcade
from main import *

CHARACTER_SCALING = 1.5
UPDATES_PER_FRAME=5

# Constants used to track if the player is facing left or right
RIGHT_FACING = 1
LEFT_FACING = 0

#loads two textures on reverse and on normal for left and right animations
def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class CreatureCharacter(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.cur_texture=0



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

        #change state based on position as test
        if(self.center_x<=SCREEN_WIDTH/2 and self.center_y<=SCREEN_HEIGHT/2):
            self.state=="walking"
        elif(self.center_x>=SCREEN_WIDTH/2 and self.center_y<=SCREEN_HEIGHT/2):
            self.state="attacking"
        elif(self.center_x<=SCREEN_WIDTH/2 and self.center_y>=SCREEN_HEIGHT/2):
            self.state="damaged"
        else:
            self.state="dying"

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