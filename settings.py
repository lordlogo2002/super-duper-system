import math

class GAME:
    @classmethod
    def update_screen_size(cls, width:int, height:int):
        cls.SCREEN_SIZE = cls.SCREEN_WIDTH, cls.SCREEN_HEIGHT = width, height
        cls.HALF_WIDTH = cls.SCREEN_WIDTH // 2
        cls.HALF_HEIGHT = cls.SCREEN_HEIGHT // 2

        MOUSE.update()
        RayCast.update()
        SCREEN.update()

    WIDTH_FACTOR = 100
    HEIGHT_FACTOR = 100
    SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
    HALF_WIDTH = SCREEN_WIDTH // 2
    HALF_HEIGHT = SCREEN_HEIGHT // 2
    TARGET_FPS = 0

class PLAYER:
    START_POSITION = 1.5, 2  # mini_map
    START_ANGLE = 0
    SPEED = 0.004
    ROTATION_SPEED = 0.002
    SIZE_SCALE = 60
    MAX_HEALTH = 100

class MOUSE:
    @classmethod
    def update(cls):
        cls.BORDER_RIGHT = GAME.SCREEN_WIDTH - cls.BORDER_LEFT

    SENSITIVITY = 0.0001
    MAX_REL = 40
    BORDER_LEFT = 100
    BORDER_RIGHT = GAME.SCREEN_WIDTH - BORDER_LEFT

class DECO:
    FLOOR_COLOR = (30, 30, 30)

class RayCast:
    @classmethod
    def update(cls):
        cls.NUM_RAYS = GAME.SCREEN_WIDTH // 2
        cls.HALF_NUM_RAYS = cls.NUM_RAYS // 2
        cls.DELTA_ANGLE = cls.FOV / cls.NUM_RAYS

    FOV = math.pi / 3
    HALF_FOV = FOV / 2
    NUM_RAYS = GAME.SCREEN_WIDTH // 2
    HALF_NUM_RAYS = NUM_RAYS // 2
    DELTA_ANGLE = FOV / NUM_RAYS
    MAX_DEPTH = 20

class SCREEN:
    @classmethod
    def update(cls):
        cls.DISTANCE = GAME.HALF_WIDTH / math.tan(RayCast.HALF_FOV)
        cls.SCALE = GAME.SCREEN_WIDTH // RayCast.NUM_RAYS

    DISTANCE = GAME.HALF_WIDTH / math.tan(RayCast.HALF_FOV)
    SCALE = GAME.SCREEN_WIDTH // RayCast.NUM_RAYS

class TEXTURE:
    TEXTURE_SIZE = 512
    HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2