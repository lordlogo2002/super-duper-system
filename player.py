import settings
import pygame
import math
from logger import glob


class Player:
    def __init__(self, game):
        # Logging the start of the construction process.
        glob.gen.info("Initializing Player...")

        # Associate game with the player.
        self.game = game

        # Setting player's initial position and angle.
        self.x, self.y = settings.PLAYER.START_POSITION
        self.angle = settings.PLAYER.START_ANGLE

        # Logging the player's position and angle.
        glob.gen.debug(f"Set Player Initial Position to: ({self.x}, {self.y})")
        glob.gen.debug(f"Set Player Initial Angle to: {self.angle}")

        self.shot = False
        self.health = settings.PLAYER.MAX_HEALTH
        self.rel = 0
        self.health_recovery_delay = 700
        self.time_prev = pygame.time.get_ticks()
        # diagonal movement correction
        self.diag_move_corr = 1 / math.sqrt(2)

    def recover_health(self):
        if self.check_health_recovery_delay() and self.health < settings.PLAYER.MAX_HEALTH:
            self.health += 1

    def check_health_recovery_delay(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True

    def check_game_over(self):
        if self.health < 1:
            self.game.object_renderer.game_over()
            pygame.display.flip()
            pygame.time.delay(1500)
            self.game.new_game()

    def get_damage(self, damage):
        if self.game.game_console.be_god:
            return

        self.health -= damage
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = settings.PLAYER.SPEED * self.game.delta_time
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            dx += speed_cos
            dy += speed_sin
        elif keys[pygame.K_s]:
            dx += -speed_cos
            dy += -speed_sin
        if keys[pygame.K_a]:
            dx += speed_sin
            dy += -speed_cos
        elif keys[pygame.K_d]:
            dx += -speed_sin
            dy += speed_cos

        self.check_wall_collision(dx, dy)

        # if keys[pygame.K_LEFT]:
        #     self.angle -= settings.PLAYER.ROTATION_SPEED * self.game.delta_time
        # elif keys[pygame.K_RIGHT]:
        #     self.angle += settings.PLAYER.ROTATION_SPEED * self.game.delta_time
        # self.angle %= math.tau

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map or self.game.game_console.no_clip

    def check_wall_collision(self, dx, dy):
        scale = settings.PLAYER.SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def mouse_control(self):
        mx, my = pygame.mouse.get_pos()
        mb_left = settings.MOUSE.BORDER_LEFT
        mb_right = settings.MOUSE.BORDER_RIGHT
        max_rel = settings.MOUSE.MAX_REL
        half_width = settings.GAME.HALF_WIDTH
        half_height = settings.GAME.HALF_HEIGHT

        if mx < mb_left or mx > mb_right:
            pygame.mouse.set_pos([half_width, half_height])
        self.rel = pygame.mouse.get_rel()[0]
        self.rel = max(-max_rel, min(max_rel, self.rel))
        self.angle += self.rel * settings.MOUSE.SENSITIVITY * self.game.delta_time

    def draw(self):
        pygame.draw.line(self.game.screen, 'yellow', (self.x * settings.GAME.WIDTH_FACTOR, self.y * settings.GAME.HEIGHT_FACTOR),
                        (self.x * 100 + settings.GAME.SCREEN_WIDTH * math.cos(self.angle),
                         self.y * 100 + settings.GAME.SCREEN_WIDTH * math.sin(self.angle)), 2)
        pygame.draw.circle(self.game.screen, 'green', (self.x * settings.GAME.WIDTH_FACTOR, self.y * settings.GAME.HEIGHT_FACTOR), 15)

    def update(self):
        self.movement()
        self.mouse_control()
        self.recover_health()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
