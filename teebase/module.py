import subprocess
import time
class teeController:
    def __init__(self, window_name, timeout, username):
        self.window_name = window_name
        self.timeout = timeout
        self.username = username
        self.logname = str(time.strftime("%Y%m%d.log"))

    def display_info(self):
        return f'''
        Window Name: {self.window_name}
        Timeout: {self.timeout}ms
        Username: {self.username}
        Logname: {self.logname}
        '''
    

    def start(self):
        commands = [
            "title " + self.window_name,
            "wsl ssh " + self.username + "@telehack.com -p 2222 | wsl tee -a " + self.logname
        ]
        command = "&& ".join(commands)
        process = subprocess.run(["wt", "-d", ".", "cmd", "/k", command], shell=True)

    def readLast(self, lines):
        with open(self.logname, 'r') as f:
            return f.readlines()[-lines:]