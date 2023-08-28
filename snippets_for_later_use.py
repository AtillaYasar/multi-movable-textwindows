"""
for stuff ive written/implemented locally but not yet implemented in this repo
"""

        def evalin_flag(flagged):
            program = flagged
            namespace = {}
            exec(program, namespace)
            result = namespace['result']

            title = self.master['text']
            self.replace_flagged('evalout', str(result))

        # in MyText.on_keypress in tkinter_text.py
        elif keysym.startswith('F'):  # do something on f keys
            flag = f'on {keysym.lower()}'
            flagged = tkinter_functionality.get_flagged(self.get(1.0, 'end')[0:-1], flag)
            if flagged != None:
                self.run_script_lines(flagged)
