import json
import math
import os
import platform
import shutil
import socket
import subprocess
import sys

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.functions import GeneralFunctions, map_options, game_type_options
import platform
from pywinauto import Application

from src.generate_file import GenerateFile
from src.version import VERSION

class MyApp(tk.Tk):
    def __init__(self, profiles_dir, icons_dir, mods_dir):
        super().__init__()
        self.profiles_dir = profiles_dir
        self.mods_dir = mods_dir
        self.tab_control = tk.ttk.Notebook(self)
        self.function = GeneralFunctions()
        self.title(f"Call Of Duty 2 Server Manager {VERSION}")
        self.geometry("800x600")
        self.iconbitmap(os.path.join(icons_dir, 'Call-of-Duty-2.ico'))

        self.host = 'windows' if platform.system() == 'Windows' else 'mac' if platform.system() == 'Darwin' else ''
        self.tab_control.grid(rowspan=15, columnspan=10)
        self.root_window()
        self.create_tabs()
        self.run_function_every_minute()
        self.mainloop()

    def root_window(self):
        self.edit_button = tk.Button(self,text="Save and Apply all settings", command=self.save_config)
        self.edit_button.grid(row=20, column=0, columnspan=5, sticky='w', padx=5, pady=5)

    def save_config(self):
        new_maps_dict = self.function.get_maps_dict(map_vars=self.maps_tab.checkbox_map_vars)
        game_type = self.maps_tab.combo_box_game_type.get()
        config = {
            'ip': self.server_tab.ip_entry.get(),
            'port': self.server_tab.port_entry.get(),
            'filename': self.config_tab.path_entry.get(),
            'game_type': game_type,
            'full_game_path': self.config_tab.full_game_path.get(),
            'game_path': os.path.dirname(self.config_tab.full_game_path.get()),
            'maps': new_maps_dict
        }
        try:
            profile_file = self.profile_tab.get_profile_file_name()
            with open(profile_file, 'w') as f:
                json.dump(config, f)
                messagebox.showinfo("Saved", "Data has been saved.")
        except (FileNotFoundError, PermissionError) as e:
                messagebox.showinfo("Error", str(e))
        except Exception as e:
                messagebox.showinfo("Error", str(e))
        dirname = os.path.join(os.path.dirname(self.config_tab.full_game_path.get()), 'main')
        server_file = os.path.join(dirname, 'server.cfg')
        if self.config_tab.path_entry.get() and os.path.dirname(self.config_tab.full_game_path.get()):
            self.generate_cfg_file(new_maps_dict=new_maps_dict, game_type=game_type)
            shutil.copy(self.config_tab.path_entry.get(), server_file)
            messagebox.showinfo("cfg file moved", "CFG file has been moved.")

    def generate_cfg_file(self, new_maps_dict, game_type):
        G = GenerateFile(match_type=game_type, maps_dict=new_maps_dict, path_entry=self.config_tab.path_entry.get(),
                         ip_adress=self.server_tab.ip_entry.get())
        G.generate_match_type_setting()
        G.generate_ip_setting()
        G.generate_log_name()
        G.apply_settings()


    def run_function_every_minute(self):
        self.enable_buttons_based_game_running_config_set()
        self.profile_tab.get_profiles()
        self.mods_tab.get_available_mods()
        # get_running_map_name()
        self.after(3000, self.run_function_every_minute)

    def enable_buttons_based_game_running_config_set(self):
        if self.function.is_game_running(self.host):
            self.server_tab.stop_button.config(state="normal")
            self.server_tab.start_button.config(state="disabled")
            self.server_tab.reload_cfg_button.config(state='normal')
            self.server_tab.next_map_button.config(state="normal")
            self.server_tab.next_game_type_button.config(state="normal")
            self.server_tab.skip_map_button.config(state="normal")
        else:
            self.server_tab.next_map_button.config(state="disabled")
            self.server_tab.next_game_type_button.config(state="disabled")
            self.server_tab.next_map_button.config(state="disabled")
            self.server_tab.next_game_type_button.config(state="disabled")
            self.server_tab.skip_map_button.config(state='disabled')
            self.server_tab.reload_cfg_button.config(state='disabled')
        if len(self.config_tab.full_game_path.get()) > 0:
            self.server_tab.start_button.config(state="normal")
            self.mods_tab.add_mod_to_server_button.config(state='normal')
        else:
            self.server_tab.start_button.config(state="disabled")
            self.mods_tab.add_mod_to_server_button.config(state='disabled')


    def create_tabs(self):
        self.server_tab = ServerTab(self)
        self.tab_control.add(self.server_tab, text="Server")
        self.server_tab.create()
        self.config_tab = ConfigTab(self)
        self.tab_control.add(self.config_tab, text="Config")
        self.config_tab.create()

        self.maps_tab = MapsTab(self)
        self.tab_control.add(self.maps_tab, text="Maps")

        self.mods_tab = ModsTab(self)
        self.tab_control.add(self.mods_tab, text="Mods")
        self.mods_tab.create()

        self.profile_tab = ProfileTab(self)
        self.tab_control.add(self.profile_tab, text="Profile")

        # Create specific part after config is loaded
        self.maps_tab.create()


class ServerTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

    def check_server(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        if ip and port:
            server_address = (ip, int(port))
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            local_addres = (ip, 12345)
            message = b"test"
            try:
                udp_socket.bind(local_addres)
                udp_socket.sendto(message, server_address)
                message, local_addres = udp_socket.recvfrom(1024)
                if message:
                    self.status_label.config(text="Server is up!")
                    self.stoplight_canvas.itemconfig(self.stoplight, fill="green")

                else:
                    self.status_label.config(text=f"Server is down.")
                    if not self.stoplight_canvas.winfo_viewable():
                        self.stoplight_canvas.grid(row=4, column=0)
                    self.stoplight_canvas.itemconfig(self.stoplight, fill="red")

            except socket.error as e:
                self.status_label.config(text=f"Server is down. {e}")
                self.stoplight_canvas.itemconfig(self.stoplight, fill="red")
                if self.master.function.is_game_running(self.master.host):
                    self.stop_button.config(state="normal")
                    self.start_button.config(state="disabled")
                    self.reload_cfg_button.config(state='normal')
                else:
                    self.start_button.config(state="normal")

        else:
            self.status_label.config(text="Please enter IP address and port.")

    def stop_server(self):
        if self.master.function.is_game_running(self.master.host):
            pid = self.master.function.get_pid_game()
            # Stop the process with the PID
            subprocess.run(["taskkill", "/pid", pid, "/f"])
            self.status_label.config(text="Server stopped.")
            self.stop_button.config(state="disabled")
            self.reload_cfg_button.config(state="disabled")

    def reload_server(self):
        if self.master.function.is_game_running(self.master.host):
            app = Application().connect(process=int(self.master.function.get_pid_game()))
            game_window = app.top_window()
            game_window.type_keys("exec{SPACE}server.cfg{ENTER}")
            self.status_label.config(text="Server CFG reloaded.")
            self.stoplight_canvas.itemconfig(self.stoplight, fill="green")

    def start_server(self):
        if not self.master.config_tab.path_entry:
            messagebox.showinfo("Error", 'Configure your path in config tab')
        else:
            self.master.save_config()
            config = r'server.cfg'
            full_command = f'{self.master.config_tab.full_game_path.get()} +exec {config}'
            proc = subprocess.Popen(
                full_command, cwd=self.master.config_tab.game_path.get())
            # app = pywinauto.Application().start(full_command, work_dir=game_path.get())

    def go_to_next_map(self):
        self.master.function.next_map(host=self.master.host, status_label=self.status_label, stoplight_canvas=self.stoplight_canvas, stoplight=self.stoplight,
                 value=self.next_map_combobox.get())

    def go_to_next_game_type(self):
        self.master.function.next_game_type(host=self.master.host, status_label=self.status_label, stoplight=self.stoplight, stoplight_canvas=self.stoplight_canvas,
                       value=self.next_game_type_combobox.get())

    def go_skip_map(self):
        self.master.function.skip_map(host=self.master.host, status_label=self.status_label, stoplight=self.stoplight, stoplight_canvas=self.stoplight_canvas)

    def create(self):
        # notebook.add(self.server_tab, text="Server")
        # Create server tab
        self.ip_label = tk.Label(self, text="IP Address:")
        self.ip_label.grid(row=0, column=0, sticky='w')
        self.ip_entry = tk.Entry(self)
        self.ip_entry.grid(row=0, column=1, sticky='w')
        self.ip_entry.bind('<Button-1>', self.enable_check_button)

        self.fill_local_ip_button = tk.Button(self, text="Fill in local IP", command=self.fill_local_ip)
        self.fill_local_ip_button.grid(row=0, column=3, sticky='w')

        self.port_label = tk.Label(self, text="Port:")
        # port_label.pack()
        self.port_label.grid(row=2, column=0, sticky='w')

        self.port_entry = tk.Entry(self)
        # port_entry.pack()
        self.port_entry.bind('<Button-1>', self.enable_check_button)
        # port_entry.insert(0, "28960")
        self.port_entry.grid(row=2, column=1, sticky='w')

        self.check_button = tk.Button(self, text="Check", command=self.check_server, state="disabled")
        self.check_button.grid(row=3, column=1, sticky='w')

        self.status_label = tk.Label(self, text="")
        self.status_label.grid(row=4, column=1, sticky='w', columnspan=5)

        # Create a canvas to draw the stoplight
        self.stoplight_canvas = tk.Canvas(self, width=20, height=20)

        # Draw a gray circle to start
        self.stoplight = self.stoplight_canvas.create_oval(0, 0, 20, 20, fill="gray")
        self.stoplight_canvas.grid(row=4, column=0)

        # create separator
        self.sep_server = ttk.Separator(self, orient='horizontal')
        # sep_server.pack(fill='x', padx=5, pady=5)
        self.sep_server.grid(row=5, column=0, sticky='ew', columnspan=9, rowspan=2, padx=5, pady=5)

        self.acties_label = tk.Label(self, text="Server actions")
        self.acties_label.grid(row=7, column=0, sticky='w', padx=5, pady=5)

        self.start_button = tk.Button(self, text="Start", command=self.start_server, state="normal")
        self.start_button.grid(row=7, column=2, sticky='w', padx=5, pady=5)

        self.reload_cfg_button = tk.Button(self, text="Reload CFG", command=self.reload_server, state="disabled")
        self.reload_cfg_button.grid(row=7, column=3, sticky='w', padx=5, pady=5)

        self.stop_button = tk.Button(self, text="Stop", command=self.stop_server, state="disabled")
        self.stop_button.grid(row=7, column=4, sticky='w', padx=5, pady=5)

        self.next_map_label = tk.Label(self, text="Change map")
        self.next_map_label.grid(row=8, column=0, sticky='w', padx=5, pady=5)
        self.next_map_combobox = ttk.Combobox(self, values=map_options)
        self.next_map_combobox.set('toujane')
        self.next_map_combobox.grid(row=8, column=1, sticky='w', padx=5, pady=5)

        self.next_map_button = tk.Button(self, text="Apply", command=self.go_to_next_map, state="normal")
        self.next_map_button.grid(row=8, column=2, sticky='w', padx=5, pady=5)

        self.next_game_type_label = tk.Label(self, text="Change gametype")
        self.next_game_type_label.grid(row=9, column=0, sticky='w', padx=5, pady=5)
        self.next_game_type_combobox = ttk.Combobox(self, values=game_type_options)
        self.next_game_type_combobox.grid(row=9, column=1, sticky='w', padx=5, pady=5)
        self.next_game_type_combobox.set('Death Match')

        self.next_game_type_button = tk.Button(self, text="Apply", command=self.go_to_next_game_type, state="normal")
        self.next_game_type_button.grid(row=9, column=2, sticky='w', padx=5, pady=5)

        self.skip_map_button = tk.Button(self, text="Skip current map", command=self.go_skip_map, state="normal")
        self.skip_map_button.grid(row=8, column=3, sticky='w', padx=5, pady=5)

    def enable_check_button(self,event):
        if len(self.ip_entry.get()) > 0 and len(self.port_entry.get()) > 0:
            self.check_button.config(state="normal")
        else:
            self.check_button.config(state="disabled")

    def fill_local_ip(self):
        ip = socket.gethostbyname(socket.gethostname())
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, ip)


class ConfigTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)


    def open_cfg_file_dialog(self, event):
        filename = filedialog.askopenfilename(filetypes=[('Cfg files', '.cfg')])
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
            self.edit_file_button.config(state="normal")
        else:
            self.edit_file_button.config(state="disabled")

    def open_game_file_dialog(self, event):
        filename = filedialog.askopenfilename(filetypes=[('exe', '.exe')])
        if filename:
            self.full_game_path.delete(0, tk.END)
            self.full_game_path.insert(0, filename)
            self.game_path.delete(0, tk.END)
            self.game_path.insert(0, os.path.dirname(filename))

    def enable_edit_button(self, event):
        if len(self.path_entry.get()) > 0:
            self.edit_file_button.config(state="normal")
        else:
            self.edit_file_button.config(state="disabled")

    def edit_config_file(self):
        filename = self.path_entry.get() if self.path_label else ""
        with open(filename, 'r') as f:
            contents = f.read()
        edit_window = tk.Toplevel()
        edit_window.title("Edit Config File")
        text_widget = tk.Text(edit_window)
        text_widget.insert(tk.END, contents)
        text_widget.grid(row=0, column=0)

        def save_changes():
            new_contents = text_widget.get("1.0", tk.END)
            with open(filename, 'w') as f:
                f.write(new_contents)
            edit_window.destroy()

        save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
        save_button.grid()

    def create(self):

        self.path_label = tk.Label(self, text="Server CFG file:")
        self.path_label.grid(row=0, column=0, sticky='w')

        self.path_entry = tk.Entry(self, width=60)
        self.path_entry.grid(row=0, column=1, sticky='w')
        self.path_entry.bind("<Button-1>", self.open_cfg_file_dialog)
        self.path_entry.bind('<KeyRelease>', self.enable_edit_button)

        self.full_game_path_label = tk.Label(self, text="Multiplayer executable")
        self.full_game_path_label.grid(row=1, column=0, sticky='w')

        self.full_game_path = tk.Entry(self, width=100)
        self.full_game_path.grid(row=1, column=1, sticky='w')
        self.full_game_path.bind("<Button-1>", self.open_game_file_dialog)

        self.game_path_label = tk.Label(self, text="Call of Duty install directory")
        self.game_path_label.grid(row=2, column=0, sticky='w')

        self.game_path = tk.Entry(self, state='readonly', width=100)
        self.game_path.grid(row=2, column=1, sticky='w')

        self.edit_file_button = tk.Button(self, text="Edit Config File", command=self.edit_config_file)
        self.edit_file_button.grid(row=3, column=0, sticky='w')


class ProfileTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.profiles_list = []
        self.create()
        self.load_config()

    def get_profiles(self):
        profiles_dir = self.master.profiles_dir
        if os.path.isdir(profiles_dir):
            for file in os.listdir(profiles_dir):
                if file.endswith(".json"):
                    if file not in self.profiles_list:
                        self.profiles_list.append(file)
                        self.profile_load_combobox.config(value=self.profiles_list)

    def get_profile_file_name(self):
        if len(self.profile_name.get()) > 0:
            if self.profile_name.get().endswith(".json"):
                CONFIG_FILE = os.path.join(self.master.profiles_dir, self.profile_name.get())
                # CONFIG_FILE = os.path.join('profiles', self.profile_name.get())
            else:
                full_name = f'{self.profile_name.get()}.json'
                CONFIG_FILE = os.path.join(self.master.profiles_dir, full_name)
                # CONFIG_FILE = os.path.join('profiles', full_name)
        else:
            CONFIG_FILE = os.path.join(self.master.profiles_dir, 'config.json')
        return CONFIG_FILE

    def select_profile_to_load(self):
        self.profile_name.delete(0, tk.END)
        self.profile_name.insert(0, self.profile_load_combobox.get())
        self.master.maps_tab.reinitialize()

    def load_config(self):
        if os.path.isfile(self.get_profile_file_name()):
            with open(self.get_profile_file_name(), 'r') as f:
                config = json.load(f)
                self.master.server_tab.ip_entry.delete(0, tk.END)
                self.master.server_tab.ip_entry.insert(0, config.get('ip', ''))
                self.master.server_tab.port_entry.delete(0, tk.END)
                self.master.server_tab.port_entry.insert(0, config.get('port', ''))
                self.master.config_tab.path_entry.delete(0, tk.END)
                self.master.config_tab.path_entry.insert(0, config.get('filename', ''))
                self.master.maps_tab.combo_box_game_type.insert(0, config.get('game_type', 'Death Match'))
                self.master.config_tab.full_game_path.delete(0, tk.END)
                self.master.config_tab.full_game_path.insert(0, config.get('full_game_path', ''))
                self.master.config_tab.game_path.config(state='normal')
                self.master.config_tab.game_path.delete(0, tk.END)
                self.master.config_tab.game_path.insert(0, config.get('game_path', ''))
                self.master.config_tab.game_path.config(state='disabled')
                self.master.maps_tab.maps_dict.update(config.get('maps', {}))

    def create(self):
        # add config map tab
        self.profile_name_label = tk.Label(self, text="Save to profile name")
        self.profile_name_label.grid(row=2, column=0, sticky='w', padx=5, pady=5)

        self.profile_name = tk.Entry(self, width=40)
        self.profile_name.insert(0, string='profile.json')
        self.profile_name.grid(row=2, column=1, sticky='w')

        self.profile_load_label = tk.Label(self, text="Load Profile")
        self.profile_load_label.grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.profile_load_combobox = ttk.Combobox(self, values=self.profiles_list)
        self.profile_load_combobox.grid(row=3, column=1, sticky='w', padx=5, pady=5)

        self.load_profile_button = tk.Button(self, text="Load Selected Profile", command=self.select_profile_to_load)
        self.load_profile_button.grid(row=3, column=2, sticky='w')



class MapsTab(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        # create a list of options for the combobox
        self.game_type_options = ["Death Match", "Team Deathmatch", "Search & Destroy", "Capture the Flag", "Head Quaters",
                             "Retrieval", "Domination", "Sabotage", "VIP escort"]
        self.maps_dict = {}
        self.game_type_label = tk.Label(self, text="Select Game Type")
        self.game_type_label.grid(row=15, column=0, sticky='w')

        # create a combobox and add the options to it
        self.combo_box_game_type = ttk.Combobox(self, values=self.game_type_options)
        self.combo_box_game_type.grid(row=15, column=1, sticky='w')

    def create(self):
        self.checkbox_map_vars = []
        self.checkboxes_map = []
        items = len(map_options)
        cols = 5
        rows = math.ceil(items / cols)
        total_cols = 0
        padx = 5
        pady = 5
        for row in range(rows):
            col = 0
            while col < cols and total_cols < items:
                value = self.master.function.set_maps_vars(map_options[total_cols], maps_dict=self.maps_dict)
                var = tk.BooleanVar(name=map_options[total_cols], value=value)
                self.checkbox_map_vars.append(var)
                maps_checkbox = tk.Checkbutton(self, text=map_options[total_cols], variable=var)
                self.checkboxes_map.append(maps_checkbox)
                # maps_checkbox.pack()
                maps_checkbox.grid(row=row, column=col, padx=padx, pady=pady, sticky='w')
                col = col + 1
                total_cols = total_cols + 1

    def reinitialize(self):
        self.maps_tab = MapsTab(self)
        self.game_type_label = tk.Label(self, text="Select Game Type")
        self.game_type_label.grid(row=15, column=0, sticky='w')

        # create a combobox and add the options to it
        self.combo_box_game_type = ttk.Combobox(self, values=self.game_type_options)
        self.combo_box_game_type.grid(row=15, column=1, sticky='w')
        self.master.profile_tab.load_config()
        self.create()


class ModsTab(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.mods_list = []
        self.mods_sub_dir = self.master.mods_dir

    def create(self):
        self.select_mod_label = tk.Label(self, text="Select Mod")
        self.select_mod_label.grid(row=2, column=0, sticky='w')
        self.combo_box_select_mod = ttk.Combobox(self, values=self.mods_list)
        self.combo_box_select_mod.grid(row=2, column=1, sticky='w')
        self.add_mod_to_server_button = tk.Button(self, text="Apply mod to server", command=self.add_mod_to_server)
        self.add_mod_to_server_button.grid(row=2, column=2, sticky='w')

    def add_mod_to_server(self):
        if self.combo_box_select_mod.get() != '':
            mod_dir = os.path.join(self.mods_sub_dir, self.combo_box_select_mod.get())
            main_dirname = os.path.join(os.path.dirname(self.master.config_tab.full_game_path.get()), 'main')
            # http_server_dir = os.path.join(os.getcwd(), 'httpserver_dir', 'main')
            for file in os.listdir(mod_dir):
                filepath = os.path.join(mod_dir, file)
                shutil.copy(filepath, main_dirname)
                # shutil.copy(filepath, http_server_dir)
            messagebox.showinfo(f"Mods {self.combo_box_select_mod.get()}", f"{self.combo_box_select_mod.get()} has been applied to server.")

    def get_available_mods(self):
        if os.path.isdir(self.mods_sub_dir):
            for sub_dir in os.listdir(self.mods_sub_dir):
                is_it_a_dir = os.path.join(self.mods_sub_dir, sub_dir)
                if os.path.isdir(is_it_a_dir):
                    if sub_dir not in self.mods_list:
                        self.mods_list.append(sub_dir)
                        self.combo_box_select_mod.config(value=self.mods_list)
