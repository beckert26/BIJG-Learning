import arcade

CHARACTER_SCALING = 1.5
UPDATES_PER_FRAME=5

class CreatureCharacter(arcade.sprite):
    def __init__(self):
        super().__init__()

        self.cur_texture=0

        self.scale=CHARACTER_SCALING

        #load sprite textures
        #walking
        self.walk_textures = []
        for i in range(6):
            texture= arcade.load_texture("sprites/walk/frame_{i}_delay-0.1s.gif")
            self.walk_textures.append(texture)
    def update_animation(self, delta_time: float = 1/60):
        #walking animation
        self.cur_texture+=1
        if(self.cur_texture>6*UPDATES_PER_FRAME):
            self.cur_texture=0
        frame = self.cur_texture
        self.texture=self.walk_textures[frame]