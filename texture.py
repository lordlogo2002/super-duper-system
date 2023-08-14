import settings
import pygame
from logger import glob


class Texture(settings.TEXTURE):
    @staticmethod
    def create_default_texture(text, res=(settings.TEXTURE.TEXTURE_SIZE, settings.TEXTURE.TEXTURE_SIZE), color=(255, 0, 255)):
        """Create a full color texture with the given text res and color"""

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
        """
            Load a texture from the path with the given texture and return a default texture if not found
            image not scaled the scale is for default image
        """

        logger = glob.gen

        logger.debug(f"Attempting to load texture from path: {path}")

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

        return texture, image_found

    @classmethod
    def start_with_default(cls, text, color, load_state:bool=False, res=(settings.TEXTURE.TEXTURE_SIZE, settings.TEXTURE.TEXTURE_SIZE)):
        texture, _ = cls.create_default_texture(text, res, color)
        return cls(None, res, pre_texture=texture, load_state=load_state)

    def __init__(self, path:str, res=(settings.TEXTURE.TEXTURE_SIZE, settings.TEXTURE.TEXTURE_SIZE), *, pre_texture=None, load_state:bool=False):
        self.__path = path
        self.__res = res

        if pre_texture:
            self.texture = pre_texture
            self.__loading_successful = load_state
            return

        self.texture, self.__loading_successful = self.load_texture(path, res)

    @property
    def path(self):
        return self.__path

    @property
    def res(self):
        return self.__res

    @property
    def loading_successfully(self):
        return self.__loading_successful


class ScaledTexture(Texture):
    @classmethod
    def load_texture(cls, path, res=(settings.TEXTURE.TEXTURE_SIZE, settings.TEXTURE.TEXTURE_SIZE)):
        logger = glob.gen
        texture, load = super().load_texture(path, res)
        texture = pygame.transform.scale(texture, res)
        logger.debug(f"Texture scaled to target resolution: {res}")

        logger.info(f"Texture processing completed for path: {path}")
        return texture, load

    def __init__(self, path: str, res=(settings.TEXTURE.TEXTURE_SIZE, settings.TEXTURE.TEXTURE_SIZE)):
        super().__init__(path, res)
