import arcade
import random
import math
from arcade.sound import load_sound

sprite_scaling_player = 0.03
sprite_scaling_coin = 0.1
sprite_scaling_laser = 0.8
coin_count = 10
ancho_pantalla = 800
alto_pantalla = 600
titulo = "Nintendont"
bullet_speed = 5

particle_gravity = 0.05

particle_fade_rate = 8
particle_min_speed = 2.5
particle_speed_range = 2.5

particle_count = 20
particle_radius = 3

particle_colors = [ arcade.color.ALIZARIN_CRIMSON,
                    arcade.color.COQUELICOT,
                    arcade.color.LAVA,
                    arcade.color.KU_CRIMSON,
                    arcade.color.DARK_TANGERINE ]

particle_sparkle_chance = 0.02


smoke_start_scale = 0.25
smoke_expansion_rate = 0.03

smoke_fade_rate = 7
smoke_rise_rate = 0.5

smoke_chance = 0.25

class Smoke(arcade.SpriteCircle):
    def __init__(self, size):
        super().__init__(size, arcade.color.LIGHT_GRAY, soft=True)
        self.change_y = smoke_rise_rate
        self.scale = smoke_start_scale
    
    def update(self):
        if self.alpha <= particle_fade_rate:
            self.remove_from_sprite_lists()
        else:
            self.alpha -= smoke_fade_rate
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.scale += smoke_expansion_rate
            
class Particle(arcade.SpriteCircle):
    def __init__(self, my_list):
        color = random.choice(particle_colors)
        super().__init__(particle_radius, color)
        self.normal_texture = self.texture
        self.my_list = my_list
        
        speed = random.random() * particle_speed_range + particle_min_speed
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed

        self.my_alpha = 255
        self.my_list = my_list
    
    def update(self):
        if self.my_alpha <= particle_fade_rate:
            self.remove_from_sprite_lists()
        else:
            self.my_alpha -= particle_fade_rate
            self.alpha = self.my_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.change_y -= particle_gravity

            if random.random() <= particle_sparkle_chance:
                self.alpha = 255
                self.texture = arcade.make_circle_texture(self.width, arcade.color.WHITE)
            else: 
                self.texture = self.normal_texture
            
            if random.random() <= smoke_chance:
                smoke = Smoke(5)
                smoke.position = self.position
                self.my_list.append(smoke)
                            
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.RED_BROWN)
        self.player_list = None
        self.coin_list = None
        self.bullet_blue_list = None
        self.bullet_red_list = None
        self.explosions_list = None
        
        self.background = None
        self.frame_count = 0
        self.enemy_list = None

        self.player = None
        self.score = 0


        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser2.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/explosion2.wav")
        
    def setup(self):
        self.background = arcade.load_texture("assets/BackgroundSpace.png")
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.bullet_blue_list = arcade.SpriteList()
        self.bullet_red_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.score = 0
        
        self.player = arcade.Sprite("assets/spaceship.png", sprite_scaling_player)
        self.player.center_y = 40
        self.player_list.append(self.player)
        musica = load_sound("assets/Intergalactic-Odyssey.mp3")
        arcade.sound.play_sound(musica)
        for _ in range(coin_count):
            coin = arcade.Sprite("assets/alien2.png", sprite_scaling_coin)
            coin.angle = 180
            coin.center_x = random.randrange(500)
            coin.center_y = random.randrange(200, alto_pantalla - 20 )

            self.coin_list.append(coin)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, ancho_pantalla, alto_pantalla, self.background)
        self.coin_list.draw()
        self.enemy_list.draw()
        self.bullet_blue_list.draw()
        self.bullet_red_list.draw()
        self.player_list.draw()
        self.explosions_list.draw()

        arcade.draw_text(f"Score: {self.score}", 700, 20, arcade.color.WHITE, 14)
    
    def on_update(self, delta_time):
        
        for coin in self.enemy_list:
            coin.center_x = coin.center_x + 100
            
        self.bullet_blue_list.update()
        self.bullet_red_list.update()
        self.explosions_list.update()

        for coin_index in self.coin_list:
            odds = 200
            adj_odds = int(odds * (1/60)/ delta_time)
            
            if random.randrange(adj_odds) == 0:
                arcade.sound.play_sound(self.gun_sound)
                bullet_red = arcade.Sprite(":resources:images/space_shooter/laserRed01.png")
                bullet_red.center_x = coin_index.center_x
                bullet_red.angle = 180
                bullet_red.top = coin_index.bottom
                bullet_red.change_y = -5
                self.bullet_red_list.append(bullet_red)


        
        for bullet_blue in self.bullet_blue_list:

            hit_list_enemy = arcade.check_for_collision_with_list(bullet_blue, self.coin_list)

            if len(hit_list_enemy) > 0:
                bullet_blue.remove_from_sprite_lists()

                    
            for coin in hit_list_enemy:
                for _ in range(particle_count):
                    particle = Particle(self.explosions_list)
                    particle.position = coin.position
                    self.explosions_list.append(particle)

                smoke = Smoke(10)
                smoke.position = coin.position
                self.explosions_list.append(smoke)
                coin.remove_from_sprite_lists()
                self.score += 1
                arcade.sound.play_sound(self.hit_sound)
            if bullet_blue.bottom > alto_pantalla:
                bullet_blue.remove_from_sprite_lists()

        for bullet_red in self.bullet_red_list:
            hit_list_player = arcade.check_for_collision_with_list(bullet_red, self.player_list)

            if len(hit_list_player) > 0:
                bullet_red.remove_from_sprite_lists()

            for player in hit_list_player:
                for _ in range(particle_count):
                    particle = Particle(self.explosions_list)
                    particle.position = player.position
                    self.explosions_list.append(particle)


                smoke = Smoke(10)
                smoke.position = player.position
                self.explosions_list.append(smoke)
                player.remove_from_sprite_lists()

                arcade.sound.play_sound(self.hit_sound)
                
            if bullet_red.top > alto_pantalla:
                bullet_red.remove_from_sprite_lists()
            
        
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        arcade.sound.play_sound(self.gun_sound)

        bullet_blue = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", sprite_scaling_laser)
        bullet_blue.angle = 90

        bullet_blue.change_y = bullet_speed

        bullet_blue.center_x = self.player.center_x
        bullet_blue.bottom = self.player.top
        self.bullet_blue_list.append(bullet_blue)
    
    def on_mouse_motion(self, x, y, delta_x, delta_y):
        self.player.center_x = x
        self.player_center_y = 20
class Instruction_View(arcade.View):
        def on_show(self):
            arcade.set_background_color(arcade.csscolor.LIGHT_YELLOW)

            arcade.set_viewport(0, ancho_pantalla - 1, 0, alto_pantalla - 1)
        def on_draw(self):
            arcade.start_render()
            arcade.draw_text("ANIQUILA A LOS ALIENS!", ancho_pantalla / 2, alto_pantalla / 2,
                            arcade.color.BLACK_OLIVE, font_size=50, anchor_x="center")
            arcade.draw_text("Insert Coin", ancho_pantalla / 2, alto_pantalla / 2-75,
                            arcade.color.BLACK_OLIVE, font_size=20, anchor_x="center")
        def on_mouse_press(self, _x, _y, _button, _modifiers):
            moneda = load_sound("assets/moneda.mp3")
            arcade.sound.play_sound(moneda)
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
def main():
    window = window = arcade.Window(ancho_pantalla, alto_pantalla, titulo)
    start_view = Instruction_View()
    window.show_view(start_view)
    arcade.run()
if __name__ == "__main__":
    main()
