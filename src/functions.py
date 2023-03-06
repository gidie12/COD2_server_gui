import subprocess

import psutil

from src.generate_file import GenerateFile

CONFIG_FILE = 'profiles/config.json'
# create a list of options for the combobox
game_type_options = ["Death Match", "Team Deathmatch", "Search & Destroy", "Capture the Flag", "Head Quaters",
                     "Retrieval", "Domination", "Sabotage", "VIP escort"]

map_options = ["brecourt",
               "burgundy",
               "carentan",
               "dawnville",
               "decoy",
               "downtown",
               "farmhouse",
               "leningrad",
               "matmata",
               "railyard",
               "toujane",
               "trainstation",
               "abbey",
               "aldernest",
               "breakout",
               "dawnville2",
               "downtown_sniper",
               "farmhouse2",
               "lolv2",
               "makin",
               "makin_day",
               "rhine",
               "tigertown",
               "toujane_night",
               "villers_bocage",
               "xi",
               "port"]

from pywinauto import Application

class GeneralFunctions():

    def get_pid_game(self):
        # Find the process ID (PID) of the Call of Duty 2 multiplayer process
        process_name = "CoD2MP_s.exe"
        result = subprocess.run(["tasklist", "/fi", f"imagename eq {process_name}"], capture_output=True, text=True)
        pid_line = next((line for line in result.stdout.split("\n") if process_name in line), None)
        if pid_line:
            return pid_line.split()[1]
        else:
            return None


    def is_game_running(self,host):
        if host == 'windows':
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.name() == "CoD2MP_s.exe":
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        if host == 'mac':
            output = subprocess.check_output(["ps", "-A"])
            lines = output.decode().split("\n")
            for line in lines:
                if "CoD2MP_s" in line:
                    return True
        return False


    def get_maps_dict(self,map_vars):
        maps_dict = {}
        for item in map_vars:
            maps_dict[str(item)] = bool(item.get())
        return maps_dict


    def set_maps_vars(self,item, maps_dict):
        for key, value in maps_dict.items():
            if str(item) == str(key):
                return value
        return False


    def next_map(self,value, host, status_label, stoplight_canvas, stoplight):
        if self.is_game_running(host):
            new_map = f'mp_{value}'
            app = Application().connect(process=int(self.get_pid_game()))
            game_window = app.top_window()
            game_window.type_keys("map{SPACE}"+ new_map + "{ENTER}")
            status_label.config(text=f"Server changed map to {value}")
            stoplight_canvas.itemconfig(stoplight, fill="green")


    def next_game_type(self,host, value, status_label, stoplight_canvas, stoplight):
        if self.is_game_running(host):
            match_type = GenerateFile.get_match_type_value(value)
            app = Application().connect(process=int(self.get_pid_game()))
            game_window = app.top_window()
            game_window.type_keys("g_gametype{SPACE}" + match_type + "{ENTER}")
            # game_window.type_keys("map_restart{ENTER}")
            status_label.config(text=f"Server changed game type to {value} on end of current map")
            stoplight_canvas.itemconfig(stoplight, fill="green")

    def skip_map(self,host, status_label, stoplight, stoplight_canvas):
        if self.is_game_running(host):
            app = Application().connect(process=int(self.get_pid_game()))
            game_window = app.top_window()
            game_window.type_keys("map_rotate{ENTER}")
            status_label.config(text=f"Server skipped current map")
            stoplight_canvas.itemconfig(stoplight, fill="green")