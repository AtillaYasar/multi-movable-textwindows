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

        # check data
        if cmd in data:
            if all([key in data[cmd] for key in ['last opened', 'timeout']]):
                correct = True
            else:
                correct = False
        else:
            correct = False
        if not correct:
            data[cmd] = {
                'last opened': 0,
                'timeout': default_timeout,
            }

        # check if goes through
        elapsed = time.time() - data[cmd]['last opened']
        if elapsed > data[cmd]['timeout']:
            search_engines.open_chrome_tab(words[1])
            data[cmd]['last opened'] = time.time()
        else:
            print(f'not opening tab, elapsed={elapsed}, timeout={data[cmd]["timeout"]}')
        
        # update data
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
