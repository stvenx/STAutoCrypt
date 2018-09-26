import sublime, sublime_plugin
import os
pwd = ''
class StAutoCryptCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print(111)
        # self.view.insert(edit, 0, "Hello, World!")
        file_name = self.view.file_name();
        print(file_name)
        ext = os.path.splitext(file_name)[1]
        print(ext)
        # print (sublime.expand_variables())

class ReplaceInputCommand(sublime_plugin.TextCommand):
    def run(self, edit, start = 0, end = 0, password = ''):
        self.view.replace(edit, sublime.Region(start, end), password)

class StAutoCrypt(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.input = ''
        super().__init__(view)
        self.input_view = None
        self.length = 0

    def maskpass(self, password):
        if len(password) == self.length:
            return
        if len(password) < self.length:
            self.input = self.input[0:len(password)]
            self.length = len(password)
            return
        if not self.input_view:
            return
        new_length = len(password) - len(self.input)
        self.input += password[len(self.input):]
        self.length = len(password)
        pos = len(password) - new_length
        self.input_view.run_command('replace_input', {'start': pos,
         'end': pos + new_length,
         'password': '*' * new_length})
        # self.view.replace(edit, sublime.Region(start, end), password)

    def get_ext(self):
        file_name = self.view.file_name();
        print(file_name)
        ext = os.path.splitext(file_name)[1]
        return ext

    def on_load(self):
        ext = self.get_ext();
        if ext == '.stxt':
            print(222)
            self.view.set_read_only(True)
            self.view.window().open_file(self.view.file_name())
            sublime.set_timeout(self.show_input, 100)
        else:
            print('noting to do')

    def show_input(self):
        window = self.view.window();
        self.input_view = sublime.active_window().show_input_panel('password:', '', self.on_done, self.maskpass, None)
        window.focus_view(self.input_view)

    def on_done(self, string):
        print(333)
        print(string)
        print(self.input)
        self.view.set_read_only(False)


    def on_pre_save(self):
        self.content = self.view.substr(sublime.Region(0, self.view.size()))
        # print(content)
        pass
    def on_post_save(self, edit):

        self.view.run_command('replace_input', {'start': 0,
         'end': pos + new_length,
         'password': self.})
        pass

