import sprite_obj
import pygame
from logger import glob
import npc

class ObjectHandler:
    def __init__(self, game):
        logger = glob.gen
        logger.info("Initializing ObjectHandler")

        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_positions = {}

        self.static_sprite_path = r"resources\sprites\static_sprites"
        self.anim_sprite_path = r"resources\sprites\animated_sprites"
        add_sprite = self.add_sprite
        add_npc = self.add_npc

        for pos in ((6.131577420285329, 11.410276214115536),(15.486827488749768, 9.023410886629465),
                    (10.542315667941995, 4.601395441669941),(10.378829674186568, 1.403358374889963),
                    (18.14854820875154, 5.923465146187969),(23.47915286748974, 5.850778232918253),
                    (24.760835512255124, 5.42238839957973),(28.30632449769619, 7.980462909788688),
                    (20.731645996615367, 11.164708383716288),(15.985414169479037, 26.510169999789273),
                    (15.858281588588879, 21.198914954460896),(1.4983378341914781, 14.425149012801725),
                    (4.587598180780894, 27.616152438509673)):
            add_sprite(sprite_obj.SpriteObject(game, pos=pos))

        for pos in ((23.309369109510424, 20.04402676667299),(4.608871840768402, 21.073551015067263)):
            add_sprite(sprite_obj.AnimatedSprite(game, self.anim_sprite_path+"/green_light/0.png", pos=pos))

        for pos in ((13.657689992532712, 14.100030574724427),(25.80713143681789, 10.145890782284074),(23.10184135696746, 5.866812395939256)):
            add_sprite(sprite_obj.AnimatedSprite(game, self.anim_sprite_path+"/red_light/0.png", pos=pos))

        for pos in ((6.131577420285329, 11.410276214115536),(15.486827488749768, 9.023410886629465),
                    (10.542315667941995, 4.601395441669941),(10.378829674186568, 1.403358374889963),
                    (18.14854820875154, 5.923465146187969),(23.47915286748974, 5.850778232918253),
                    (24.760835512255124, 5.42238839957973),(28.30632449769619, 7.980462909788688),
                    (20.731645996615367, 11.164708383716288),(15.985414169479037, 26.510169999789273),
                    (15.858281588588879, 21.198914954460896),(1.4983378341914781, 14.425149012801725),
                    (4.587598180780894, 27.616152438509673)):
            add_npc(npc.SoldierNPC(game, pos=pos))

        for pos in ((23.309369109510424, 20.04402676667299),(4.608871840768402, 21.073551015067263)):
            add_npc(npc.CyberDemonNPC(game, pos=pos))

        for pos in ((13.657689992532712, 14.100030574724427),(25.80713143681789, 10.145890782284074),(23.10184135696746, 5.866812395939256)):
            add_npc(npc.CacoDemonNPC(game, pos=pos))

    def check_win(self):
        if not len(self.npc_positions):
            self.game.object_renderer.win()
            pygame.display.flip()
            pygame.time.delay(1500)
            self.game.new_game()

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        for sprite in self.sprite_list:
            sprite.update()
        for npc in self.npc_list:
            npc.update()
        self.check_win()

    def add_npc(self, npc):
        logger = glob.gen
        logger.debug(f"npc {type(npc).__name__} added to the list")
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        logger = glob.gen
        logger.debug(f"Sprite {type(sprite).__name__} added to the list")
        self.sprite_list.append(sprite)
