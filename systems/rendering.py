import math
import pygame
from components.movement import *
from components.rendering import *
from components.special_rendering_tags import *
from general.camera import *


_BASE_ANGLES = {
    Rotation.RIGHT: 0.0,
    Rotation.UP: 90.0,
    Rotation.LEFT: 180.0,
    Rotation.DOWN: 270.0,
}


def _vector_angle(v: pygame.Vector2) -> float:
    return math.degrees(math.atan2(-v.y, v.x)) % 360


def _apply_special_rendering(movement: MovementComponent, sprite: RenderingComponent,
                              special: SpecialRenderingComponent) -> None:
    direction = movement.direction

    if special.rotates_with_direction:
        if direction.length_squared() > 0:
            target_angle = _vector_angle(direction)
            base_angle = _BASE_ANGLES[special.original_rotation_angle]
            sprite.angle = (target_angle - base_angle) % 360
        else:
            sprite.angle = 0.0

    if special.flips_with_direction:
        if direction.x > 0:
            sprite.flip_x = special.original_orientation_x == Rotation.LEFT
        elif direction.x < 0:
            sprite.flip_x = special.original_orientation_x == Rotation.RIGHT


def _draw_sort_key(pos: MovementComponent, sprite: RenderingComponent):
    layer = getattr(sprite, "layer", 0)
    z_index = getattr(sprite, "z_index", None)
    y_key = z_index if z_index is not None else pos.pos.y
    return (layer, y_key)


def render_system(world, screen, camera: Camera):
    renderables = []
    for e in world.entities:
        pos, sprite, special_rendering_component = (
            e.get(MovementComponent),
            e.get(RenderingComponent),
            e.get(SpecialRenderingComponent),
        )
        if not (pos and sprite):
            continue

        if special_rendering_component:
            _apply_special_rendering(pos, sprite, special_rendering_component)

        renderables.append((pos, sprite))

    renderables.sort(key=lambda item: _draw_sort_key(item[0], item[1]))

    for pos, sprite in renderables:
        image = sprite.image
        if not image:
            continue
        w, h = image.get_size()

        screen_x, screen_y = camera.world_to_screen(pos.pos.x, pos.pos.y)

        if camera.zoom != 1.0:
            image = pygame.transform.scale(image, (int(w * camera.zoom), int(h * camera.zoom)))

        if sprite.flip_x:
            image = pygame.transform.flip(image, True, False)

        if sprite.angle != 0.0:
            image = pygame.transform.rotate(image, sprite.angle)

        w, h = image.get_size()
        draw_x = screen_x - w / 2 + sprite.offset.x * camera.zoom
        draw_y = screen_y - h / 2 + sprite.offset.y * camera.zoom

        screen.blit(image, (draw_x, draw_y))