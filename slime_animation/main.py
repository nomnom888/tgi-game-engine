import sys, os
print(os.path.dirname(__file__))
sys.path.append(r"..")
from tgi import *

fm = FileManager(current_dir=os.path.dirname(__file__))
v2 = Vectors2D()

main_scene = Scene(size=(100,25))

slime_data = fm.load(r'Assets\Animations\slime_idle.txt')
slime_idle = Animation(slime_data, 0.8)
slime = GameObject(scene=main_scene, 
                   position=(5, 20), 
                   states={'idle': slime_idle},
                   layer=1)

floor_data = fm.load(r'Assets\base.txt')
floor = GameObject(scene=main_scene,
                   position=(1, 25),
                   states={'main': floor_data})

sun_data = fm.load(r'Assets\sun.txt')
sun = GameObject(scene=main_scene,
                 position=(4, 1),
                 states={'main': sun_data})

sign_data = fm.load(r'Assets\sign.txt')
sign = GameObject(scene=main_scene,
                  position=(70, 17),
                  states={'main': sign_data})

name = GameObject(scene=main_scene,
                  position=(93, 1),
                  states={'main': 'nomnom'})

class Menu:

    def __init__(self):
        self.menu_scene = Scene(size=(21,10), active=True)

        menu_play_data = fm.load(r'Assets\Menu\menu_play.txt')
        menu_opts_data = fm.load(r'Assets\Menu\menu_opts.txt')
        menu_exit_data = fm.load(r'Assets\Menu\menu_exit.txt')

        self.menu_obj = GameObject(scene    = self.menu_scene,
                                   position = (3,2),
                                   states   = {'play': menu_play_data,
                                               'opts': menu_opts_data,
                                               'exit': menu_exit_data})

menu = Menu()

def on_startup():
    GameUpdate.set_fps(60)

def fix_update(delta):


    # Main Input Components
    key = KeyboardInput.get_key()
    held_keys = KeyboardInput.held_keys

    if menu.menu_scene.active:
        # Controls
        if held_keys != set():

            active_state = menu.menu_obj.active_state_name

            # Menu Movement
            if key == keyboard.Key.up:
                if active_state == 'opts':
                    menu.menu_obj.set_active_state('play')
                elif active_state == 'exit':
                    menu.menu_obj.set_active_state('opts')
            elif key == keyboard.Key.down:
                if active_state == 'play':
                    menu.menu_obj.set_active_state('opts')
                elif active_state == 'opts':
                    menu.menu_obj.set_active_state('exit')
            elif key == keyboard.Key.enter:
                if active_state == 'play':
                    Grapichs.set_active_scene(main_scene)
                elif active_state == 'exit':
                    GameUpdate.exit_program()
            elif key == keyboard.Key.esc:
                GameUpdate.exit_program()

    elif main_scene.active:

        # Controls
        if held_keys != set():

            # Basic Movement
            if keyboard.Key.right in held_keys:
                slime.velocity = v2.sum(slime.velocity, v2.scalar((1, 0), 40*delta))
            if keyboard.Key.left in held_keys:
                slime.velocity = v2.sum(slime.velocity, v2.scalar((-1, 0), 40*delta))
            slime.move_and_accelerate()
            slime.velocity = (0,0)

            # Exit
            if key == keyboard.Key.esc:
                GameUpdate.exit_program()

if __name__ == '__main__':
    GameUpdate.main_loop(on_startup, fix_update)