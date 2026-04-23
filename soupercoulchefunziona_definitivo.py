import arcade
import random
import math
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Platform"

PLAYER_SPEED = 5
JUMP_SPEED = 10
GRAVITY = 0.5
BULLET_SPEED = 14
ENEMY_SPEED = 2
ENEMY_BULLET_SPEED = 5
GRACE_PERIOD_DURATION = 2
PLATFORM_BUFFER = 120       

class Enemy(arcade.Sprite):
    def __init__(self, x, y, danger_list):
        super().__init__("enemy.png", scale=1.2)
        self.center_x = x
        self.center_y = y
        self.change_x = random.choice([-1, 1]) * ENEMY_SPEED
        self.danger_list = danger_list

    def update(self, delta_time=0, *args, **kwargs):
        self.center_x += self.change_x

        if self.center_x >= 560:
            self.center_x = 559
            self.change_x = -ENEMY_SPEED
        elif self.center_x <= -560:
            self.center_x = -559
            self.change_x = ENEMY_SPEED

        hit = arcade.check_for_collision_with_list(self, self.danger_list)
        if hit:
            platform = hit[0]
            self.change_x *= -1

            if self.center_x < platform.center_x:
                self.center_x = platform.left - self.width / 2 - 1
            else:
                self.center_x = platform.right + self.width / 2 + 1


class ShooterEnemy(arcade.Sprite):
    def __init__(self, x, y, danger_list, enemy_bullet_list):
        super().__init__("enemy.png", scale=1.2)
        self.center_x = x
        self.center_y = y
        self.change_x = random.choice([-1, 1]) * ENEMY_SPEED
        self.danger_list = danger_list
        self.enemy_bullet_list = enemy_bullet_list
        self.shoot_timer = random.uniform(0, 2.0)
        self.shoot_interval = random.uniform(1.5, 3.0)
        self.color = (255, 120, 120)

    def update(self, delta_time=0, *args, **kwargs):
        self.center_x += self.change_x

        if self.center_x >= 560:
            self.center_x = 559
            self.change_x = -ENEMY_SPEED
        elif self.center_x <= -560:
            self.center_x = -559
            self.change_x = ENEMY_SPEED

        hit = arcade.check_for_collision_with_list(self, self.danger_list)
        if hit:
            platform = hit[0]
            self.change_x *= -1
            if self.center_x < platform.center_x:
                self.center_x = platform.left - self.width / 2 - 1
            else:
                self.center_x = platform.right + self.width / 2 + 1

        self.shoot_timer += delta_time
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0.0
            self._shoot()

    def _shoot(self):
        bullet = arcade.SpriteSolidColor(8, 16, arcade.color.ORANGE)
        bullet.center_x = self.center_x
        bullet.top = self.bottom
        bullet.change_y = -ENEMY_BULLET_SPEED
        bullet.change_x = 0
        self.enemy_bullet_list.append(bullet)


class SpreadShooterEnemy(arcade.Sprite):
    def __init__(self, x, y, danger_list, enemy_bullet_list):
        super().__init__("enemy.png", scale=1.2)
        self.center_x = x
        self.center_y = y
        self.change_x = random.choice([-1, 1]) * ENEMY_SPEED
        self.danger_list = danger_list
        self.enemy_bullet_list = enemy_bullet_list
        self.shoot_timer = random.uniform(0, 2.5)
        self.shoot_interval = random.uniform(2.0, 4.0)
        self.color = (120, 120, 255)

    def update(self, delta_time=0, *args, **kwargs):
        self.center_x += self.change_x

        if self.center_x >= 560:
            self.center_x = 559
            self.change_x = -ENEMY_SPEED
        elif self.center_x <= -560:
            self.center_x = -559
            self.change_x = ENEMY_SPEED

        hit = arcade.check_for_collision_with_list(self, self.danger_list)
        if hit:
            platform = hit[0]
            self.change_x *= -1
            if self.center_x < platform.center_x:
                self.center_x = platform.left - self.width / 2 - 1
            else:
                self.center_x = platform.right + self.width / 2 + 1

        self.shoot_timer += delta_time
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0.0
            self._shoot_spread()

    def _shoot_spread(self):
        for angle_deg in [270, 225, 315]:
            angle_rad = math.radians(angle_deg)
            bullet = arcade.SpriteSolidColor(8, 8, arcade.color.ELECTRIC_BLUE)
            bullet.center_x = self.center_x
            bullet.center_y = self.bottom - 4
            bullet.change_x = ENEMY_BULLET_SPEED * math.cos(angle_rad)
            bullet.change_y = ENEMY_BULLET_SPEED * math.sin(angle_rad)
            self.enemy_bullet_list.append(bullet)


class Fruit(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("fruitt.png", scale=1.4)
        self.center_x = x
        self.center_y = y
        self.pulse_timer = random.uniform(0, math.pi * 2)

    def update(self, delta_time=0, *args, **kwargs):
        self.pulse_timer += 0.05
        s = 1.0 + 0.4 * math.sin(self.pulse_timer)
        self.scale = s


def overlaps_any_platform(x, y, size, platforms):
    for p in platforms:
        if (abs(x - p.center_x) < (size / 2 + p.width / 2) and
                abs(y - p.center_y) < (size / 2 + p.height / 2)):
            return True
    return False


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.danger_list = arcade.SpriteList()
        self.fruit_list = arcade.SpriteList()

        self.max_y = 0
        self.generated_y = 0

        self.player = None
        self.physics_engine = None

        self.bonus_score = 0
        self.high_score = 0
        self.grace_timer = 0
        self.music_player = None

        self.camera = arcade.Camera2D()

    def setup(self):
        if self.music_player:
            self.music_player.pause()
            # Note: delete() is not needed in newer arcade/pyglet versions, but we pause it.

        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.danger_list = arcade.SpriteList()
        self.fruit_list = arcade.SpriteList()

        self.max_y = 0
        self.generated_y = 0
        self.bonus_score = 0
        self.grace_timer = GRACE_PERIOD_DURATION

        # --- UPDATED SOUND PATHS ---
        # We add "sounds/" before each filename
        self.snd_shoot = arcade.Sound("sounds/shoot.wav")
        self.snd_death = arcade.Sound("sounds/deathwav.wav")
        self.snd_fruit = arcade.Sound("sounds/fruit.wav")
        self.snd_ouch = arcade.Sound("sounds/ouch.wav")
        self.music = arcade.Sound("sounds/music.mp3")

        self.music_player = self.music.play(volume=0.4, loop=True)

        self.player = arcade.Sprite("palla.png", scale=1)
        self.player.center_x = 100
        self.player.center_y = 50
        self.player_list.append(self.player)

        ground = arcade.SpriteSolidColor(800, 20, arcade.color.DARK_BROWN)
        ground.center_x = 400
        ground.center_y = 10
        self.wall_list.append(ground)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list, gravity_constant=GRAVITY
        )

        self.generate_platforms(1000)

    def generate_platforms(self, up_to_y):
        while self.generated_y < up_to_y:
            valid_pos = False
            attempts = 0
            temp_y = self.generated_y + random.randint(80, 110)
            temp_x = 0

            while not valid_pos and attempts < 10:
                temp_x = random.randint(-500, 500)
                if not overlaps_any_platform(temp_x, temp_y, PLATFORM_BUFFER, self.danger_list):
                    valid_pos = True
                attempts += 1

            self.generated_y = temp_y
            platform = arcade.Sprite("platform_2.png", scale=random.randint(2, 6))
            platform.center_x = temp_x
            platform.center_y = self.generated_y
            self.danger_list.append(platform)

            if random.random() < 0.5:
                for _ in range(20):
                    ex = random.randint(-500, 500)
                    ey = self.generated_y - random.randint(20, 60)
                    if not overlaps_any_platform(ex, ey, 40, self.danger_list):
                        roll = random.random()
                        if roll < 0.40:
                            self.enemy_list.append(Enemy(ex, ey, self.danger_list))
                        elif roll < 0.70:
                            self.enemy_list.append(
                                ShooterEnemy(ex, ey, self.danger_list, self.enemy_bullet_list)
                            )
                        else:
                            self.enemy_list.append(
                                SpreadShooterEnemy(ex, ey, self.danger_list, self.enemy_bullet_list)
                            )
                        break

            if random.random() < 0.15:
                for _ in range(20):
                    fx = random.randint(-500, 500)
                    fy = self.generated_y - random.randint(10, 50)
                    if not overlaps_any_platform(fx, fy, 24, self.danger_list):
                        self.fruit_list.append(Fruit(fx, fy))
                        break

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.wall_list.draw()
        self.danger_list.draw()
        self.fruit_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()

        score = int(self.max_y) + self.bonus_score

        arcade.draw_text(
            f"Score: {score - 49}",
            400 + self.camera.position[0],
            270 + self.camera.position[1],
            arcade.color.BLACK,
            14
        )

        arcade.draw_text(
            f"High Score: {self.high_score - 49}",
            400 + self.camera.position[0],
            240 + self.camera.position[1],
            arcade.color.BLACK,
            14
        )

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.bullet_list.update()
        self.enemy_bullet_list.update()
        self.enemy_list.update(delta_time)
        self.fruit_list.update()

        if self.grace_timer > 0:
            self.grace_timer -= delta_time
            self.player.alpha = 150
        else:
            self.player.alpha = 255

        if self.player.center_y > self.max_y:
            self.max_y = self.player.center_y

        self.high_score = max(self.high_score, int(self.max_y) + self.bonus_score)
        self.generate_platforms(self.max_y + 800)
        self.player.center_x = max(-560, min(560, self.player.center_x))

        if self.grace_timer <= 0:
            if arcade.check_for_collision_with_list(self.player, self.danger_list):
                self.snd_death.play()
                self.setup()
                return

            if arcade.check_for_collision_with_list(self.player, self.enemy_list):
                self.snd_death.play()
                self.setup()
                return

            if arcade.check_for_collision_with_list(self.player, self.enemy_bullet_list):
                self.snd_death.play()
                self.setup()
                return

        if self.player.center_y < self.max_y - 340:
            self.snd_death.play()
            self.setup()
            return

        for fruit in arcade.check_for_collision_with_list(self.player, self.fruit_list):
            self.snd_fruit.play()
            fruit.remove_from_sprite_lists()
            self.bonus_score += 500

        for bullet in list(self.bullet_list):
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if hit_list:
                bullet.remove_from_sprite_lists()
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                arcade.play_sound(self.snd_ouch)
                self.bonus_score += 100
            if bullet.top > SCREEN_HEIGHT + self.camera.position[1]:
                bullet.remove_from_sprite_lists()

        cam_y = self.camera.position[1]
        for eb in list(self.enemy_bullet_list):
            if (eb.bottom < cam_y - SCREEN_HEIGHT or
                    eb.top > cam_y + SCREEN_HEIGHT * 2 or
                    eb.right < -600 or eb.left > 600):
                eb.remove_from_sprite_lists()

        self.center_camera_to_player()

    def center_camera_to_player(self):
        screen_center_x = self.player.center_x - SCREEN_WIDTH / 2
        screen_center_x = max(0, screen_center_x)
        self.camera.position = (screen_center_x, self.max_y)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -PLAYER_SPEED
            self.player.scale_x = -1
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = PLAYER_SPEED
            self.player.scale_x = 1
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player.change_y = JUMP_SPEED
        elif key == arcade.key.SPACE:
            self.snd_shoot.play()
            bullet = arcade.SpriteSolidColor(10, 20, arcade.color.YELLOW)
            bullet.center_x = self.player.center_x
            bullet.bottom = self.player.top
            bullet.change_y = BULLET_SPEED
            self.bullet_list.append(bullet)
        elif key == arcade.key.R:
            self.setup()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.D, arcade.key.A):
            self.player.change_x = 0

def main():
    game = Game()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()