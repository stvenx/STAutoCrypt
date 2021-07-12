# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import base64
import sys
import os
import hashlib
import zipfile

sys.path.insert(0, os.path.dirname(__file__))
# from Crypto.Cipher import AES

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
CRYPTO_PATH = os.path.join(BASE_PATH, "Transcrypt/Crypto")
IS_64BITS = sys.maxsize > 2 ** 32

# Set the zipfile path according to the platform.
if sys.platform == "darwin":
    # OS X
    ZIP_FILE_NAME = "macos.zip"
elif sys.platform in ("linux", "linux2"):
    # Linux.
    if IS_64BITS:
        ZIP_FILE_NAME = "linux64.zip"
    else:
        ZIP_FILE_NAME = "linux32.zip"
elif sys.platform == "win32":
    # Windows.
    if IS_64BITS:
        ZIP_FILE_NAME = "win64.zip"
    else:
        ZIP_FILE_NAME = "win32.zip"
ZIP_FILE_PATH = os.path.join(CRYPTO_PATH, ZIP_FILE_NAME)


AES = None
C_PAD = b"\0"
KEY_SIZES = [16, 24, 32]


def init():
    """Load AES pre-built binaries."""
    try:
        from Transcrypt.Crypto import AES
    except ImportError:
        if os.path.isfile(ZIP_FILE_PATH):
            with zipfile.ZipFile(ZIP_FILE_PATH, "r") as f:
                f.extractall(CRYPTO_PATH)
        try:
            from Transcrypt.Crypto import AES
        except ImportError:
            raise Exception("Can't load AES")
    globals()['AES'] = AES


class StAutoCryptCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        ext = os.path.splitext(file_name)[1]
        print(ext)


class ReplaceInputCommand(sublime_plugin.TextCommand):

    def run(self, edit, start=0, end=0, text=''):
        self.view.replace(edit, sublime.Region(start, end), text)


class StAutoCrypt(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.st_pwd = ''
        super().__init__(view)
        self.input_view = None
        self.length = 0

    def maskpass(self, st_pwd):
        if len(st_pwd) == self.length:
            return
        if len(st_pwd) < self.length:
            self.st_pwd = self.st_pwd[0:len(st_pwd)]
            self.length = len(st_pwd)
            return
        if not self.input_view:
            return
        new_length = len(st_pwd) - len(self.st_pwd)
        self.st_pwd += st_pwd[len(self.st_pwd):]
        self.length = len(st_pwd)
        pos = len(st_pwd) - new_length
        self.input_view.run_command('replace_input', {'start': pos, 'end': pos + new_length, 'text': '*' * new_length})

    def get_ext(self):
        file_name = self.view.file_name()
        ext = os.path.splitext(file_name)[1]
        return ext

    def on_load(self):
        ext = self.get_ext()
        if ext == '.stxt':
            # self.view.set_read_only(True)
            # self.view.window().open_file(self.view.file_name())
            sublime.set_timeout(self.show_input, 100)

    def show_input(self):
        window = self.view.window()
        self.input_view = sublime.active_window().show_input_panel('password:', '', self.on_done, self.maskpass, None)
        window.focus_view(self.input_view)

    def show_input_password(self):
        window = self.view.window()
        self.input_view = sublime.active_window().show_input_panel('password:', '', None, self.maskpass, None)
        window.focus_view(self.input_view)

    def on_done(self, string):
        encrypted_content = self.view.substr(sublime.Region(0, self.view.size()))
        if len(encrypted_content) == 0:
            return

        try:
            plaintext = self.decrypt(encrypted_content)
            self.view.run_command('replace_input', {'start': 0, 'end': self.view.size(), 'text': plaintext})
            self.view.set_read_only(False)
        except Exception:
            sublime.message_dialog('password error')

    def on_modified(self):
        self.view.set_scratch(False)

    # 保存前加密
    def on_pre_save(self):
        self.content = self.view.substr(sublime.Region(0, self.view.size()))
        if self.get_ext() == '.stxt':
            encrypted_content = self.encrypt(self.content)
            self.view.run_command('replace_input', {'start': 0, 'end': self.view.size(), 'text': encrypted_content})

    def on_close(self):
        self.view.run_command('hide_panel')

    def get_password(self):
        print(self.st_pwd)
        if self.st_pwd == '':
            print('empty st_pwd')
            self.show_input_password()

        m = hashlib.md5()
        m.update(self.st_pwd.encode('utf-8'))
        s = m.digest()
        print(s)
        return s

    def encrypt(self, plaintext):
        key = self.get_password()
        aes = AES.new(key)
        plaintext = plaintext.encode('utf-8')
        pad_nr = AES.block_size - (len(plaintext) % AES.block_size)
        return base64.b64encode(aes.encrypt(plaintext + (pad_nr * C_PAD))).decode('utf-8')

    def decrypt(self, ciphertext):
        key = self.get_password()
        aes = AES.new(key)
        try:
            return aes.decrypt(base64.b64decode(ciphertext, validate=True)).rstrip(C_PAD).decode('utf-8')
        except (ValueError, binascii.Error) as e:
            sublime.message_dialog('password error')
            raise e

    def on_post_save(self):
        if self.get_ext() == '.stxt':
            self.view.run_command('replace_input', {'start': 0, 'end': self.view.size(), 'text': self.content})
            self.view.set_scratch(True)


def plugin_loaded():
    """Load and unzip the pre-built binary files, if needed."""
    sublime.set_timeout(init, 200)
