import pygame

# just base
class Binding:
    def poll(self, events):
        raise NotImplementedError


# pygame things, ex pygame.K_SPACE
class KeyBinding(Binding):
    def __init__(self, key):
        self.key = key

    def poll(self, events):
        return pygame.key.get_pressed()[self.key]
    
# 0=left, 1=middle, 2=right
class MouseButtonBinding(Binding):
    def __init__(self, button):
        self.button = button  

    def poll(self, events):
        return pygame.mouse.get_pressed()[self.button]


# indeces ex (joystick, 0),
class JoyAxisBinding(Binding):
    def __init__(self, joystick, axis, direction=1, threshold=0.5):
        self.joystick = joystick
        self.axis = axis
        self.direction = direction
        self.threshold = threshold

    def poll(self, events):
        if self.joystick is None:
            return False
        value = self.joystick.get_axis(self.axis)
        return value * self.direction > self.threshold


class JoyButtonBinding(Binding):
    def __init__(self, joystick, button):
        self.joystick = joystick
        self.button = button

    def poll(self, events):
        if self.joystick is None:
            return False
        return self.joystick.get_button(self.button)

# up / down
class WheelBinding(Binding):
    def __init__(self, direction="up"):
        self.direction = direction  

    def poll(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                if self.direction == "up" and event.y > 0:
                    return True
                if self.direction == "down" and event.y < 0:
                    return True
        return False


class InputAction:
    def __init__(self, bindings, on_trigger=None):
        self.bindings = bindings
        self.on_trigger = on_trigger

    def execute(self, *args, **kwargs):
        if self.on_trigger:
            self.on_trigger(*args, **kwargs)

    def is_triggered(self, events):
        return any(b.poll(events) for b in self.bindings)

    def check(self, events):
        if self.is_triggered(events):
            self.execute()

class InputMap: 
    def __init__(self, actions : list[InputAction]):
        self.actions = actions

    def _update(self, events):
        for action in self.actions:
            action.check(events)