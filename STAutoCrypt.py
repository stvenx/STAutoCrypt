# -*- coding: utf-8 -*-

import sublime, sublime_plugin
import base64
import os,sys
import hashlib
import base64
sys.path.insert(0, os.path.dirname(__file__))
# from Crypto.Cipher import AES
import pyaes

pwd = ''
class StAutoCryptCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name();
        ext = os.path.splitext(file_name)[1]

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
        ext = os.path.splitext(file_name)[1]
        return ext

    def on_load(self):
        ext = self.get_ext();
        if ext == '.stxt':
            # self.view.set_read_only(True)
            # self.view.window().open_file(self.view.file_name())
            sublime.set_timeout(self.show_input, 100)


    def show_input(self):
        window = self.view.window();
        self.input_view = sublime.active_window().show_input_panel('password:', '', self.on_done, self.maskpass, None)
        window.focus_view(self.input_view)

    def on_done(self, string):
        encrypted_content = self.view.substr(sublime.Region(0, self.view.size()))
        plaintext = self.decrypt(encrypted_content)
        self.view.run_command('replace_input', {'start': 0,'end': self.view.size(), 'text': plaintext})
        self.view.set_read_only(False)

    def on_modified(self):
        self.view.set_scratch(False)

    # 保存前加密
    def on_pre_save(self):
        self.content = self.view.substr(sublime.Region(0, self.view.size()))
        if self.get_ext() == '.stxt':
            encrypted_content = self.encrypt(self.content)
            self.view.run_command('replace_input', {'start': 0, 'end': self.view.size(), 'text': encrypted_content})

    def encrypt(self, plaintext):
        m = hashlib.md5()
        m.update(self.password.encode('utf-8'))
        key = m.digest();
        aes = pyaes.AESModeOfOperationCTR(key)
        ciphertext = aes.encrypt(plaintext)
        encrypted_content = base64.b64encode(ciphertext)
        return encrypted_content.decode('utf-8')


    def decrypt(self, ciphertext):
        ciphertext_string = ciphertext.encode('utf-8');
        ciphertext_string = base64.b64decode(ciphertext_string)
        m = hashlib.md5()
        m.update(self.password.encode('utf-8'))
        key = m.digest();
        aes = pyaes.AESModeOfOperationCTR(key)
        plaintext = aes.decrypt(ciphertext_string)
        return bytes.decode(plaintext)

    def on_post_save(self):
        if self.get_ext() == '.stxt':
            self.view.run_command('replace_input', {'start': 0,'end': self.view.size(), 'text': self.content})
            self.view.set_scratch(True)
