import json
import os
from datetime import datetime

game_type_option_values = {
    'Death Match': 'dm',
    'Team Deathmatch': 'tdm',
    'Search & Destroy': 'sd',
    'Capture the Flag': 'ctf',
    'Retrieval': 're',
    'Domination': 'dom',
    'Sabotage': 'sab',
    'VIP Escort': 'vip',

}


class GenerateFile():
    def __init__(self, ip_adress, match_type, maps_dict, path_entry):
        self.ip_entry = None
        self.port_entry = None
        self.config_file = path_entry
        self.combo_box_game_type = None
        self.match_type = match_type
        self.match_type_value = self.get_match_type_value(self.match_type)
        self.settings_to_apply = {}
        self.maps_dict = maps_dict
        self.maps_string = self.get_maps_string()
        self.ip_adress = ip_adress

    def get_map_name(self, option):
        return f'mp_{option}'

    def apply_settings_to_file(self):
        for key, value in self.settings_to_apply.items():
            self.replace_or_add_string_in_file(key, value)

    def get_maps_string(self):
        maps = ''
        for key, value in self.maps_dict.items():
            if value == True:
                maps += f'mp_{key};'
        return maps

    def generate_match_type_setting(self):
        map_rotate = self.generate_command_string(start='set sv_mapRotationCurrent "',
                                                  type_prefix=f'gametype {self.match_type_value} map',
                                                  string=self.maps_string, end_string='"')
        self.settings_to_apply['sv_mapRotationCurrent'] = map_rotate

    def generate_ip_setting(self):
        ip_setting = self.generate_command_string(start='set net_ip "', type_prefix="", string=self.ip_adress, end_string='"', with_spaces=False)
        self.settings_to_apply['net_ip'] = ip_setting

    def generate_log_name(self):
        current_date = datetime.now().date()
        date_log_file = self.generate_command_string(start='set g_log "', type_prefix="", string=f"server_mp_{current_date}.log", end_string='"', with_spaces=False)
        self.settings_to_apply['g_log'] = date_log_file

    def generate_command_string(self, start, type_prefix, string, end_string, with_spaces=True):
        command = start
        for item in string.split(';'):
            if item != '':
                if type_prefix:
                    command += f'{type_prefix} {item}'
                else:
                    command += f'{item}'
                if with_spaces:
                    command += f' '
        command += end_string
        return command

    @staticmethod
    def get_match_type_value(match_type):
        if match_type:
            for key, value in game_type_option_values.items():
                if key == match_type:
                    return value
            return None

    def replace_or_add_string_in_file(self, old_string, new_string):
        with open(self.config_file, 'r') as f:
            lines = f.readlines()

        changed = False

        # Replace the old string with the new string, or add it if it doesn't exist
        with open(self.config_file, 'w') as f:
            for line in lines:
                if old_string in line:
                    changed = True
                    line = new_string + "\n"
                f.write(line)

        if not changed:
            with open(self.config_file, 'a') as f:
                f.write(new_string)


    def apply_settings(self):
        for key, value in self.settings_to_apply.items():
            self.replace_or_add_string_in_file(key, value)
