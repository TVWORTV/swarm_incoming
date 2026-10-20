# SWARM INCOMING

A top-down, wave-survival action game written in Python with Pygame. You control a lone character, hold out against ever-growing swarms of insects, collect experience, and choose upgrades as you level up. The game runs on desktop and in the browser as a WebAssembly build.

The project is as much an architecture exercise as a game: the codebase is built around a custom entity-component-system, spatial-hash collision detection, object pooling, and a data-driven content pipeline.

## Gameplay

- Move around a tiled arena while enemies spawn from beyond the screen and converge on you.
- Weapons fire automatically; kill enemies to drop experience pickups.
- Collect experience to level up, then pick one of three randomly offered abilities.
- Survive as long as possible while spawn rates and enemy types escalate with time and points.
- Choose a difficulty level that scales enemy speed, size, damage, and health.

### Controls

| Action | Input |
| --- | --- |
| Move | WASD, arrow keys, or gamepad left stick |
| Zoom | Mouse wheel, or gamepad shoulder buttons |

## The Core of the Project

Everything in the game is an `Entity`: a bare object with an id, an active flag, and a dictionary of components keyed by type. Players, enemies, projectiles, experience pickups, and emitters all use the same structure.

Behavior lives in systems, plain functions that run each frame over the world's entities. The main loop in `main.py` is essentially a pipeline:

```
player control -> enemy AI -> movement -> emitting -> projectiles -> animation
-> spatial grid build -> collision -> health -> death -> text spawning -> rendering
```

Systems never call each other directly. When something happens (damage dealt, an enemy dies, a projectile spawns, a sound should play), a system appends an event to a queue on the world, and the relevant system consumes it later in the frame. The world clears those queues at the end of each frame.

This keeps each system small and testable, and makes adding new content mostly a matter of writing new definitions rather than new control flow.

## Project Structure

```
main.py                  Entry point, scene setup, main async loop
consts.py                Tunable gameplay and display constants
save_manager.py          Cross-platform settings persistence
components/              Pure data: movement, collider, health, animation, emitter, projectile, ...
systems/                 Per-frame logic: collision, movement, rendering, emitting, death, sound, ...
events/                  Event types: damage, death, projectile spawn, sound effect
pools/                   Object pools for enemies, projectiles, damage text, experience pickups
data_and_definitions/    Data-driven enemy and projectile definitions
abilities/               Ability definitions, effects, and the resolver that applies them
world/                   World state, entity registry, and time/point-based progression
scenes/                  Scene base class, scene manager, and scene objects
UI/                      Custom UI toolkit: buttons, sliders, dropdowns, bars, nine-slice, layout groups
tiles/                   Rule-based tilemap and grid layout
general/                 Entity, camera, asset loading, input actions
utilities/               Spawning and reset helpers for enemies, projectiles, and text
files/                   Sprites, fonts, music, and sound effects
build/                   Web (WebAssembly) build output
```

## Programming Techniques Used

### Entity-Component-System architecture
Entities are generic containers, components are data-only classes, and systems are functions operating on component combinations. The separation allows new enemy types, projectiles, and effects to be composed rather than subclassed.

### Spatial-hash collision detection
Collision uses a uniform grid (`CELL_SIZE = 16`) rebuilt every frame. Each entity is bucketed by position, and only entities in the same or neighboring cells are compared, avoiding the O(n^2) cost of naive pair checks. Pairs are de-duplicated, and circle colliders handle the player, enemy, projectile, and experience-pickup interactions. Overlapping enemies are gently pushed apart so swarms do not stack into a single point. A debug overlay (`render_spatial_grid`) visualizes cell occupancy.

### Object pooling
Enemies, projectiles, floating damage text, and experience pickups are allocated up front and recycled through pools (`pools/`). A pool hands out an inactive entity when one is available, grows only when exhausted, and resets entities on return. This reduces allocation and garbage-collection pressure during large swarms.

### Event-driven communication
Damage, death, projectile spawn, and sound effect events are queued on the world and processed by dedicated systems. This decouples the code that detects a hit from the code that applies damage, spawns text, plays sounds, or drops loot.

### Data-driven content
Enemies and projectiles are described by definition dataclasses (speed, health, damage, pierce count, crit rate, hit cooldown, collision sound, and so on). Spawning code builds entities from these definitions, so balance and content changes do not require logic changes.

### Ability and upgrade system
Abilities are declarative: each has dependencies, exclusions, and a list of effects (`AddEmitter`, `ModifyEmitter`, `RemoveAbility`, `StatChange`). An `AbilityResolver` determines which abilities are currently available, offers three random choices on level-up, falls back to a repeatable pool, and applies or reverses effects using structural pattern matching (`match` / `case`). The design notes in `abilities/abilities.txt` describe four-tier upgrade chains for abilities such as toxic sludge, aim bot, laser, and armor.

### Time- and point-based progression
`WorldProgression` uses two independent bracket tables: one maps survival time to spawn interval, the other maps accumulated points to the list of enemy types that may spawn. Points are earned over time and on kills, so difficulty ramps with both survival time and player success. Experience thresholds grow by a multiplier on each level.

### Custom UI toolkit
Rather than relying on a UI library, the project implements its own buttons, sliders, dropdowns, progress bars, images, text rendering, layout groups, and nine-slice panels, all managed through a scene system with draw-order sorting and add/remove lifecycle hooks.

### Input abstraction
`InputAction` maps one logical action to any number of bindings (`KeyBinding`, `MouseButtonBinding`, `WheelBinding`, `JoyAxisBinding`, `JoyButtonBinding`), so keyboard, mouse, and gamepad all drive the same game logic without special cases.

### Tilemap and camera
A rule-based tile system and grid layout build the arena. The camera follows the player with smoothing, supports zoom with minimum and maximum limits, and converts between world and screen space.

### Cross-platform persistence
`saveManager` stores music volume, sound effect volume, and difficulty. On desktop it writes JSON to the user's config directory using a temp-file-and-replace pattern to avoid corrupted saves; in the browser it uses `localStorage`. Failures fall back to defaults instead of crashing.

### Async main loop and web deployment
The main loop is an `async` function that yields each frame with `await asyncio.sleep(0)`, which allows the same code to run natively and inside the browser through Pygbag, which packages the game as a WebAssembly build served from `build/web`.

## Running the Game

Requirements:

- Python 3.12 or newer
- `pygame`
- `platformdirs` (optional, used for the desktop save location)

```
pip install pygame platformdirs
python main.py
```

### Web build

The game can be packaged for the browser with Pygbag:

```
pip install pygbag
pygbag .
```

A prebuilt web version is included under `build/web`.

## Possible Next Steps

- Add automated tests for the collision and progression systems.
- Expand the enemy roster and boss encounters through new definitions.
- Add a requirements file and continuous-integration build for the web version.
