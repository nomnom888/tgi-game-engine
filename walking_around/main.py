import sys, os
print(os.path.dirname(__file__))
sys.path.append(r"..")
from tgi import *

fm = FileManager(current_dir=os.path.dirname(__file__))
v2 = Vectors2D()

sys.path.append(fm.get_abs_path(r'Scenes'))
from first_scene import *

def on_startup():
    GameUpdate.set_fps(60)
    Grapichs.set_active_scene(first_scene)

def fix_update(delta):
    key = KeyboardInput.get_key()
    held_keys = KeyboardInput.held_keys

    if held_keys != set():
        if keyboard.Key.right in held_keys:
            char.velocity = v2.sum(char.velocity, v2.scalar((1, 0), delta*15))
        if keyboard.Key.left in held_keys:
            char.velocity = v2.sum(char.velocity, v2.scalar((-1, 0), delta*15))
        if keyboard.Key.up in held_keys:
            char.velocity = v2.sum(char.velocity, v2.scalar((0, -1), delta*15))
        if keyboard.Key.down in held_keys:
            char.velocity = v2.sum(char.velocity, v2.scalar((0, 1), delta*15))
        char.move_and_accelerate()

    if char.grid_position[1] > 15:
        char.set_position_y = 15

    if char.active_state_name != 'walkr' and char.velocity[0] > 0:
        char.set_active_state('walkr', change_when_over=True)
    elif char.active_state_name != 'walkl' and char.velocity[0] < 0:
        char.set_active_state('walkl', change_when_over=True)
    elif char.velocity[0] == 0:
        char.set_active_state('idle')
    char.velocity = (0, 0)

if __name__ == '__main__':
    GameUpdate.main_loop(on_startup, fix_update)