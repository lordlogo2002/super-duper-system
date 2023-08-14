# object_renderer.pyx
# cython: language_level=3
cimport cython

import pygame
import os
import settings
from logger import glob

cdef dict texture_buffer = {}

cdef class ObjectRenderer:
    cdef object _game, _wall_textures, _sky_texture, _screen
    cdef float _sky_offset
    cdef int _width, _height, _half_height

    def __init__(self, game):
        glob.gen.info("Construct ObjectRenderer")

        self._game = game
        self._screen = game.screen
        self._width = settings.GAME.SCREEN_WIDTH
        self._height = settings.GAME.SCREEN_HEIGHT
        self._half_height = settings.GAME.HALF_HEIGHT
        self._wall_textures = self.load_wall_textures()
        self._sky_texture = self.load_texture("resources/textures/sky.png", (self._width, self._half_height))
        self._sky_offset = 0.0

    @property
    def game(self):
        return self._game

    @property
    def screen(self):
        return self._screen

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def half_height(self):
        return self._half_height

    @property
    def wall_textures(self):
        return self._wall_textures

    @property
    def sky_offset(self):
        return self._sky_offset

    def set_sky_offset(self, value):
        self._sky_offset = value

    @property
    def sky_texture(self):
        return self._sky_texture

    @property
    def sky_offset(self):
        return self._sky_offset

    def draw(self):
        self.draw_background()
        self.render_game_objects()

    def draw_background(self):
        width = settings.GAME.SCREEN_WIDTH
        width, height = settings.GAME.SCREEN_SIZE
        half_height = settings.GAME.HALF_HEIGHT
        self.set_sky_offset((self.sky_offset + 4.0 * self.game.player.rel) % width)
        self.screen.blit(self.sky_texture["texture"], (-self.sky_offset, 0))
        self.screen.blit(self.sky_texture["texture"], (-self.sky_offset + width, 0))
        # floor
        pygame.draw.rect(self.screen, settings.DECO.FLOOR_COLOR, (0, half_height, width, height))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def create_default_texture(text, res=(settings.TEXTURE.TEXTURE_SIZE, settings.TEXTURE.TEXTURE_SIZE), color=(255, 0, 255)):
        glob.gen.debug("Creating default texture with text: {}, resolution: {}, and color: {}".format(text, res, color))

        # Create a new surface and fill it with color
        texture = pygame.Surface(res)
        texture.fill(color)

        # Define a font and color for the text
        font = pygame.font.Font(None, 20)  # Choose your preferred font and size
        text_color = (255, 255, 255)  # White color for the text

        # Render the text
        text_surface = font.render(text, True, text_color)

        # Calculate the position of the text (centered)
        text_width, text_height = text_surface.get_size()
        text_pos = ((res[0] - text_width) // 2, (res[1] - text_height) // 2)

        # Draw the text on the texture
        texture.blit(text_surface, text_pos)

        glob.gen.info("Default texture created successfully")

        return texture

    @classmethod
    def load_texture(cls, path, res=(settings.TEXTURE.TEXTURE_SIZE, settings.TEXTURE.TEXTURE_SIZE)):
        glob.gen.debug("Loading texture from path: {}".format(path))
        glob.gen.debug("Resolution: {}".format(res))

        try:
            # Try to load the texture from the file
            texture = pygame.image.load(path)
            glob.gen.info("Texture loaded from path: {}".format(path))
            image_found = True
        except FileNotFoundError:
            # If file is not found, create a default texture
            glob.gen.warn("File not found at path: {}. Using default texture.".format(path))
            texture = cls.create_default_texture("ERR:FILE:"+path, res)
            image_found = False
        except pygame.error:
            # If file is not the right format, create a default texture
            glob.gen.warn("Filetype in path {} is not supported. Using default texture.".format(path))
            texture = cls.create_default_texture("ERR:FORMAT:"+path, res, (220, 220, 120))
            image_found = False

        glob.gen.debug("Scaling texture to the desired resolution")
        texture = pygame.transform.scale(texture, res)

        glob.gen.info("Texture loaded and scaled successfully")

        return {"path": path, "texture": texture, "res": res, "found": image_found}

    def load_wall_textures(self):
        glob.gen.debug("Load Wall textures")
        textures = {
            1: self.load_texture('resources/textures/1.png'),
            2: self.load_texture('resources/textures/2.png'),
            3: self.load_texture('resources/textures/3.png'),
            4: self.load_texture('resources/textures/4.png'),
            5: self.load_texture('resources/textures/5.png')
        }
        glob.gen.info("Textures Loaded:")
        if all(not v["found"] for v in textures.values()):
            glob.gen.critical("No Images Found")
        else:
            for texture in textures.values():
                if texture["found"]:
                    glob.gen.info(f"FOUND TEXTURE: {texture['path']} <> RES: {texture['res']}")
                else:
                    glob.gen.warn(f"MISSING TEXTURE: {texture['path']} <> RES: {texture['res']}")
        return textures

    def get_wall_texture(self, key):
        texture = self.wall_textures.get(key)
        if texture is not None:
            return texture["texture"]

        default_texture = texture_buffer.get(key)
        if default_texture is not None:
            return default_texture

        glob.gen.critical(f"Warning KEY:{key} is not registered")
        default_texture = self.create_default_texture(f"ERR:KEY:{key}", color=(255, 0, 0))
        texture_buffer[key] = default_texture
        return default_texture
