# Description: contains the MyText class, which is a subclass of tkinter.Text

# general modules
import tkinter as tk
import threading, os, json
import colorsys

# my modules
import tkinter_functionality

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

# prevents the app from freezing during slow functions, like api calls or downloads
def new_thread(function):
    threading.Thread(target=function).start()

class MyText(tk.Text):
    def __init__(self, master, signal_func, **kwargs):
        self.master = master
        super().__init__(master, **kwargs, wrap=tk.WORD)
        fg_col = 'grey'
        bg_col = 'black'
        self.config(**{
            'fg': fg_col,
            'bg': bg_col,
            'insertbackground': 'white',
            'selectbackground': fg_col,
            'selectforeground': bg_col,
            'cursor': 'arrow #ffffff',
            'font': ('Calibri', 13),
            'height': 500,
        })
        self.bind('<Motion>', self.on_motion)
        self.bind('<ButtonPress>', self.on_click)
        self.bind('<ButtonRelease>', self.on_release, add='+')
        self.bind('<KeyPress>', self.on_keypress)

        self.top_left = master.top_left
        self.signal_func = signal_func

        self.previous_state = {
            'text': self.get(1.0, 'end')[0:-1],
            'cursor': self.index(tk.INSERT),
            'scroll': self.yview()[0],
        }

        tkinter_functionality.set_tab_length(self, 4)
    
    def increment_width(self, amount):
        frame = self.master
        cur = frame.winfo_width()
        frame.config(width=cur + amount)
    
    def increment_height(self, amount):
        frame = self.master
        cur = frame.winfo_height()
        frame.config(height=cur + amount)
    
    def replace_flagged(self, flag, replacement):
        idx_start = self.search(f'[{flag}]', 1.0, 'end') + ' linestart'
        idx_end = self.search(f'[/{flag}]', 1.0, 'end') + ' lineend'

        self.delete(idx_start, idx_end)
        self.insert(
            idx_start,
            '\n'.join([
                f'[{flag}]',
                replacement,
                f'[/{flag}]'
            ])
        )
    
    def on_click(self, event):
        self.master.tkraise()
        self.signal_func(self.master, 'clicked')

        if event.state == 12:  # ctrl click
            idx = self.index(f'@{event.x},{event.y}')
            line = self.get(idx + ' linestart', idx + ' lineend')

            self.run_script_lines(line)

            '''prompt = get_paragraph(event)
            prompt_words = prompt.split(' ')
            if len(prompt_words) == 3:
                print('3 words, entered this branch')
                if os.path.exists(prompt_words[0]):
                    start, end = prompt_words[1:]
                    sample_path = use_api(
                        'crop_audio',
                        {
                            'in_path': prompt_words[0],
                            'starttime': start,
                            'endtime': end,
                        }
                    )['return']
                    play_audio(sample_path)
            else:
                def to_call():
                    speak(self.get(1.0, 'end')[:-1], alts={'prompt': prompt})
                new_thread(to_call)'''
    
    def on_release(self, event):
        sel = tkinter_functionality.get_selected(self)
        if sel != None:
            full_text = self.get(1.0, 'end')[0:-1]
            selcode = tkinter_functionality.get_flagged(full_text, 'on sel')
            if selcode != None:
                self.run_script_lines(selcode)
    
    def print_editor_content(self, path, title):
        print(f'trying to get path={path}, title={title}')
        if not os.path.exists(path):
            print('path does not exist')
            return
        else:
            with open(path, 'r', encoding="utf-8") as f:
                contents = json.load(f)
                f.close()

            for item in contents:
                if item['frame']['title'] == title:
                    print(col('cy', '='*20))
                    print(item['editor']['text'])
                    print(col('cy', '='*20))
                    print('found it.')
                    return
            print('did not find anything.')

    def run_script_lines(self, script):
        macros = self.get_macros()
        editors = self.master.master.get_editors()

        # subfunctions for each kind of command

        # will write text to an arbitrary frame's section
        def write_to(line):
            passed = line.partition('(')[2].partition(')')[0]
            args = passed.split(' --> ')
            if len(args) == 2:
                source, dest = args
                if source == '{sel}':
                    source = tkinter_functionality.get_selected(self)
                self.master.master.write_to(source, dest)
        
        # will "run" an arbitrary frame's section with MyText.run_flag
        def run(line):
            cmd = line.partition('run(')[2].partition(')')[0]
            if len(cmd[1:-1].split('.')) != 2:
                print(f'invalid run command in run_script_lines:"{cmd}"')
                return
            else:
                title, flag = cmd[1:-1].split('.')
                for editor in self.master.master.get_editors():
                    if editor.master['text'] == title:
                        flagged = tkinter_functionality.get_flagged(editor.get(1.0, 'end')[0:-1], flag)
                        if flag in ['prompt',]:
                            editor.run_flag(flag, flagged, multithread=False)
                        else:
                            editor.run_flag(flag, flagged)
                        return
        
        def maximize(line):
            to_maximize = line.partition('maximize(')[2].partition(')')[0]
            for editor in editors:
                if editor.master['text'] == to_maximize:
                    editor.master.maximize()
                    return

        def minimize(line):
            to_minimize = line.partition('minimize(')[2].partition(')')[0]
            for editor in editors:
                if editor.master['text'] == to_minimize:
                    editor.master.minimize()
                    return
        
        def relocate(line):
            middle = line.partition('relocate(')[2].partition(')')[0]
            to_relocate, loc = middle.split(' --> ')
            x, y = loc.split(',')
            for editor in editors:
                if editor.master['text'] == to_relocate:
                    editor.master.relocate(int(x), int(y))
                    return

        def resize(line):
            middle = line.partition('resize(')[2].partition(')')[0]
            to_resize, size = middle.split(' --> ')
            w, h = size.split(',')
            for editor in editors:
                if editor.master['text'] == to_resize:  # note: "text" is the title, since it's a tkinter.LabelFrame
                    editor.master.config(width=int(w), height=int(h))

        def external_editor(line):
            code = line.partition('external(')[2].partition(')')[0]
            parts = code.split(' --> ')
            if len(parts) != 2:
                return
            else:
                path, title = parts
                self.print_editor_content(path, title)

        def to_call():
            macros = self.get_macros()
            for line in script.split('\n'):
                if line in macros:
                    line = macros[line]

                if line.startswith('write_to('):
                    write_to(line)
                elif line.startswith('run('):
                    run(line)
                elif line.startswith('maximize('):
                    maximize(line)
                elif line.startswith('minimize('):
                    minimize(line)
                elif line.startswith('relocate('):
                    relocate(line)
                elif line.startswith('resize('):
                    resize(line)
                elif line.startswith('external('):
                    external_editor(line)
                else:
                    if line.startswith('dl ') or line.startswith('t ') or line.startswith('s '):
                        tkinter_functionality.process_cmd(line)

        new_thread(to_call)

    def on_motion(self, event):
        pass

    def move(self, x, y):
        new_loc = (
            self.top_left[0] + x,
            self.top_left[1] + y
        )
        self.master.top_left = new_loc
        self.master.place(x=new_loc[0], y=new_loc[1])

    def on_keypress(self, event):
        if event.keysym == 'Escape':
            self.master.master.remove_frame(self.master)  # lol
        elif event.state == 12 and event.keysym == 'r' or event.keysym == 'F5':
            # get flag
            frame = self.master
            editor = self
            idx = editor.index(tk.INSERT)
            flag, flagged = tkinter_functionality.detect_flag(editor, idx)
            if flag != None:
                self.run_flag(flag, flagged)
        elif event.state == 12 and event.keysym == 'b':
            highlight_wordstarts(self)
        elif event.state == 12 and event.keysym == 'z':
            self.restore_state()
        elif event.state == 12 and event.keysym == 'f':
            idx = self.index(tk.INSERT)
            line = self.get(idx + ' linestart', idx + ' lineend')

            self.run_script_lines(line)
        elif event.state == 12 and event.keysym == 'p':
            self.master.popout()
        elif event.state == 393224:
            incr = 10
            if event.keysym == 'Left':
                self.increment_width(-incr)
            elif event.keysym == 'Right':
                self.increment_width(incr)
            elif event.keysym == 'Up':
                self.increment_height(-incr)
            elif event.keysym == 'Down':
                self.increment_height(incr)
    
    def after_prompt(self):
        flagged = tkinter_functionality.get_flagged(self.get(1.0, 'end')[0:-1], 'after prompt')
        if flagged != None:
            print(f'will run flagged code: {flagged}')
            self.run_script_lines(flagged)

    def run_flag(self, flag, flagged, multithread=True):
        print('~'*20)
        print('run_flag called')
        print(f'flag: {flag}')
        print(f'flagged: {flagged}')
        print(f'multithread: {multithread}')
        print('~'*20)
        full_text = self.get(1.0, 'end')[0:-1]

        # first define helper functions, then pass `flagged` to the appropriate one

        # will do a language model completion
        def prompt_flag(flagged, multithread=True):
            # full_text is an argument in run_flag

            self.store_state()
            engine = tkinter_functionality.get_flagged(full_text, 'engine')
            prompt = flagged
            def printfunc(text):
                idx = self.search('\n[/prompt]', 1.0, 'end') + ' lineend'
                self.insert(idx, text)
                self.see(f'{idx} +4l')
            # use seperate thread for api call, to prevent the app from freezing

            def replace_two_blocks(macrostext, extratext):
                self.replace_flagged('macros', macrostext)
                self.replace_flagged('extra', extratext)

            def to_call():
                tkinter_functionality.language_model(
                    prompt,
                    as_stream=True,
                    print_func=printfunc,
                    model=engine,
                    editors=self.master.master.get_editors(),
                    after_prompt=replace_two_blocks,
                )

            if multithread:
                new_thread(to_call)
            else:
                to_call()
        
        # will resize the frame that this text editor is embedded in
        def resize_flag(flagged):
            print(f'running resize with flagged = "{flagged}"')
            keys = [
                'width',
                'height'
            ]
            d = {k:None for k in keys}
            for line in flagged.split('\n'):
                k,v = line.split(' = ')
                if k in keys:
                    d[k] = int(v)
            frame = self.master
            #assert isinstance(frame, (tk.LabelFrame, tk.Frame))
            if d['width'] != None:
                print(f'changing width to {d["width"]}')
                frame.config(width=d['width'])
            if d['height'] != None:
                print(f'changing height to {d["height"]}')
                frame.config(height=d['height'])
        
        # change the font of this editor
        def font_flag(flagged):
            keys = [
                'size',
                'family',
                'fg',
                'bg',
            ]
            d = {k:None for k in keys}
            for line in flagged.split('\n'):
                leftright = line.split(' = ')
                if len(leftright) != 2:
                    continue
                k,v = leftright
                if k in keys:
                    d[k] = v
            if d['family'] == None:
                d['family'] = self['font'].split(' ')[0]
            if d['size'] == None:
                d['size'] = self['font'].split(' ')[1]
            self.config(font=(d['family'], d['size']))
            if d['fg'] != None:
                d['fg'] = tkinter_functionality.changecol(self, d['fg'])
                self.config(fg=d['fg'])
                self.config(selectbackground=d['fg'])
            if d['bg'] != None:
                d['bg'] = tkinter_functionality.changecol(self, d['bg'])
                self.config(bg=d['bg'])
                self.config(selectforeground=d['bg'])

        def title_flag(flagged):
            self.master.config(text=flagged)

        def analysis_flag(flagged):
            lines = flagged.split('\n')
            if len(lines) != 2:
                print(col('re', 'analysis code must have exactly 2 lines'))
                return
            else:
                source = lines[0]
                destination = lines[1]
                for s in (source, destination):
                    if not s.startswith('{') and not s.endswith('}'):
                        print(col('re', 'analysis code lines must be in curly braces'))
                        return

                source = source[1:-1]
                destination = destination[1:-1]
                editors = self.master.master.get_editors()
                # get source
                if source == 'sel':
                    to_analyze = tkinter_functionality.get_selected(self)
                else:
                    title, flag = source.split('.')
                    for editor in editors:
                        if editor.master['text'] == title:
                            to_analyze = tkinter_functionality.get_flagged(editor.get('1.0', 'end -1c'), flag)
                            break
                # get analysis
                analysis = {
                    'word count': len(to_analyze.split(' ')),
                }
                analysis = str(analysis)
                # get destination
                title, flag = destination.split('.')
                for editor in editors:
                    if editor.master['text'] == title:
                        editor.replace_flagged(flag, analysis)

        # run the appropriate function
        if flag == 'prompt':
            prompt_flag(flagged, multithread)
        elif flag == 'resize':
            resize_flag(flagged)
        elif flag == 'font':
            font_flag(flagged)
        elif flag == 'title':
            title_flag(flagged)
        elif flag == 'analysis':
            analysis_flag(flagged)
        elif flag == 'script':
            self.run_script_lines(flagged)

    def store_state(self):
        text = self.get(1.0, 'end')[0:-1]
        idx = self.index(tk.INSERT)
        scroll = self.yview()[0]
        self.previous_state = {
            'text': text,
            'cursor': idx,
            'scroll': scroll,
        }

    def restore_state(self):
        self.delete(1.0, 'end')
        self.insert(1.0, self.previous_state['text'])
        self.mark_set(tk.INSERT, self.previous_state['cursor'])
        self.yview_moveto(self.previous_state['scroll'])

    def get_macros(self):
        macros_string = tkinter_functionality.get_flagged(self.get(1.0, 'end')[:-1], 'macros')
        if macros_string == None:
            return {}
        else:
            macros = {}
            for line in macros_string.split('\n'):
                if line == '':
                    continue
                parts = line.split(' --> ')
                if len(parts) != 2:
                    continue
                key, value = parts
                macros[key] = value
            return macros

def int_to_hexadecimal(number):
    """Takes an integer between 0 and 255, returns the hexadecimal representation."""

    if number < 0 or number > 255:
        raise ValueError('must be between 0 and 255')

    digits = list("0123456789ABCDEF")
    first = number // 16
    second = number%16
    return ''.join(map(str,(digits[first],digits[second])))

def hsv_to_hexcode(hsv, scale=1):
    """Takes a list of 3 numbers, returns hexcode.

    Divides each number by scale, multiplies by 255, rounds it, converts to 2-digit hex number

    Scale divides each number to make it a fraction.
        (So with scale=500, you can pass numbers between 0 and 500, instead of between 0 and 1.)
    """
    numbers = list(map(lambda n:n/scale, (hsv)))
    rgb = colorsys.hsv_to_rgb(*numbers)
    hexcode = '#' + ''.join(map(lambda n:int_to_hexadecimal(int(n*255)), rgb))
    return hexcode

def highlight_wordstarts(widget):
    # start of word highlighting, inspired by https://twitter.com/InternetH0F/status/1656853851348008961

    # helper functions
    def convert_range(pair):
        """take normal range, return tkinter range"""
        assert len(pair) == 2
        assert len(pair[0]) == 2
        assert len(pair[1]) == 2
        def conv(tup):
            line, char = tup
            string = f'{line+1}.{char}'
            return string

        str1, str2 = map(conv, pair)
        tkinter_range = (str1, str2)

        return tkinter_range
    def get_hsv(color):
        rgb = tuple((c/65535 for c in widget.winfo_rgb(color)))
        hsv = colorsys.rgb_to_hsv(*rgb)
        return hsv
    def change_color(color, changers):
        # changers should be 3 callables, each taking a number between 0 and 1, and returning a number between 0 and 1
        # will be applied to hue/saturation/value, in that order.
        # (to make darker, reduce value)
        hsv = get_hsv(color)
        new_hsv = tuple(map(lambda n:changers[n](hsv[n]), range(3)))
        new_color = hsv_to_hexcode(new_hsv, scale=1)
        return new_color

    def get_changers():
        def third_fg_changer(n):
            # make darker
            n = max(0.1, n*0.7)
            return n
        fg_changers = [
            lambda n:n,
            lambda n:n,
            third_fg_changer,
        ]
        bg_changers = [
            lambda n:n,
            lambda n:n,
            lambda n:n,
        ]
        return fg_changers, bg_changers

    to_analyze = widget.get(1.0, 'end')[:-1]

    # get indices of words
    word_indices = []
    lines = to_analyze.split('\n')
    for line_n, line in enumerate(lines):
        idx = 0
        words = line.split(' ')
        for word in words:
            indices = ( (line_n,idx), (line_n,idx+len(word)) )
            word_indices.append(indices)
            idx += len(word) + 1  # +1 is for the space

    for pair in word_indices:
        ranges = convert_range(pair)
        widget.tag_add('wordstart', ranges[0], ranges[0]+' +2c')

    # keep bg the same, make fg darker.
    fg_changers, bg_changers = get_changers()
    new_fg = change_color(
        widget.cget('fg'),
        fg_changers
    )
    new_bg = change_color(
        widget.cget('bg'),
        bg_changers
    )
    settings = {
        'foreground': new_fg,
        'background': new_bg,
        'selectbackground': new_fg,
        'selectforeground': new_bg,
    }
    widget.tag_config('wordstart', **settings)