
import arcade

BIOME_SCALING = 1

#pictures are 100x100
BIOME_LENGTH=100
BIOME_SPAWN_RATE_LIST=[1.5,1.1,0.8]

class Biomes(arcade.Sprite):
    def __init__(self, biome,textures,biome_spawn = BIOME_SPAWN_RATE_LIST):
        super().__init__()

        self.type="none"
        self.biome = biome
        self.food_spawn=1.0
        self.scale=BIOME_SCALING
        self.texture = textures[0]
        self.textures = textures
        self.biome_spawn = biome_spawn

        if biome==0:
            self.texture = textures[0]
            self.type="plain"
            self.food_spawn = self.biome_spawn[biome]
        elif biome==1:
            self.texture = textures[1]
            self.type="mountain"
            self.food_spawn = self.biome_spawn[biome]
        elif biome==2:
            self.texture = textures[2]
            self.type="desert"
            self.food_spawn = self.biome_spawn[biome]
        else:
            self.type="none"
    def update_animation(self, delta_time: float = 1/60):
        return

    def update_spawn(self, biome_spawn):
        self.biome_spawn = biome_spawn
        if self.biome==0:
            self.food_spawn = self.biome_spawn[self.biome]
        elif self.biome==1:
            self.food_spawn = self.biome_spawn[self.biome]
        elif self.biome==2:
            self.food_spawn = self.biome_spawn[self.biome]
        else:
            self.food_spawn = 0
