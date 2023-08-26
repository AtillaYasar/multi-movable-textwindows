        def evalin_flag(flagged):
            program = flagged
            namespace = {}
            exec(program, namespace)
            result = namespace['result']

            title = self.master['text']
            self.replace_flagged('evalout', str(result))
