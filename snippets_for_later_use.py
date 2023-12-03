"""
for stuff ive written/implemented locally but not yet implemented in this repo
"""
        # tkinter_text.py, def run_flag
        def evalin_flag(flagged):
            program = flagged
            namespace = {}
            exec(program, namespace)
            if 'result' in namespace:
                result = namespace['result']

                title = self.master['text']
                self.replace_flagged('evalout', str(result))
            if 'scriptlines' in namespace:
                scriptlines = namespace['scriptlines']
                self.run_script_lines(scriptlines)

        # in MyText.on_keypress in tkinter_text.py
        elif keysym.startswith('F'):  # do something on f keys
            flag = f'on {keysym.lower()}'
            flagged = tkinter_functionality.get_flagged(self.get(1.0, 'end')[0:-1], flag)
            if flagged != None:
                self.run_script_lines(flagged)


# in tkinter_functionality.py, def process_cmd
    elif words[0] == 't':
        # will open a chrome a tab (after checking if enough time has passed since the last time it was opened)

        defaul_timeout = 60

        # get_data
        path = 't_command.json'
        if path in os.listdir():
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            data = {}

# autoinsert example, in tkinter.Text, when you hit Enter, based on the current/next/previous line and the full text of the editor
    def on_keyrelease(self, event):
        key = event.keysym
        if key == 'Return':
            # detect line, nextline and fulltext.
            idx = self.index('insert')
            line = self.get(f'{idx} linestart', f'{idx} lineend')
            prevline = self.get(f'{idx} -1l linestart', f'{idx} -1l lineend')
            nextline = self.get(f'{idx} +1l linestart', f'{idx} +1l lineend')
            fulltext = self.get('1.0', 'end')

            # some conditions before it does autoinsertion
            if all([
                prevline.startswith('['),
                prevline.endswith(']'),
                not prevline.startswith('[/'),
                not nextline.startswith('['),
            ]):
                flag = prevline[1:-1]
                closer = f'[/{flag}]'
                if closer in fulltext:
                    return

                # now decide what to insert based on the flag
                if flag == 'font':
                    to_insert = '\n'.join([
                        'size = 16',
                        'fg = grey',
                        'family = calibri',
                        closer
                    ])
                elif flag == 'engine':
                    to_insert = '\n'.join([
                        'gpt-3-oai',
                        closer,
                        'kayra',
                        'gpt-4v',
                    ])
                elif flag == 'on sel':
                    to_insert = '\n'.join([
                        'write_to({sel} --> {0.seldump})',
                        'run({0.emb})',
                        closer,
                    ])
                elif flag == 'emb':
                    to_insert = '\n'.join([
                        '!query={0.seldump}',
                        '!output={1.yo}',
                        closer,
                    ])
                elif flag == 'feed emb':
                    to_insert = '\n'.join([
                        '!tags=',
                        closer
                    ])
                else:
                    to_insert = closer
                self.insert('insert', to_insert)
            elif prevline.startswith('$') and prevline.endswith('$'):
                # not implemented or figured out yet
                to_insert = ''
                self.insert('insert', to_insert)
