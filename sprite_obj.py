import pygame
import settings
import math
import os
from collections import deque

from logger import glob
import dev_console


class SpriteObject:
    def __init__(self, game, path='resources/sprites/static_sprites/candlebra.png',
                 pos=(10.5, 3.5), scale=0.7, shift=0.27):
        self.game = game
        self.player = game.player
        self.x, self.y = pos
        self.image = pygame.image.load(path).convert_alpha()
        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.image.get_width() // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
        self.dx, self.dy, self.theta, self.screen_x, self.dist, self.norm_dist = 0, 0, 0, 0, 1, 1
        self.sprite_half_width = 0
        self.SPRITE_SCALE = scale
        self.SPRITE_HEIGHT_SHIFT = shift

    def get_sprite_projection(self):
        proj = settings.SCREEN.DISTANCE / self.norm_dist * self.SPRITE_SCALE
        proj_width, proj_height = proj * self.IMAGE_RATIO, proj

        image = pygame.transform.scale(self.image, (proj_width, proj_height))

        self.sprite_half_width = proj_width // 2
        height_shift = proj_height * self.SPRITE_HEIGHT_SHIFT
        pos = self.screen_x - self.sprite_half_width, settings.GAME.HALF_HEIGHT - proj_height // 2 + height_shift

        self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos))

    def get_sprite(self):
        # Calculate the difference in x and y between the sprite and the player
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        self.dx, self.dy = dx, dy

        # Get the angle of the sprite relative to the player
        self.theta = math.atan2(dy, dx)

        # Ensure math.tau is defined or use 2*math.pi instead
        tau = 2 * math.pi

        # Wrap the difference in angle to [-pi, pi]
        def wrap_angle(angle):
            return (angle + math.pi) % tau - math.pi

        delta = wrap_angle(self.theta - self.player.angle)

        # Calculate the sprite's position on the screen
        delta_rays = delta / settings.RayCast.DELTA_ANGLE
        self.screen_x = (settings.RayCast.HALF_NUM_RAYS + delta_rays) * settings.SCREEN.SCALE

        # Calculate the distance to the sprite and the normalized distance
        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)

        # Check if the sprite is within the visible range and not too close to the player
        if (-self.IMAGE_HALF_WIDTH < self.screen_x < (settings.GAME.SCREEN_WIDTH + self.IMAGE_HALF_WIDTH)) and self.norm_dist > 0.1:
            self.get_sprite_projection()


    def update(self):
        self.get_sprite()


class AnimatedSprite(SpriteObject):
    def __init__(self, game, path='resources/sprites/animated_sprites/green_light/0.png',
                 pos=(11.5, 3.5), scale=0.8, shift=0.16, animation_time=120):
        super().__init__(game, path, pos, scale, shift)
        self.animation_time = animation_time
        self.path = path.rsplit('/', 1)[0]
        self.images = self.get_images(self.path)
        self.animation_time_prev = pygame.time.get_ticks()
        self.animation_trigger = False

    def update(self):
        super().update()
        self.check_animation_time()
        self.animate(self.images)

    def animate(self, images):
        if self.animation_trigger:
            images.rotate(-1)
            self.image = images[0]

    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pygame.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def get_images(self, path):
        images = deque()
        for file_name in os.listdir(path):
            if os.path.isfile(os.path.join(path, file_name)):
                img = pygame.image.load(path + '/' + file_name).convert_alpha()
                images.append(img)
        return images
