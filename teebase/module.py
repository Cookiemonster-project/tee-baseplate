import subprocess
import time
import re
import os
from pywinauto import Application
import pyautogui as pg

pg.FAILSAFE = False

class teeController:
    def __init__(self, window_name: str, username: str, host: str, timeout: int, delay: int, manualMode=False):
        self.window_name = window_name
        self.timeout = timeout
        self.username = username
        self.logname = str(time.strftime("%Y%m%d")) + "_" + window_name + ".log"
        self.host = host
        self.delay = delay / 1000
        self.manualMode = manualMode


    def display_info(self):
        return f'''
        Window Name: {self.window_name}
        Delay: {self.delay}s
        Timeout: {self.timeout}s
        Username: {self.username}
        Logname: {self.logname}
        Host: {self.host}
        Manual Mode: {self.manualMode}
        '''
    
    def start(self):
        if not self.manualMode:
            commands = [
                "title " + self.window_name,
                "wsl ssh " + self.username + "@" + self.host + " -p 2222 | wsl tee " + self.logname
            ]
            command = "&& ".join(commands)
            process = subprocess.Popen(["wt", "-d", ".", "cmd", "/k", command])
        else:
            commands = [
                "ssh " + self.username + "@" + self.host + " -p 2222 | " + os.path.join(os.path.dirname(__file__), 'tee-x64.exe') + " " + self.logname
            ]
            command = "&& ".join(commands)
            process = subprocess.Popen(["wt", "-d", ".", "--title", self.window_name, "--suppressApplicationTitle", "cmd", "/k", command])
            #pg.alert(text=f"Please manually set the window's title to {self.window_name}", title='WARNING', button='OK')

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
            out = self.readLast(1)[0]
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
            last = self.readLast(1)[0]
            if string in last:
                return True
            if time.time() - start_time > self.timeout:
                print("Timeout reached while waiting for string.")
                return False
            time.sleep(self.delay)


    def focusWindow(self):
        app = Application().connect(title=self.window_name)
        window = app.window(title=self.window_name)
        if window.exists(timeout=self.timeout):
            window.set_focus()
            return True
        else:
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
    