import pygame
import sys
import settings
import map
import player
import raycasting
import object_renderer
import sprite_obj
import object_handler
import weapon
import sound
import pathfinding

import dev_console

import logger
from logger import glob
import traceback

class Game:
    def __init__(self):
        # Start the game initialization logging.
        glob.gen.info("Starting Game Initialization...")

        # Initialize pygame.
        pygame.init()
        glob.gen.debug("Pygame initialized")

        # Get the screen size of the current monitor.
        screen_info = pygame.display.Info()
        screen_width, screen_height = screen_info.current_w, screen_info.current_h
        settings.GAME.update_screen_size(screen_width, screen_height)
        glob.gen.debug(f"Detected Screen Dimensions: Width: {screen_width}, Height: {screen_height}")

        # Set the display mode to full screen.
        self.screen = pygame.display.set_mode(settings.GAME.SCREEN_SIZE, pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        screen_size = settings.GAME.SCREEN_SIZE
        glob.gen.debug(f"Game Window Size set to: {screen_size}")

        # Set FPS target for the game.
        glob.gen.debug(f"Target FPS: {settings.GAME.TARGET_FPS}")
        self.clock = pygame.time.Clock()
        self.delta_time = 1

        # Log width and height factors.
        width_factor = settings.GAME.WIDTH_FACTOR
        height_factor = settings.GAME.HEIGHT_FACTOR
        glob.gen.debug(f"WIDTH/HEIGHT Factor: {width_factor}, {height_factor}")

        # Mark the game as active.
        self.game_active = True
        glob.gen.debug("Game marked as active.")


        self.global_trigger = False
        self.global_event = pygame.USEREVENT + 0
        pygame.time.set_timer(self.global_event, 40)

        # Start a new game.
        self.new_game()

        # Conclude the game initialization logging.
        glob.gen.info("Game Initialization Completed Successfully.")

    def new_game(self):
        glob.gen.info("Starting New Game Setup...")

        # Initialize the game map.
        self.map = map.Map(self)
        glob.gen.debug("Game Map initialized")

        # Initialize the player.
        self.player = player.Player(self)
        glob.gen.debug("Player initialized")

        # Initialize the object renderer.
        self.object_renderer = object_renderer.ObjectRenderer(self)
        glob.gen.debug("Object Renderer initialized")

        # Initialize the ray casting.
        self.raycasting = raycasting.RayCasting(self)
        glob.gen.debug("Ray Casting initialized")

        self.object_handler = object_handler.ObjectHandler(self)
        self.weapon = weapon.Weapon(self)

        self.pathfinding = pathfinding.PathFinding(self)

        self.sound = sound.Sound(self)

        glob.gen.info("New Game Setup Completed Successfully.")


    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        pygame.display.flip()
        self.delta_time = self.clock.tick(settings.GAME.TARGET_FPS)
        target_fps = settings.GAME.TARGET_FPS
        pygame.display.set_caption(f'{self.clock.get_fps() :.1f} FPS {f"/ {target_fps}" if target_fps != 0 else ""}')

    def draw(self):
        if self.game_console.render_3d:
            self.object_renderer.draw()
            self.weapon.draw()

        if self.game_console.view_map:
            self.map.draw()
        if self.game_console.view_raycast_player:
            self.player.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                glob.gen.critical("[Event] Player initiated window close.")
                self.terminate_game()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                glob.gen.critical("[Event] Player pressed the ESCAPE key.")
                self.terminate_game()

            elif event.type == self.global_event:
                self.global_trigger = True

            self.player.single_fire_event(event)

    def terminate_game(self):
        glob.gen.info("[System] Beginning the shutdown process.")
        self.game_active = False
        pygame.quit()
        glob.gen.info("[System] Pygame successfully terminated.")
        sys.exit()

    def run(self):
        glob.gen.info("[System] Game loop initiated.")
        start_time = pygame.time.get_ticks()
        while self.game_active:
            self.check_events()
            self.update()
            self.draw()

class GameHandler(dev_console.CommandHandler):
    def __init__(self, script: Game):
        super().__init__(script, "#")
        self.position_stamps = {}
        self.let_god_shoot = False
        self.be_god = False
        self.no_clip = False
        self.view_map = False
        self.view_raycast_player = False
        self.view_raycast_enemy = False
        self.render_3d = True
        self.script.game_console = self

    def call(self, command: str, log):
        command = command.removeprefix(self.id + " ")

        def set_boolean_attribute(attr_name, cmd_split, log):
            if len(cmd_split) != 2:
                log.warn(f"Please provide a value for {attr_name}.")
                return -1
            setattr(self, attr_name, "1" in cmd_split[1])
            log.info(f"{attr_name.replace('_', ' ')} set to {getattr(self, attr_name)}")
            return 1

        if command == "soft-exit":
            self.script.game_active = False
            return 1

        # Stamp logic
        elif command.startswith("stamp -"):
            _, name = command.split("-", 1)
            if not name:
                log.warn("Please provide a name for the stamp.")
                return -1
            self.position_stamps[name] = self.script.player.pos
            log.info(f"Stamped at position {self.script.player.pos}")
            return 1
        elif command == "stamp clear":
            self.position_stamps.clear()
            log.info("Cleared all position stamps.")
            return 1
        elif command.startswith("# stamp remove "):
            _, name = command.split("# stamp remove ", 1)
            if name in self.position_stamps:
                del self.position_stamps[name]
                log.info(f"Removed stamp {name}")
            else:
                log.warn(f"No stamp found with name {name}")
                return -1
            return 1
        elif command == "stamp show":
            log.info("Stamped Positions:")
            for i, (key, value) in enumerate(self.position_stamps.items()):
                log.info(f"<{i}> {key}: {value}")
            return 1
        elif command == "stamp show tuple":
            log.info("Stamped tuple Positions:")
            result = "(" + ",".join(str(x) for x in self.position_stamps.values()) + ")"
            log.info(f"result: " + result)
            return 1
        # Cheats and Debugs
        elif any(command.startswith(prefix) for prefix in ["be-god", "let-god-shoot:", "no-clip:", "view-map:", "ray-cast-player:", "ray-cast-enemy:", "render-3d:"]):
            cmd_name, _ = command.split(":", 1)
            attr_name = cmd_name.replace('-', '_').replace(':', '')
            return set_boolean_attribute(attr_name, command.split(":", 1), log)
        else:
            log.warn(f"Unknown command: {command}")
            return -1

    @dev_console.CommandHandler.help_call
    def help(self):
        return "\n".join([
            f"{self.id} soft-exit - stop the game and close window",
            "\nStamps:",
            f"{self.id} stamp -<name> - set a stamp",
            f"{self.id} stamp clear - remove all stamps",
            f"{self.id} stamp remove <name> - remove a specific stamp",
            f"{self.id} stamp show - list all stamps in their order of creation",
            "\nCheats:",
            f"{self.id} let-god-shoot:<1 | 0> - toggle rapid firing",
            f"{self.id} be-god-shoot:<1 | 0> - toggle god mode",
            "\nDebug:",
            f"{self.id} no-clip:<1 | 0> - toggle noclip mode",
            f"{self.id} view-map:<1 | 0> - toggle 2D mini-map view",
            f"{self.id} render-3d:<1 | 0> - toggle 3D game view",
            f"{self.id} ray-cast-player:<1 | 0> - toggle player raycast visualization",
            f"{self.id} ray-cast-enemy:<1 | 0> - toggle enemy raycast visualization"
        ])

def main():
    try:
        # Initialize the logger.
        log = logger.create_logger("gen", "game.log")
        logger.glob.gen = log
        glob.gen.info("[System] Logger 'gen' initialized and globally referenced.")
        # Initialize and run the game.
        game = Game()
        console = dev_console.Console(game, log, dev_console)
        console.register_handler(GameHandler(game))
        glob.gen.info("[System] Game instance created successfully. Starting game loop...")
        console.run()
        game.run()
    except Exception as e:
        error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        glob.gen.critical(f"[Error] Critical error encountered:\n{str(e)} {error_message}\nShutting down...")
        # Potentially add any cleanup operations here.
    finally:
        game.terminate_game()

if __name__ == "__main__":
    main()