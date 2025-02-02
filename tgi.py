import atexit
import sys
from math import fabs, trunc
from time import time
from sys import stdout
from os import system, get_terminal_size, path, chdir
from pynput import keyboard
from pygame import mixer

class Scene:
    
    def __init__(self, size, active=False, within_scene_position=(1, 1)):
        self.container = []
        self.size = size
        self.columns, self.rows = size
        self.active = active
        self.within_scene_position = within_scene_position
        if active:
            Grapichs.set_active_scene(self)

    def clear(self):
        self.container = []

class MovingObject2D:
    
    def __init__(self, position, velocity, acceleration, collider_relative):
        self.abs_position = position
        self.grid_position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.collider_relative = collider_relative

    def move_and_accelerate(self):
        self.velocity = Vectors2D.sum(self.velocity, self.acceleration)
        self.abs_position, self.grid_position = Movement2D.move(self.velocity, self.abs_position, self.grid_position)
        for obj in self.relative_objects:
            obj.abs_position, obj.grid_position = (Vectors2D.sum(self.abs_position, obj.position),
                                                   Vectors2D.sum(self.grid_position, obj.position))

    def set_position_x(self, x):
        for obj in self.relative_objects:
            obj.abs_position = (x, obj.abs_position[1])
            obj.grid_position = (x, obj.grid_position[1])
        self.abs_position = (x, self.abs_position[1])
        self.grid_position = (x, self.grid_position[1])

    def set_position_y(self, y):
        for obj in self.relative_objects:
            obj.abs_position = (obj.abs_position[0], y)
            obj.grid_position = (obj.grid_position[0], y)
        self.abs_position = (self.abs_position[0], y)
        self.grid_position = (self.grid_position[0], y)

    def set_position(self, position):
        for obj in self.relative_objects:
            obj.abs_position = Vectors2D.sum(position, obj.position)
            obj.grid_position = Vectors2D.sum(position, obj.position)
        self.abs_position = position
        self.grid_position = position

    def get_collider(self, obj):
        return (Vectors2D.sum(obj.collider_relative[0], obj.grid_position, (-1, -1)),
                Vectors2D.sum(obj.collider_relative[1], obj.grid_position, (-1, -1)))

    def is_colliding(self, obj):
        collider = self.get_collider(self)
        obj_collider = self.get_collider(obj)
        x_collision = obj_collider[0][0] <= collider[1][0] and collider[0][0] <= obj_collider[1][0]  
        y_collision = obj_collider[0][1] <= collider[1][1] and collider[0][1] <= obj_collider[1][1]
        if x_collision and y_collision: return True
        else: return False

class GameObject(MovingObject2D):

    def __init__(self, scene, position, states: dict, relative_to=None, 
                 hide=False, layer=0, style=None, keep_spaces=False,
                 velocity=(0, 0), acceleration=(0, 0), collider_relative=((1,1), (2,2))):
        super().__init__(position, velocity, acceleration, collider_relative)
        self.position = position
        self.relative_objects = []
        if relative_to != None:
            self.grid_position = Vectors2D.sum(position, relative_to.grid_position)
            relative_to.relative_objects.append(self)
        self.keep_spaces = keep_spaces
        self.hide = hide
        self.layer = layer
        self.states = states
        self.style = style
        self.active_state_name = tuple(states.keys())[0]
        self.active_state = states[self.active_state_name]
        self.scene = scene
        self.set_scene(scene)

    def set_scene(self, scene):
        if scene != self.scene:
            self.scene.container.remove(self)
            self.scene = scene
        for index, game_object in enumerate(scene.container):
            if game_object.layer > self.layer:
                return scene.container.insert(index, self)
        return scene.container.append(self)

    def set_active_state(self, state_name, change_when_over=False):
        target_state = self.states[state_name]
        if type(self.active_state) == Animation:
            if change_when_over:
                self.active_state.game_object = self
                self.active_state.new_state_name = state_name
                self.active_state.change_when_over = True
            else:
                self.active_state.frame_counter = 0
                self.active_state.timer = 0
                self.active_state_name = state_name
                self.active_state = target_state
        elif type(self.active_state) == str:
                self.active_state_name = state_name
                self.active_state = target_state

    def update_state(self, state_name, new_value):
        self.states[state_name] = new_value
        if state_name == self.active_state_name:
            self.active_state = new_value

    def remove_from_scene(self):
        self.scene.container.remove(self)
    
    def delete(self):
        self.scene.container.remove(self)
        del self

class GameUpdate:

    running = True
    chdir(path.dirname(__file__))

    @staticmethod
    def start():
        system('cls||clear') # Clears screen when first ran 
                             # Also fixes windows cmd bug with ansi sequences
        print("testsetsetsetsetsetsetsetset")
        CursorHandler.reset_cursor_position()
        KeyboardInput.start_listening()
        atexit.register(KeyboardInput.stop_listening)
        stdout.write('\x1b[?25l') # Hides cursor
        # atexit.register(CursorHandler.clear)

    @classmethod
    def set_fps(cls, fps):
        cls.fps = fps
        cls.delta_seconds = 1/fps

    @classmethod
    def precise_sleep(cls, secs):
        end_time = time() + secs
        while time() < end_time:
            pass

    @classmethod
    def update_end_sleep(cls, update_time):
        sleep_time = cls.delta_seconds - update_time
        cls.precise_sleep(sleep_time)

    @staticmethod
    def exit_program():
        exit()

    @classmethod
    def main_loop(cls, on_startup, fix_update):
        cls.start()
        on_startup()
        while True:
            st = time()
            fix_update(delta=cls.delta_seconds)
            display = Grapichs.render()
            Grapichs.stylize(display)
            Grapichs.print_out(display())
            et = time()
            update_time = et - st
            cls.update_end_sleep(update_time)

class FileManager:
    
    def __init__(self, current_dir): # path.dirname(__file__)
        self.current_dir = current_dir

    def get_abs_path(self, relative_path):
        return r'{}'.format(path.join(self.current_dir, relative_path))

    # @staticmethod
    # def get_abs_path(relative_path):
        # try:
            # base_path = sys._MEIPASS2
        # except Exception:
            # base_path = path.abspath('.')
        # return path.join(base_path, relative_path)

    def load(self, relative_path):
        with open(self.get_abs_path(relative_path), encoding='utf-8') as file:
            return file.read()

    def save(self, relative_path, text):
        with open(self.get_abs_path(relative_path), 'w') as file:
            file.write(text)


class TimedEvent:

    def __init__(self, time_seconds, event, only_once=False):
        self.time = time_seconds
        self.event = event
        self.timer = 0
        self.only_once = only_once
        self.do_nothing = False

    def __call__(self, default_return=None, *args, **kwargs):
        if self.do_nothing: 
            return default_return
        self.timer += GameUpdate.delta_seconds
        if self.timer >= self.time:
            self.timer -= self.time
            if self.only_once: 
                self.do_nothing = True
            return self.event(*args, **kwargs)
        else: return default_return

class Animation(TimedEvent):

    def __init__(self, text, duration_seconds):
        self.frames = []
        self.frame_counter = 0
        self.change_when_over = False
        self.new_state_name = None
        self.game_object = None
        self.text = text
        self.duration_seconds = duration_seconds
        self.insert_frames(self.text)
        self.frame_number = len(self.frames)
        self.active_frame = self.frames[self.frame_counter]    
        super().__init__(time_seconds=self.duration_seconds/self.frame_number, event=self.set_active_frame)

    def insert_frames(self, text):
        split_text = text.split('%')[1:-1]
        for frame in split_text:
            split_frame = frame.split('\n')
            repeat = int(split_frame.pop(0).strip(' '))
            split_frame = split_frame[:-1] # Removes \n at the end of the frame
            frame = '\n'.join(split_frame)
            for _ in range(repeat):
                self.frames.append(frame)

    def set_active_frame(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_number:
            self.frame_counter = 0
            if self.change_when_over:
                self.timer = 0
                self.change_when_over = False
                self.game_object.active_state_name = self.new_state_name
                self.game_object.active_state = self.game_object.states[self.new_state_name]
        self.active_frame = self.frames[self.frame_counter]

class CursorHandler:

    @staticmethod
    def set_cursor_position(x, y):
        stdout.write(f'\x1b[{y};{x}H')

    @staticmethod
    def move_curser_relative(up=0, down=0, left=0, right=0):
        stdout.write(f'\033[{up}A\033[{down}B\033[{right}C\033[{left}D')

    @staticmethod
    def reset_cursor_position():
        stdout.write("\033[H")

    @staticmethod
    def clear():
        stdout.write('\033[2J\033[3J')

class Grapichs(CursorHandler):
    
    active_scene = None

    @classmethod
    def render(cls, scene=None):
        if scene == None:
            scene = cls.active_scene
        columns, rows = scene.size
        borders = ('┌' + '─'*columns + '┐\n') + ('│' + ' '*columns + '│\n')*rows + ('└' + '─'*columns + '┘')
        display = AsciiImage(string=borders)

        for obj in scene.container:
            if type(obj) == Scene:
                within_scene = obj
                text = cls.render(scene=within_scene)
                display.cursor_position = Vectors2D.sum(within_scene.within_scene_position, (1, 1))
                display.overwrite(text)
                continue
            else: game_object = obj  

            if game_object.hide: 
                continue

            item = game_object.active_state
            if type(item) == Animation:
                animation = item
                animation()
                display.cursor_position = Vectors2D.sum(game_object.grid_position, (1, 1))
                display.overwrite(animation.active_frame)
            elif type(item) == str:
                text = item
                display.cursor_position = Vectors2D.sum(game_object.grid_position, (1, 1))
                display.overwrite(text)
        return display

    @classmethod
    def stylize(cls, display):

        ascii_codes = [] # [[y, [x, style], [x+1, style], ...], [y+1, ...], ...]

        for obj in reversed(cls.active_scene.container):
            if type(obj) == Scene:
                pass
            else: game_object = obj

            if game_object.hide: continue

            if game_object.style != None:
                style = game_object.style
                item = game_object.active_state
                if type(item) == Animation:
                    text = item.active_frame
                elif type(item) == str:
                    text = item

                x, y = game_object.grid_position
                split_text = text.split('\n')
                # Checks if line number already exists
                for line in split_text:
                    line_found = False
                    for index, line_codes in enumerate(ascii_codes):
                        if line_codes[0] == y:
                            line_found = True
                            break
                    if not line_found:
                        ascii_codes.append([y])
                        index = -1

                    if not obj.keep_spaces: space_num = display.count_spaces(line)
                    else: space_num = 0
                    x = game_object.grid_position[0] + space_num - 1
                    for char in line[space_num:]:
                        x += 1
                        tile_occupied = False
                        for item in ascii_codes[index][1:]:
                            if item[0] == x:
                                tile_occupied = True
                                break
                        if tile_occupied: continue

                        position_style = [x, style]
                        ascii_codes[index].append(position_style)
                    y += 1

        ascii_codes.sort(key=(lambda i: i[0]))
        for index, item in enumerate(ascii_codes):
            new_item = item[1:]
            new_item.sort(key=lambda i: i[0])
            ascii_codes[index] = [item[0]] + new_item

        split_lines = display().split('\n')
        for line_codes in ascii_codes:
            y = line_codes[0]
            line_codes = line_codes[1:]
            skip_num = 0
            for index, code in enumerate(line_codes):
                if skip_num > 0:
                    skip_num -= 1
                    continue
                x1, style1 = code
                display.cursor_position = (x1, y)
                display.line_insert(split_lines, style1)
                for code in line_codes[index+1:]:
                    style2 = code[1]
                    if style1 == style2:
                        skip_num += 1
                    else: break
                display.cursor_position = (x1+len(style1)+skip_num+1, y)
                display.line_insert(split_lines, '\x1b[0m')
                for code in line_codes[index+1+skip_num:]:
                    code[0] = code[0] + len(style1) + len('\x1b[0m')
        display.string = '\n'.join(split_lines)
        

    @classmethod
    def print_out(cls, display):
        for line in display.split('\n'):
            stdout.write(line+'\n')        
        CursorHandler.reset_cursor_position()
        del display

    @classmethod
    def set_active_scene(cls, scene):
        if cls.active_scene != None:
            cls.active_scene.active = False
        scene.active = True
        cls.active_scene = scene
        CursorHandler.clear()

class Movement2D:

    @staticmethod
    def move(distance, abs_position, grid_position):
        abs_position = Vectors2D.sum(distance, abs_position)
        grid_position = round(abs_position[0]), round(abs_position[1])
        return abs_position, grid_position

class Vectors2D:

    @staticmethod
    def sum(*args):
        new_vector = (0, 0)
        for vector in args:
            new_vector = (new_vector[0] + vector[0], new_vector[1] + vector[1])
        return new_vector

    @staticmethod
    def scalar(vector, scalar):
        return (vector[0]*scalar, vector[1]*scalar)

class AsciiImage:

    def __init__(self, string, cursor_position=(1,1)):
        self.string = string
        self.cursor_position = cursor_position

    def __call__(self):
        return self.string

    def overwrite(self, text, remove_leftside_spaces=True, wrap_around=False):
        y = self.cursor_position[1]
        for line in text.split('\n'):
            x = self.cursor_position[0]
            if remove_leftside_spaces:    
                line_start = self.count_spaces(line)
                line = line[line_start:]
                x += line_start
            if not wrap_around and y <= 0:
                y += 1
                continue
            string_lines = self.string.split('\n') 
            try: target_line = string_lines[y-1]
            except IndexError:
                for _ in range(y-len(string_lines)):
                    string_lines.append('')
                target_line = string_lines[y-1]
            line_length = len(target_line)
            if line_length < x-1:
                target_line += ' '*(x-1-line_length)
            string_lines[y-1] = target_line[:x-1] + line + target_line[x+len(line)-1:]
            self.string = '\n'.join(string_lines)
            y += 1

    def count_spaces(self, string, rightside=False):
        if rightside: i = -1
        else: i = 1
        count = 0
        for i in string[::i]:
            if i == ' ': count += 1
            else: break
        return count

    def line_insert(self, lines: list, text):
        x, y = self.cursor_position
        line = lines[y]
        lines[y] = line[:x] + text + line[x:]
        
class KeyboardInput:

    key_queue = []
    held_keys = set()

    @classmethod
    def start_listening(cls):
        cls.listener = keyboard.Listener(on_press=cls.on_press, on_release=cls.on_release)
        cls.listener.start()
 
    @classmethod
    def get_key(cls):
        try:
            event = cls.key_queue.pop(0)
        except:
            event = None
        return event
    
    @classmethod
    def stop_listening(cls):
        cls.listener.stop()

    def on_press(key):
        try:
            event = key.char
        except AttributeError:
            event = key

        if len(KeyboardInput.key_queue) < 5:
            KeyboardInput.key_queue.append(event)
        KeyboardInput.held_keys.add(event)

    def on_release(key):
        try:
            event = key.char
        except AttributeError:
            event = key
        KeyboardInput.held_keys.discard(event)

class Sound:

    mixer.init()

    @staticmethod
    def play_from_path(relative_path):
        Sound.get_sound_data(relative_path).play()

    @staticmethod
    def play(sound):
        sound.play()

    @staticmethod
    def get_sound_data(relative_path):
        return mixer.Sound(file=FileManager.get_abs_path(relative_path))

class DialogBox:

    def __init__(self):
        pass

if __name__ == '__main__':
    pass