from components.movement import *
import pygame

MAX_HEARING_DISTANCE = 700.0
MIN_HEARING_DISTANCE = 100.0

MAX_PAN_DISTANCE = 400.0  # horizontal distance at which panning maxes out (full one-ear)


def _distance_to_volume(distance: float) -> float:
    if distance <= MIN_HEARING_DISTANCE:
        return 1.0
    if distance >= MAX_HEARING_DISTANCE:
        return 0.0
    t = (distance - MIN_HEARING_DISTANCE) / (MAX_HEARING_DISTANCE - MIN_HEARING_DISTANCE)
    return 1.0 - t


def _pan_from_offset(dx: float) -> tuple[float, float]:
    t = max(-1.0, min(1.0, dx / MAX_PAN_DISTANCE))
    left_gain = min(1.0, 1.0 - t) if t > 0 else 1.0
    right_gain = min(1.0, 1.0 + t) if t < 0 else 1.0
    return left_gain, right_gain


def sound_system(world, sound_effect_level):
    player_pos = world.player_entity.get(MovementComponent).pos

    for e in world._sound_effect_events:
        if e.sfx is None:
            continue

        offset = e.at - player_pos
        distance = offset.length()
        distance_volume = _distance_to_volume(distance)

        final_volume = distance_volume * sound_effect_level
        final_volume = max(0.0, min(1.0, final_volume))

        if final_volume <= 0.0:
            continue

        left_gain, right_gain = _pan_from_offset(offset.x)

        channel = pygame.mixer.find_channel()
        if channel is None:
            continue  

        channel.set_volume(final_volume * left_gain, final_volume * right_gain)
        channel.play(e.sfx)

    world._sound_effect_events.clear()