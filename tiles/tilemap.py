import pygame
from scenes.sceneObject import *
from general.camera import *
from tiles.ruleTile import *
from tiles.gridLayout import GridLayout, SquareGridLayout

from tiles.tile import *


class Tilemap(SceneObject):

    def __init__(self, tileset, tile_width, tile_height,
                 map_width, map_height, chunk_size=16, layout: GridLayout = None):
        super().__init__()

        self.tile_width = tile_width
        self.tile_height = tile_height
        self.map_width = map_width
        self.map_height = map_height
        self.chunk_size = chunk_size

        # Defaults to the existing square behavior; pass HexGridLayout() for a hex map.
        self.layout = layout if layout is not None else SquareGridLayout()

        self.grid = [[None for _ in range(map_width)]
                     for _ in range(map_height)]

        self.tileset = tileset

        self.chunks = {}
        self._dirty_chunks = set()

    def get_placed(self, x, y):
        if not (0 <= x < self.map_width and 0 <= y < self.map_height):
            return None
        return self.grid[y][x]

    def set_tile(self, x, y, tile):
        if not (0 <= x < self.map_width and 0 <= y < self.map_height):
            return
        self.grid[y][x] = tile
        self._mark_dirty_around(x, y)

    def fill(self, tile):
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.grid[y][x] = tile
        for cy in range(0, self.map_height, self.chunk_size):
            for cx in range(0, self.map_width, self.chunk_size):
                self._dirty_chunks.add((cx // self.chunk_size, cy // self.chunk_size))

    def _mark_dirty_around(self, x, y):
        for ny in range(y - 1, y + 2):
            for nx in range(x - 1, x + 2):
                if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
                    self._dirty_chunks.add((nx // self.chunk_size, ny // self.chunk_size))

    def _rebuild_chunk(self, chunk_x, chunk_y):
        px_w, px_h = self.layout.chunk_pixel_size(self.chunk_size, self.tile_width, self.tile_height)
        surface = pygame.Surface((int(px_w), int(px_h)), pygame.SRCALPHA)

        start_x = chunk_x * self.chunk_size
        start_y = chunk_y * self.chunk_size
        end_x = min(start_x + self.chunk_size, self.map_width)
        end_y = min(start_y + self.chunk_size, self.map_height)

        chunk_origin_x, chunk_origin_y = self.layout.tile_to_pixel(start_x, start_y, self.tile_width, self.tile_height)

        for ty in range(start_y, end_y):
            row = self.grid[ty]
            for tx in range(start_x, end_x):
                placed = row[tx]
                if placed is None:
                    continue
                visual = placed.get_visual(self, tx, ty)
                sprite = self.tileset[visual.sprite_id]
                if visual.flip_h or visual.flip_v:
                    sprite = pygame.transform.flip(sprite, visual.flip_h, visual.flip_v)
                if visual.rotation:
                    sprite = pygame.transform.rotate(sprite, -visual.rotation)

                tile_px_x, tile_px_y = self.layout.tile_to_pixel(tx, ty, self.tile_width, self.tile_height)
                local_x = tile_px_x - chunk_origin_x
                local_y = tile_px_y - chunk_origin_y
                surface.blit(sprite, (local_x, local_y))

        self.chunks[(chunk_x, chunk_y)] = surface

    def _flush_dirty_chunks(self):
        if not self._dirty_chunks:
            return
        for chunk_coord in self._dirty_chunks:
            self._rebuild_chunk(*chunk_coord)
        self._dirty_chunks.clear()

    def draw(self, screen):
        self._flush_dirty_chunks()

        camera = Camera.get_instance()
        origin = self.getWorldPosition()

        for (cx, cy), chunk_surface in self.chunks.items():
            start_x = cx * self.chunk_size
            start_y = cy * self.chunk_size
            chunk_origin_x, chunk_origin_y = self.layout.tile_to_pixel(start_x, start_y, self.tile_width, self.tile_height)

            world_x = origin.x + chunk_origin_x
            world_y = origin.y + chunk_origin_y
            rect = pygame.Rect(world_x, world_y, chunk_surface.get_width(), chunk_surface.get_height())
            screen_rect = camera.apply(rect)

            if screen_rect.right < 0 or screen_rect.left > camera.screen_width:
                continue
            if screen_rect.bottom < 0 or screen_rect.top > camera.screen_height:
                continue

            if camera.zoom != 1.0:
                scaled = pygame.transform.scale(chunk_surface, (screen_rect.width, screen_rect.height))
                screen.blit(scaled, (screen_rect.x, screen_rect.y))
            else:
                screen.blit(chunk_surface, (screen_rect.x, screen_rect.y))

        super().draw(screen)