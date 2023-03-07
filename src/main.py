import shutil

from src.app import MyApp
import sys
import os


# Run only if pyinstaller is used
def copy_files_to_config_dir():
    # Create the directory if it doesn't exist
    os.makedirs(destination_config_dir, exist_ok=True)
    # os.makedirs(profiles_dir, exist_ok=True)
    # os.makedirs(os.path.join(config_dir,'server_config'), exist_ok=True)
    # Copy the files from the application directory to the user config directory

    dirs_to_copy = [{'source_dir': source_profiles_dir, 'destination_dir': destination_profiles_dir},
                    {'source_dir': source_server_config_dir, 'destination_dir': destination_server_config_dir},
                    {'source_dir': source_mods_dir, 'destination_dir': destination_mods_dir}]
    for dir in dirs_to_copy:
        if os.path.exists(dir['destination_dir']):
            for source_file in os.listdir(dir['source_dir']):
                dest_files = os.listdir(dir['destination_dir'])
                if source_file in dest_files:
                    continue
                else:
                    shutil.copy(dir['source_dir'], os.path.join(dir['destination_dir'], source_file))

        else:
            shutil.copytree(dir['source_dir'], dir['destination_dir'])

        # shutil.copytree(source_server_config_dir, destination_server_config_dir, copy_function=shutil.copy2,
        #                     dirs_exist_ok=True)
        # shutil.copytree(source_mods_dir, destination_mods_dir, copy_function=shutil.copy2, dirs_exist_ok=True)


if __name__ == "__main__":

    # running in a PyInstaller bundle
    # Get path of documents directory
    destination_config_dir = os.path.expanduser("~\Documents\COD2_SERVER_GUI")
    destination_profiles_dir = os.path.join(destination_config_dir, 'profiles')
    destination_server_config_dir = os.path.join(destination_config_dir, 'server_config')
    destination_mods_dir = os.path.join(destination_config_dir, 'mods')

    if getattr(sys, 'frozen', False):
        icons_dir = os.path.join(sys._MEIPASS, 'icons')
        img_dir = os.path.join(sys._MEIPASS, 'img')
        source_profiles_dir = os.path.join(sys._MEIPASS, 'profiles')
        source_server_config_dir = os.path.join(sys._MEIPASS, 'server_config')
        source_mods_dir = os.path.join(sys._MEIPASS, 'mods')
    else:
        icons_dir = os.path.join(os.getcwd(), 'src', 'icons')
        img_dir = os.path.join(os.getcwd(), 'src', 'img')
        source_profiles_dir = os.path.join(os.getcwd(), 'src', 'profiles')
        source_server_config_dir = os.path.join(os.getcwd(), 'src', 'server_config')
        source_mods_dir = os.path.join(os.getcwd(), 'src', 'mods')

    copy_files_to_config_dir()
    app = MyApp(destination_profiles_dir, icons_dir, destination_mods_dir, img_dir)
