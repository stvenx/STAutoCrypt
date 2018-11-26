import sublime, sublime_plugin
import base64
import os,sys
import hashlib
sys.path.insert(0, os.path.dirname(__file__))
# from Crypto.Cipher import AES
print(sys.path)
import pyaes

pwd = ''
class StAutoCryptCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print(111)
        file_name = self.view.file_name();
        print(file_name)
        ext = os.path.splitext(file_name)[1]
        print(ext)

class ReplaceInputCommand(sublime_plugin.TextCommand):
    def run(self, edit, start = 0, end = 0, text = ''):
        self.view.replace(edit, sublime.Region(start, end), text)

class StAutoCrypt(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.password = ''
        super().__init__(view)
        self.input_view = None
        self.length = 0

    def maskpass(self, password):
        if len(password) == self.length:
            return
        if len(password) < self.length:
            self.password = self.password[0:len(password)]
            self.length = len(password)
            return
        if not self.input_view:
            return
        new_length = len(password) - len(self.password)
        self.password += password[len(self.password):]
        self.length = len(password)
        pos = len(password) - new_length
        self.input_view.run_command('replace_input', {'start': pos, 'end': pos + new_length, 'text': '*' * new_length})

    def get_ext(self):
        file_name = self.view.file_name();
        print(file_name)
        ext = os.path.splitext(file_name)[1]
        return ext

    def on_load(self):
        ext = self.get_ext();
        if ext == '.stxt':
            print(222)
            # self.view.set_read_only(True)
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
        print('password: ' + self.password)
        self.view.set_read_only(False)

    def on_modified(self):
        self.view.set_scratch(False)

    # 保存前加密
    def on_pre_save(self):
        self.content = self.view.substr(sublime.Region(0, self.view.size()))
        if self.get_ext() == '.stxt':
            print('on_pre_save password: ' + self.password)
            encrypted_content = '';
            self.view.run_command('replace_input', {'start': 0, 'end': self.view.size(), 'text': '122221'})
        print(self.content)

    def on_post_save(self):
        if self.get_ext() == '.stxt':
            self.view.run_command('replace_input', {'start': 0,'end': self.view.size(), 'text': self.content})
            self.view.set_scratch(True)

