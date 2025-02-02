import sys, os
print(os.path.dirname(__file__))
sys.path.append(r"..")
from tgi import *

first_scene = Scene(size=(102,27))

fm = FileManager(current_dir=os.path.dirname(__file__))

char_idle = fm.load(r'Assets\char.txt')
char_walkr = Animation(fm.load(r'Assets\char_walkr.txt'), 0.3)
char_walkl = Animation(fm.load(r'Assets\char_walkl.txt'), 0.3)

char = GameObject(first_scene,
                  (2,16),
                  {'idle': char_idle,
                   'walkr': char_walkr,
                   'walkl': char_walkl},
                   collider_relative=((1,1),(3,3)),
                   layer=10,
                   style='\x1b[1m')

cenabet = fm.load(r'Assets\cenabet.txt')

cenabet = GameObject(first_scene,
                     (18,6),
                     {'main': cenabet},
                     style='\x1b[1m\x1b[38;5;146m')

hat = fm.load(r'Assets\hat.txt')

hat = GameObject(first_scene,
                 (-1,-1),
                 {'main': hat},
                 relative_to=char,
                 style='\x1b[36m',
                 layer=10)

doner = Animation(fm.load(r'Assets\döner.txt'), 0.5)

doner = GameObject(first_scene,
                   (8,6),
                   {'main': doner},
                   relative_to=cenabet,
                   style='\x1b[38;5;231m')

flag = fm.load(r'Assets\flag.txt')

flag = GameObject(first_scene,
                    (67,7),
                    {'main': flag},
                    style='\x1b[38;5;196m')


road1 = fm.load(r'Assets\road1.txt')

road1 = GameObject(first_scene,
                 (1,19),
                 {'main': road1},
                 style='\x1b[38;5;142m')

road12 = fm.load(r'Assets\road1.txt')

road12 = GameObject(first_scene,
                  (1+26,19),
                  {'main': road12},
                  style='\x1b[38;5;142m')

road2 = fm.load(r'Assets\road2.txt')

road2 = GameObject(first_scene,
                 (1+2*26,19),
                 {'main': road2},
                 style='\x1b[38;5;142m')

road13 = fm.load(r'Assets\road1.txt')

road13 = GameObject(first_scene,
                  (1+2*26+24,19),
                  {'main': road13},
                  style='\x1b[38;5;142m')