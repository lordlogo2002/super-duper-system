# ray_casting.pyx
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False

import pygame
from libc.math cimport sin, cos
from logger import glob
import settings
from libc.math cimport isnan

cdef float ZERO_AVOIDANCE = 1e-10

cdef class RayCasting:
    cdef object _game
    cdef list _ray_casting_result, _objects_to_render
    cdef dict _textures

    def __init__(self, game):
        glob.gen.info("Construct RayCasting")
        self._game = game
        self._ray_casting_result = []
        self._objects_to_render = []
        self._textures = self._game.object_renderer.wall_textures

    @property
    def game(self):
        return self._game

    def ray_casting_result(self):
        if not self._ray_casting_result:
            return []
        return self._ray_casting_result

    def objects_to_render(self):
        if not self._objects_to_render:
            return []
        return self._objects_to_render

    @property
    def textures(self):
        return self._textures

    def get_objects_to_render(self):
        self.objects_to_render().clear()
        cdef int ray
        cdef float depth, proj_height, offset, texture_height
        cdef object texture, wall_column, wall_pos

        # Pre-calculations
        cdef float texture_size_minus_scale = settings.TEXTURE.TEXTURE_SIZE - settings.SCREEN.SCALE
        cdef int screen_scale = settings.SCREEN.SCALE
        cdef float half_height = settings.GAME.HALF_HEIGHT
        cdef int screen_height = settings.GAME.SCREEN_HEIGHT

        for ray, values in enumerate(self.ray_casting_result()):
            depth, proj_height, texture, offset = values

            # Guard against problematic values
            if abs(proj_height) < 0.0001:  # some small threshold value
                continue

            if proj_height < screen_height:
                texture = self.game.object_renderer.get_wall_texture(texture)
                wall_column = texture.subsurface(
                    offset * texture_size_minus_scale, 0, screen_scale, settings.TEXTURE.TEXTURE_SIZE
                )
                wall_column = pygame.transform.scale(wall_column, (screen_scale, int(abs(proj_height))))
                wall_pos = (ray * screen_scale, half_height - int(proj_height // 2))
            else:
                texture = self.game.object_renderer.get_wall_texture(texture)
                texture_height = settings.TEXTURE.TEXTURE_SIZE * screen_height / proj_height

                # Check for NaN
                if isnan(texture_height):
                    continue

                wall_column = texture.subsurface(
                    offset * texture_size_minus_scale, settings.TEXTURE.HALF_TEXTURE_SIZE - int(texture_height // 2),
                    screen_scale, int(texture_height)
                )
                wall_column = pygame.transform.scale(wall_column, (screen_scale, screen_height))
                wall_pos = (ray * screen_scale, 0)

            self.objects_to_render().append((depth, wall_column, wall_pos))

    def ray_cast(self):
        self.ray_casting_result().clear()
        cdef float texture_vert = 1, texture_hor = 1
        cdef float ox, oy, ray_angle, sin_a, cos_a, texture = 1, offset = 0
        cdef float x_map, y_map, depth
        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.game.player.angle - settings.RayCast.HALF_FOV + 0.0001
        for _ in range(settings.RayCast.NUM_RAYS):
            sin_a = sin(ray_angle)
            cos_a = cos(ray_angle)
            # [omitted code for brevity]

            depth *= cos(self.game.player.angle - ray_angle)

            proj_height = settings.SCREEN.DISTANCE / (depth + 0.0001)

            self.ray_casting_result().append((depth, proj_height, texture, offset))

            ray_angle += settings.RayCast.DELTA_ANGLE

    def update(self):
        self.ray_cast()
        self.get_objects_to_render()