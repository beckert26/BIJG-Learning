

from main import *

BIOME_SCALING = 1

#pictures are 100x100
BIOME_LENGTH=100
BIOME_SPAWN_RATE_LIST=[1.5,1.0,0.5]

class Biomes(arcade.Sprite):
    def __init__(self, biome):
        super().__init__()

        self.type="none"
        self.biome = biome
        self.food_spawn=1.0
        self.scale=BIOME_SCALING

        if biome==0:
            self.texture = arcade.load_texture(f"sprites/biome/plain.png")
            self.type="plain"
            self.food_spawn = BIOME_SPAWN_RATE_LIST[biome]
        elif biome==1:
            self.texture = arcade.load_texture(f"sprites/biome/mountain.png")
            self.type="mountain"
            self.food_spawn = BIOME_SPAWN_RATE_LIST[biome]
        elif biome==2:
            self.texture = arcade.load_texture(f"sprites/biome/desert.png")
            self.type="desert"
            self.food_spawn = BIOME_SPAWN_RATE_LIST[biome]
        else:
            self.type="none"
    def update_animation(self, delta_time: float = 1/60):
        return

