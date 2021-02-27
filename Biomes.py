

from main import *

BIOME_SCALING = 1
UPDATES_PER_FRAME=5

#pictures are 100x100
BIOME_LENGTH=100

class Biomes(arcade.Sprite):
    def __init__(self, biome):
        super().__init__()

        self.type="none"

        self.scale=BIOME_SCALING

        if biome==0:
            self.texture = arcade.load_texture(f"sprites/biome/plain.png")
            self.type="plain"
        elif biome==1:
            self.texture = arcade.load_texture(f"sprites/biome/mountain.png")
            self.type="mountain"
        elif biome==2:
            self.texture = arcade.load_texture(f"sprites/biome/desert.png")
            self.type="desert"
        else:
            self.type="none"
    def update_animation(self, delta_time: float = 1/60):
        return