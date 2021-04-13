
import arcade

FOOD_SCALING = .05
UPDATES_PER_FRAME=5

#pictures are 100x100
FOOD_WIDTH=452*FOOD_SCALING
FOOD_HEIGHT=512*FOOD_SCALING

class Food(arcade.Sprite):
    def __init__(self,texture):
        super().__init__()

        self.type="none"

        self.scale=FOOD_SCALING
        self.texture = texture

    def update_animation(self, delta_time: float = 1/60):
        return