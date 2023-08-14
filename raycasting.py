import pygame
import math
import settings
from logger import glob
import sprite_obj
from texture import Texture
import traceback

ZERO_AVOIDANCE = 1e-10

class RayCasting:
    def __init__(self, game):
        # Starting the construction log for RayCasting.
        glob.gen.info("Initializing RayCasting...")

        # Initializing game and lists.
        self.game = game
        self.ray_casting_result = []
        self.objects_to_render = []

        # Fetching wall textures from object renderer.
        self.textures = self.game.object_renderer.wall_textures

        # Log information about the number of textures loaded.
        glob.gen.debug(f"Loaded {len(self.textures)} wall textures for RayCasting.")

        # Concluding the initialization log for RayCasting.
        glob.gen.info("RayCasting initialized successfully.")

    def get_objects_to_render(self):
        self.objects_to_render = []

        # Track reported edge cases to avoid repetitive logging
        if not hasattr(self, "_render_edge_cases_reported"):
            self._render_edge_cases_reported = set()

        for ray, values in enumerate(self.ray_casting_result):
            if len(values) != 4:
                if "invalid_value_length" not in self._render_edge_cases_reported:
                    glob.gen.warn(f"Invalid number of values in ray_casting_result for ray {ray}. Expected 4 values, got {len(values)}. Skipping this ray.")
                    self._render_edge_cases_reported.add("invalid_value_length")
                continue

            depth, proj_height, texture_key, offset = values

            if proj_height <= 0:
                if "non_positive_proj_height" not in self._render_edge_cases_reported:
                    glob.gen.warn(f"Non-positive projection height encountered for ray {ray}. This might lead to visual glitches.")
                    self._render_edge_cases_reported.add("non_positive_proj_height")
                continue

            try:
                texture:Texture = self.game.object_renderer.get_wall_texture(texture_key)

                if proj_height < settings.GAME.SCREEN_HEIGHT:
                    wall_column = texture.texture.subsurface(
                        offset * (settings.TEXTURE.TEXTURE_SIZE - settings.SCREEN.SCALE), 0,
                        settings.SCREEN.SCALE, settings.TEXTURE.TEXTURE_SIZE
                    )
                    wall_column = pygame.transform.scale(wall_column, (settings.SCREEN.SCALE, abs(proj_height)))
                    wall_pos = (ray * settings.SCREEN.SCALE, settings.GAME.HALF_HEIGHT - proj_height // 2)
                else:
                    texture_height = settings.TEXTURE.TEXTURE_SIZE * settings.GAME.SCREEN_HEIGHT / proj_height
                    wall_column = texture.texture.subsurface(
                        offset * (settings.TEXTURE.TEXTURE_SIZE - settings.SCREEN.SCALE),
                        settings.TEXTURE.HALF_TEXTURE_SIZE - texture_height // 2,
                        settings.SCREEN.SCALE, texture_height
                    )
                    wall_column = pygame.transform.scale(wall_column, (settings.SCREEN.SCALE, settings.GAME.SCREEN_HEIGHT))
                    wall_pos = (ray * settings.SCREEN.SCALE, 0)

                self.objects_to_render.append((depth, wall_column, wall_pos))

            except Exception as e:
                if "texture_error" not in self._render_edge_cases_reported:
                    error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
                    glob.gen.error(f"Error while processing texture for ray {ray}. Details: {error_message}")
                    self._render_edge_cases_reported.add("texture_error")

    def ray_cast(self):
        self.ray_casting_result = []
        texture_vert, texture_hor = 1, 1  # Fallback textures
        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.game.player.angle - settings.RayCast.HALF_FOV + 0.0001

        if not hasattr(self, "_edge_cases_reported"):
            self._edge_cases_reported = set()

        for ray in range(settings.RayCast.NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            if sin_a == 0 or cos_a == 0:
                if "sin_cos_zero" not in self._edge_cases_reported:
                    glob.gen.warn("Encountered sin or cos value of zero, potential division by zero issue.")
                    self._edge_cases_reported.add("sin_cos_zero")
                continue

            # horizontals
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a
            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(settings.RayCast.MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.game.map.world_map:
                    texture_hor = self.game.map.world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            # verticals
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a
            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(settings.RayCast.MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.game.map.world_map:
                    texture_vert = self.game.map.world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            # depth, texture offset
            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor

            if depth <= 0:
                if "negative_depth" not in self._edge_cases_reported:
                    glob.gen.warn("Negative or zero depth encountered. Ensure proper calculations.")
                    self._edge_cases_reported.add("negative_depth")
                depth = 0.0001  # Setting to a very small positive value to avoid division by zero

            # remove fishbowl effect
            depth *= math.cos(self.game.player.angle - ray_angle)

            # projection
            proj_height = settings.SCREEN.DISTANCE / (depth + 0.0001)

            # ray casting result
            self.ray_casting_result.append((depth, proj_height, texture, offset))

            if self.game.game_console.view_raycast_player:
                pygame.draw.line(self.game.screen, 'yellow', (100 * ox, 100 * oy),
                                 (100 * ox + 100 * depth * cos_a, 100 * oy + 100 * depth * sin_a), 2)

            ray_angle += settings.RayCast.DELTA_ANGLE

    def update(self):
        self.ray_cast()
        self.get_objects_to_render()
