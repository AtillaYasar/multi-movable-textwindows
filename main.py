# general modules
import tkinter as tk
import requests, json, os, time, threading, re, sys

# my modules
import tkinter_text
import tkinter_functionality

# for play_ytvid
import cv2
import subprocess

def get_selected(text_widget):
    # returns mouse-selected text from a tk.Text widget
    try:
        text_widget.selection_get()
    except:
        return None
    else:
        return text_widget.selection_get()

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def text_create(path, content=''):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def text_read(fileName):
    with open(fileName, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

def open_json(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        contents = json.load(f)
        f.close()
    return contents

def get_flagged(string, flag):
    if f'[{flag}]' in string and f'[/{flag}]' in string:
        flagged = string.partition(f'[{flag}]')[2].partition(f'[/{flag}]')[0][1:-1]
        return flagged
    else:
        return None

def set_terminal_title(title):
    print(f"\033]0;{title}\a", end="", flush=True)

def get_own_filename():
    file_path = os.path.abspath(__file__)
    file_name = os.path.basename(file_path)
    
    return file_name


# executes a given function on a new thread, so that the app doesn't freeze while it is running
def new_thread(function):
    threading.Thread(target=function).start()

def change_fontsize(widget, increment):
    font = widget['font']
    font = font.split(' ')
    size = int(font[1])
    size += increment
    font[1] = str(size)
    font = ' '.join(font)
    widget.config(font=font)

class MovableSquare(tk.LabelFrame):
    def __init__(self, master, signal_func, top_left, bottom_right, **kwargs):
        assert callable(signal_func)
        print(f'creating movable square, topleft={top_left}, bottomright={bottom_right}')
        self.minimized = False
        self.master = master
        self.top_left = top_left
        self.bottom_right = bottom_right

        self.signal_func = signal_func

        # calculate
        x1, y1 = top_left
        x2, y2 = bottom_right
        width = x2 - x1
        height = y2 - y1

        # create frame
        super().__init__(master, width=width, height=height, bg='grey', **kwargs)
        self.place(x=x1, y=y1)
        self.pack_propagate(0)

        self.editor = tkinter_text.MyText(self, signal_func, width=width, height=height)
        self.editor.pack()

        self.bind('<Motion>', self.on_motion)
        self.bind('<ButtonPress>', self.on_click)
        self.bind('<Double-ButtonPress>', self.on_double_click)
    
    def on_click(self, event):
        self.signal_func(self, 'clicked')
    
    def on_double_click(self, event):
        if self.minimized:
            self.maximize()
        else:
            self.minimize()
    
    def on_motion(self, event):
        pass

    def move(self, x, y):
        new_loc = (
            self.top_left[0] + x,
            self.top_left[1] + y
        )
        self.top_left = new_loc
        self.place(x=new_loc[0], y=new_loc[1])
    
    def relocate(self, x, y):
        new_loc = (x, y)
        self.top_left = new_loc
        self.place(x=new_loc[0], y=new_loc[1])

    def minimize(self):
        self.normal_height = self.winfo_height()
        self.minimized_height = 20
        self.configure(height=self.minimized_height)
        self.minimized = True

    def maximize(self):
        min_height = 200
        try:
            self.normal_height
        except:
            self.normal_height = self.winfo_height()

        if self.normal_height < min_height:
            self.normal_height = min_height
        self.configure(height=self.normal_height)
        self.minimized = False

    def popout(self, contents=None):
        toplevel = tk.Toplevel()
        top_left = self.top_left
        width = self.winfo_width()
        height = self.winfo_height()
        toplevel.geometry(f'{width}x{height}+{top_left[0]}+{top_left[1]}')
        toplevel.pack_propagate(0)
        toplevel.config(bg='black')
        toplevel.title(f"{self['text']}_popout")

        editor = tk.Text(toplevel, wrap='word')
        tkinter_functionality.set_tab_length(editor, 4)
        editor.pack()
        editor.config(**{
            'font': self.editor['font'],
            'bg': self.editor['bg'],
            'fg': self.editor['fg'],
            'insertbackground': self.editor['insertbackground'],
            'selectbackground': self.editor['selectbackground'],
            'selectforeground': self.editor['selectforeground'],
            'height': 100,
        })
        if contents == None:
            editor.insert('1.0', self.editor.get('1.0', 'end'))
        else:
            editor.insert('1.0', contents)

        def on_keypress(event):
            if event.state == 12 and event.keysym == 'b':
                tkinter_functionality.highlight_firstparts(event.widget)
            elif event.state == 12 and event.keysym == 'r' or event.keysym == 'F5':
                editor = event.widget
                idx = editor.index(tk.INSERT)
                flag, flagged = tkinter_functionality.detect_flag(editor, idx)

                if flag == 'prompt':
                    def to_call():
                        prompt = flagged
                        engine = tkinter_functionality.get_flagged(
                            editor.get(1.0, 'end')[0:-1],
                            'engine'
                        )
                        
                        def print_func(text):
                            idx = editor.search('\n[/prompt]', 1.0, 'end') + ' lineend'
                            editor.insert(idx, text)
                            editor.see(f'{idx} +4l')
                        tkinter_functionality.language_model(
                            prompt,
                            as_stream=True,
                            print_func=print_func,
                            model=engine,
                            editors=self.master.get_editors()
                        )

                    new_thread(to_call)
                elif flag == 'resize':
                    keys = [
                        'width',
                        'height'
                    ]
                    d = {k:None for k in keys}
                    for line in flagged.split('\n'):
                        k,v = line.split(' = ')
                        if k in keys:
                            d[k] = int(v)
                    if d['width'] == None:
                        width = toplevel.winfo_width()
                    else:
                        width = d['width']
                    if d['height'] == None:
                        height = toplevel.winfo_height()
                    else:
                        height = d['height']
                    toplevel.geometry(f'{width}x{height}')
                elif flag == 'font':
                    keys = [
                        'size',
                        'family',
                        'fg',
                        'bg',
                    ]
                    d = {k:None for k in keys}
                    for line in flagged.split('\n'):
                        k,v = line.split(' = ')
                        if k in keys:
                            d[k] = v
                    editor.config(font=(d['family'], d['size']))
                    if d['fg'] != None:
                        editor.config(fg=d['fg'])
                        editor.config(selectbackground=d['fg'])
                    if d['bg'] != None:
                        editor.config(bg=d['bg'])
                        editor.config(selectforeground=d['bg'])

        
        editor.bind('<KeyPress>', on_keypress)


class MyFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.reset_movement()

        # motion binds
        master.bind('<ButtonPress>', self._on_click)
        master.bind('<Motion>', self._on_motion)
        master.bind('<ButtonRelease>', self._on_release)
        # key binds
        master.bind('<KeyPress>', self.on_keypress)

        self.data_path = 'frame_data.json'
        if os.path.exists(self.data_path):
            self.frames = []
            self.load()
        else:
            self.frames = []
            with open(self.data_path, 'w') as f:
                json.dump(self.frames, f)
    
    def save(self):
        # helper function
        def frame_to_dict(frame):
            editor_widget = frame.editor
            assert isinstance(frame, MovableSquare)
            assert isinstance(editor_widget, tkinter_text.MyText)

            ## collect info about frame
            loc = frame.top_left
            width = frame.winfo_width()
            height = frame.winfo_height()
            title = frame['text']

            ## collect info about editor
            text = editor_widget.get(1.0, 'end')[:-1]
            bg = editor_widget['bg']
            fg = editor_widget['fg']
            font = editor_widget['font']
            scroll = editor_widget.yview()[0]            
            idx = editor_widget.index('insert') # index of cursor

            ## make json-compatible
            d = {
                'frame':{
                    'title': title,
                    'loc': loc,
                    'width': width,
                    'height': height,
                },
                'editor':{
                    'text': text,
                    'bg': bg,
                    'fg': fg,
                    'font': font,
                    'scroll': scroll,
                    'idx': idx,
                }
            }
            return d

        data = []
        for frame in self.frames:
            d = frame_to_dict(frame)
            if d in data:
                print(col('re', 'warning: duplicate frames detected'))
                exit()
            data.append(d)

        # store
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(col('gr', f'saved to {self.data_path}'))
        backup_path = f'backups/all_frames{time.time()}.json'
        with open(backup_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(col('gr', backup_path))
    
    def load(self):
        # clear out old frames
        if self.frames != []:
            print(col('re', 'warning: old frames not cleared, doing it now'))
            for frame in self.frames:
                self.remove_frame(frame)
        assert self.frames == []

        # load data
        with open(self.data_path, 'r') as f:
            d = json.load(f)
        for item in d:
            assert d.count(item) == 1, 'duplicate frames detected'
        d = [item for item in d if item['frame']['height'] > 15 and item['frame']['width'] > 15]
        with open(self.data_path, 'w') as f:
            json.dump(d, f, indent=4)

        # apply data
        for item in d:
            frame_info = item['frame']
            editor_info = item['editor']

            # frame
            topleft = frame_info['loc']
            bottomright = (
                frame_info['loc'][0] + frame_info['width'],
                frame_info['loc'][1] + frame_info['height']
            )
            frame = self.create_frame(
                topleft,
                bottomright,
            )
            frame.config(text=frame_info['title'])

            # editor
            editor = frame.editor
            editor.insert('end -1c', editor_info['text'])
            editor.config(
                bg=editor_info['bg'],
                fg=editor_info['fg'],
                font=editor_info['font'],
            )
            editor.yview_moveto(editor_info['scroll'])
            editor.mark_set('insert', editor_info['idx'])
    
    def reset_movement(self):
        self.movement_start = (0,0)
        self.movement_delta = (0,0)
        self.control_key = False
        self.alt_key = False
        self.clicked_frame = None
    
    def signal_func(self, obj, info):
        if info == 'clicked':
            self.clicked_frame = obj
            assert isinstance(obj, MovableSquare)

    def create_frame(self, topleft, bottomright):
        width = bottomright[0] - topleft[0]
        height = bottomright[1] - topleft[1]
        if width < 20 or height < 20:
            print(col('re', 'warning: frame too small, not creating'))
            return None
        else:
            frame = MovableSquare(self, self.signal_func, topleft, bottomright, text=f'{len(self.frames)}')
            self.frames.append(frame)

            return frame
    
    def on_keypress(self, event):
        pass
        '''if event.state == 12 and event.keysym == 'z':
            if len(self.frames) > 0:
                frame = self.frames.popitem()[1]
                frame.destroy()'''
        if event.state == 12 and event.keysym == 's':
            self.save()
    
    def on_motion(self, event):
        pass

    """
    The click/drag/release stuff has basically 2 layers:
        - the _{x} functions calculate and store info about where you started, how far you moved, and where you ended, then they call the {x} functions.
        - the {x} functions do stuff with that info.
    """

    # setup
    def _on_click(self, event):
        # store loc
        x, y = event.x, event.y
        self.movement_start = (x, y)
        self.movement_delta = (0, 0)
        # store control key
        if event.state == 12:
            self.control_key = True
        if event.state == 131080:
            self.alt_key = True
        # callback
        self.on_click()

    def _on_motion(self, event):
        # store delta
        if self.movement_start is not None:
            dx = event.x - self.movement_start[0]
            dy = event.y - self.movement_start[1]
            self.movement_delta = (dx, dy)
        # callback
        self.on_motion()

    def _on_release(self, event):
        # store loc
        if self.movement_start is not None:
            x, y = event.x, event.y
            self.movement_end = (x, y)
        # callback
        self.on_release()

    # do stuff
    def on_click(self):
        pass

    def on_motion(self):
        # should be "if dragging" at some point
        if self.clicked_frame is not None and self.alt_key is True:
            frame = self.clicked_frame
            new_loc = (
                frame.top_left[0] + self.movement_delta[0],
                frame.top_left[1] + self.movement_delta[1]
            )
            frame.relocate(*new_loc)

    def on_release(self):
        #print(f'on release. all info: start={self.movement_start}, delta={self.movement_delta}, end={self.movement_end}, ctrl={self.control_key}, alt={self.alt_key}, clicked_frame={self.clicked_frame}')

        if self.control_key:
            frame = self.create_frame(self.movement_start, self.movement_end)
            if frame != None:
                default_path = 'default_text.txt'
                with open(default_path, 'r') as f:
                    default_text = f.read()
                frame.editor.insert('end -1c', default_text)

        # reset movement
        self.reset_movement()
    
    def remove_frame(self, frame):
        assert isinstance(frame, MovableSquare)
        self.frames = [f for f in self.frames if f != frame]
        frame.destroy()

    def get_editors(self):
        return [f.editor for f in self.frames]
    
    def write_to(self, source, destination):
        editors = self.get_editors()

        # handle source
        text = source  # the default is to just use the source as-is
        if source.startswith('{') and source.endswith('}'):
            text = None
            source = source[1:-1]
            if len(source.split('.')) != 2:
                return

            title, flag = source.split('.')
            for editor in editors:
                if editor.master['text'] == title:
                    text = tkinter_functionality.get_flagged(editor.get('1.0', 'end -1c'), flag)
                    break
                else:
                    #print(f'{editor.master["text"]} != {title}')
                    pass
        if text is None:
            print(f'could not find text for {source}')
            return

        # handle destination
        if len(destination[1:-1].split('.')) != 2:
            return
        title, flag = destination[1:-1].split('.')
        # iterate over editors, find the title, replace flagged section with `text`
        for editor in editors:
            if editor.master['text'] == title:
                editor.replace_flagged(flag, text)  # need to implement .replace_flagged
                break

root = tk.Tk()
root.title("Frames")
root.attributes('-fullscreen',True)
root.config(bg='black')

frame1 = MyFrame(root, bg='black', width=1500, height=1500)

frame1.pack()

root.mainloop()

