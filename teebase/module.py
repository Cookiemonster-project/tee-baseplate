import subprocess
import time
import re
import os
import pygetwindow as gw

from pywinauto import Application

import pyautogui as pg
pg.FAILSAFE = False
class teeController:
    def __init__(self, window_name, username, host, timeout, delay):
        self.window_name = window_name
        self.timeout = timeout
        self.username = username
        self.logname = str(time.strftime("%Y%m%d")) + "_" + window_name + ".log"
        self.host = host
        self.delay = delay / 1000

    def display_info(self):
        return f'''
        Window Name: {self.window_name}
        Delay: {self.delay}s
        Timeout: {self.timeout}s
        Username: {self.username}
        Logname: {self.logname}
        Host: {self.host}
        '''
    
    def start(self):
        commands = [
            "title " + self.window_name,
            "wsl ssh " + self.username + "@" + self.host + " -p 2222 | wsl tee " + self.logname
        ]
        command = "&& ".join(commands)
        process = subprocess.Popen(["wt", "-d", ".", "cmd", "/k", command])
        while not os.path.exists(self.logname):
            time.sleep(1)
        print(f"Process started on PID: {process.pid}")

    def readLast(self, lines):
        try:
            with open(self.logname, 'r') as f:
                try:
                    lines = f.readlines()[-lines:]
                except IndexError:
                    return False
                stripped_lines = [self._getRawLine(line) for line in lines]
                return stripped_lines
        except FileNotFoundError:
            print("File not found")
            return False

    def _getRawLine(self, line):
        line = line.replace('\x00', '')
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)
        
    def awaitStatic(self):
        old = ""
        out = "?"
        start_time = time.time()
        while True:
            old = out
            try:
                out = self.readLast(1)[0]
            except:
                continue
            if old == out and any(char in out[len(out)-3:] for char in [">", ":", "@", "$", "%"]):
                break
            if time.time() - start_time > self.timeout:
                print("Timeout reached while waiting for static terminal.")
                return False
            time.sleep(self.delay)
        return True
    
    def awaitString(self, string):
        start_time = time.time()
        while True:
            try:
                last = self.readLast(1)[0]
            except:
                continue
            if string in last:
                return True
            if time.time() - start_time > self.timeout:
                print("Timeout reached while waiting for string.")
                return False
            time.sleep(self.delay)


    def focusWindow(self):
        try:
            app = Application().connect(title=self.window_name)
            window = app.window(title=self.window_name)

            window.set_focus()
            return True
        except:
            print(f"Window '{self.window_name}' not found.")
            return False



        
    def write(self, keys, focus=False):
        if focus:
            self.focusWindow()
        pg.write(keys)

    def ctrl(self, key, focus=False):
        if focus:
            self.focusWindow()
        pg.hotkey('ctrl', key)
    