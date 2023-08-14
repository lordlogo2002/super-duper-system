import pygame
import settings
import os
from logger import glob
from texture import ScaledTexture

texture_buffer = {}

class ObjectRenderer:
    def __init__(self, game):
        # Logging the start of the construction process.
        glob.gen.info("Initializing ObjectRenderer...")

        # Associate game with renderer.
        self.game = game
        self.screen = game.screen

        # Load wall textures.
        glob.gen.debug("Attempting to load wall textures for ObjectRenderer...")
        self.wall_textures = self.load_wall_textures()
        glob.gen.info("Wall textures loaded successfully.")

        # Load sky texture.
        glob.gen.debug("Attempting to load sky texture from 'resources/textures/sky.png'...")
        self.sky_texture = self.load_texture("resources/textures/sky.png", (settings.GAME.SCREEN_WIDTH, settings.GAME.HALF_HEIGHT))
        glob.gen.info("Sky texture loaded successfully.")

        # Setting sky offset.
        self.sky_offset = 0
        glob.gen.debug("Sky offset set to 0.")

        self.blood_screen = self.load_texture('resources/textures/blood_screen.png', settings.GAME.SCREEN_SIZE)
        self.digit_size = 90
        self.digit_images = [self.load_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)["texture"]
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.load_texture('resources/textures/game_over.png', settings.GAME.SCREEN_SIZE)["texture"]
        self.win_image = self.load_texture('resources/textures/win.png', settings.GAME.SCREEN_SIZE)["texture"]

        # Logging the successful completion of the initialization process.
        glob.gen.info("ObjectRenderer initialized successfully.")

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_player_health()

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def draw_player_health(self):
        health = str(self.game.player.health)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (i * self.digit_size, 0))
        self.screen.blit(self.digits['10'], ((i + 1) * self.digit_size, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen["texture"], (0, 0))

    def draw_background(self):
        width = settings.GAME.SCREEN_WIDTH
        width, height = settings.GAME.SCREEN_SIZE
        half_height = settings.GAME.HALF_HEIGHT
        self.sky_offset = (self.sky_offset + 4.0 * self.game.player.rel) % width
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
        logger = glob.gen

        logger.debug(f"Initiating default texture creation. Text: {text}, Target Resolution: {res}, Color: {color}")

        # Create a new surface and fill it with color
        texture = pygame.Surface(res)
        texture.fill(color)

        # Adding a white outline to the texture
        outline_color = (255, 255, 255)
        outline_thickness = 4
        pygame.draw.rect(texture, outline_color, texture.get_rect(), outline_thickness)

        # Define a font and color for the text
        font = pygame.font.Font(None, 20)
        text_color = outline_color

        # Render the text
        text_surface = font.render(text, True, text_color)
        logger.debug("Text rendered for default texture")

        # Calculate the position of the text (centered)
        text_width, text_height = text_surface.get_size()
        text_pos = ((res[0] - text_width) // 2, (res[1] - text_height) // 2)

        # Draw the text on the texture
        texture.blit(text_surface, text_pos)

        logger.info("Default texture with outline generated and ready for use")

        return texture

    @classmethod
    def load_texture(cls, path, res=(settings.TEXTURE.TEXTURE_SIZE, settings.TEXTURE.TEXTURE_SIZE)):
        logger = glob.gen

        logger.debug(f"Attempting to load texture from path: {path} with target resolution: {res}")

        try:
            # Try to load the texture from the file
            texture = pygame.image.load(path)
            logger.info(f"Successfully loaded texture from path: {path}")
            image_found = True
        except FileNotFoundError:
            # If file is not found, create a default texture
            logger.warn(f"File not found at path: {path}. Resorting to default texture.")
            texture = cls.create_default_texture("ERR:FILE:"+path, res)
            image_found = False
        except pygame.error:
            # If file is not the right format, create a default texture
            logger.warn(f"Unsupported filetype at path: {path}. Resorting to default texture.")
            texture = cls.create_default_texture("ERR:FORMAT:"+path, res, (220, 220, 120))
            image_found = False

        texture = pygame.transform.scale(texture, res)
        logger.debug(f"Texture scaled to target resolution: {res}")

        logger.info(f"Texture processing completed for path: {path}")

        return {"path": path, "texture": texture, "res": res, "found": image_found}

    def load_wall_textures(self):
        logger = glob.gen

        logger.info("Initiating loading of wall textures.")

        texture_paths = [
            'resources/textures/1.png',
            'resources/textures/2.png',
            'resources/textures/3.png',
            'resources/textures/4.png',
            'resources/textures/5.png'
        ]

        textures = {index + 1: ScaledTexture(path) for index, path in enumerate(texture_paths)}

        logger.debug("Attempted loading of textures.")

        if all(not v.loading_successfully for v in textures.values()):
            logger.critical("Critical error: No textures found.")
            return textures

        for key, texture in textures.items():
            if texture.loading_successfully:
                logger.info(f"SUCCESS: TextureID: {key} | Path: {texture.path} | Resolution: {texture.res}")
            else:
                logger.warn(f"WARNING: Missing Texture | TextureID: {key} | Path: {texture.path} | Expected Resolution: {texture.res}")

        logger.info("Texture loading process completed.")

        return textures

    def get_wall_texture(self, key):
        logger = glob.gen

        texture = self.wall_textures.get(key)
        if texture is not None:
            return texture

        default_texture = texture_buffer.get(key)
        if default_texture is not None:
            return default_texture

        err_text = f"ERR:KEY:{key}"
        res = (settings.TEXTURE.TEXTURE_SIZE,)*2
        color=(255, 0, 0)

        # When an unrecognized map key is encountered:
        logger.error(f'Encountered unrecognized map key: "{key}".')
        logger.info('Attempting to resolve by generating a "missing texture" placeholder.')

        default_texture = ScaledTexture.start_with_default(err_text, color, res=res)

        logger.debug(f'Missing texture details: Key="{key}", Resolution={res}, Color={color}.')
        logger.info(f'For map creators: Please verify your map configuration and ensure that the key "{key}" corresponds to a known texture definition.')

        texture_buffer[key] = default_texture

        logger.info(f'Missing texture placeholder generated and stored in buffer for key: {key}. Ensuring consistency for future reference.')

        return default_texture
