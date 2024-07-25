import os
import requests
import logging
import urllib3
from win32com.client import Dispatch
import PopupView
from AppConfigReader import AppConfigReader

class FFMpegInstaller:

    required_files = ['ffplay.exe', 'ffmpeg.exe', 'ffprobe.exe']
    BaseURL = f'https://ilollek.net/PYD-REM-ASSETS/'

    def install_ffmpeg(directory: str, update_callback) -> bool:
        """Installs FFmpeg (ffmpeg.exe, ffprobe.exe, ffplay.exe) into the directory you provide as the argument.
        
        Args:
            - directory (str): The Directory to install the .exe Files into
            - update_callback (any): The Update callback

        Returns:
            - success (bool): True if Installation worked, False otherwise"""
        
        try:
            update_callback("Installing...")
            for file in FFMpegInstaller.required_files:
                update_callback(f'Installing {file}...')
                url = FFMpegInstaller.BaseURL + file
                response = requests.get(url)
                if response.status_code == 200:
                    with open(os.path.join(directory, file), 'wb') as f:
                        f.write(response.content)
                    logging.info(f"Downloaded and installed {file}")
                else:
                    logging.error(f"Failed to download {file}. Status code: {response.status_code}")
                    return False
            PopupView.show_info_box(f'Installation Successful!', f'Successfully installed FFmpeg!')
            update_callback(f'FFmpeg: Installed!')
            return True
        except requests.exceptions.ConnectionError as e:
            logging.exception(f"An error occurred during FFmpeg installation: {e}")
            return False
        except urllib3.exceptions.ProtocolError as e:
            logging.exception(f"An error occurred during FFmpeg installation: {e}")
            return False
        except Exception as e:
            logging.exception(f"An error occurred during FFmpeg installation: {e}")
            return False

    def CheckIfFFmpegIsInstalled(directory: str) -> bool:
        """Checks if FFmpeg is installed at the directory you provide as the argument.
        It Checks if all 3 required EXEs are present in the Directory. If one is missing,
        it will return FALSE.
        
        Args:
            - directory (str): The Directory to check

        Returns:
            - success (bool): True if all 3 ffmpeg EXEs are present, False otherwise"""
        
        required_files = FFMpegInstaller.required_files
        for file in required_files:
            if not os.path.isfile(os.path.join(directory, file)):
                return False
        return True

class MainInstallUtils:

    def CheckIfFirstTimeRun(program_directory: str) -> bool:
        """Checks if the Program is being run for the first time by checking if a SystemData Folder exists and a app.config File is present inside the SystemData Folder.
        
        Args:
            - program_directory (str): The Directory where SystemData should be present
            
        Returns:
            - FirstTimeRun (bool): True if it's being run for the First Time, False Otherwise."""
        
        system_data_folder = os.path.join(program_directory, 'SystemData')
        app_config_file = os.path.join(system_data_folder, 'app.config')

        # Check if the SystemData folder exists
        if os.path.exists(system_data_folder):
            # Check if the app.config file exists inside the SystemData folder
            if os.path.exists(app_config_file):
                # Not the first time run
                return False
            else:
                # First time run
                return True
        else:
            # First time run
            return True
    
    def CreateDesktopShortcut(program_directory: str) -> bool:
        """Creates a Desktop Shortcut (Icon on the Desktop)
        
        Args:
            - program_directory (str): The Directory where PyYtDownloader-Remastered.exe should be present.
            
        Returns:
            - success (bool): True if everything worked, False otherwise."""
        # Create a desktop shortcut with the icon
        try:
            path = os.path.join(os.environ['USERPROFILE'], 'Desktop', f'PyYtDownloader-Remastered.lnk')
            target = f"{program_directory}\\PyYtDownloader Remastered.exe"  # The shortcut target file or folder
            work_dir = program_directory  # The parent folder of your file

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = work_dir
            shortcut.IconLocation = f"{program_directory}\\PyYtDownloader Remastered.exe"
            shortcut.save()
            return True
        except Exception as e:
            logging.error(f'An Error occoured while trying to create a Desktop Shortcut: {e}')
            PopupView.show_error_box(f'Fatal Error', f'Unable to create Desktop Shortcut: {e}')
            return False
        
    def CreateSystemDataFolder(program_directory: str) -> bool:
        """Creates a SystemData Folder at program_directory
        
        Args:
            - program_directory (str): The Directory where the SystemData Folder should get created.
            
        Returns:
            - success (bool): True if everything worked, False otherwise."""
        
        try:
            system_data_folder = os.path.join(program_directory, "SystemData")
            
            if not os.path.exists(system_data_folder):
                os.makedirs(system_data_folder)
                logging.info("SystemData folder created successfully.")
                return True
            else:
                logging.warn("SystemData folder already exists.")
                return True
        except Exception as e:
            logging.error(f"Error creating SystemData folder: {e}")
            PopupView.show_error_box(f'Fatal Error', f'Error creating SystemData folder: {e}')
            return False

    def CreateAppConfigFile(program_directory: str) -> bool:
        """Creates a new app.config File with default Values.
        
        Args:
            - program_directory (str): The Directory where the SystemData Folder is present.
            
        Returns:
            - success (bool): True if everything worked, False otherwise."""
        
        DEFAULT_VALUES = f"""
CustomOutputPath || {os.path.join(os.environ['USERPROFILE'], 'Desktop')}
YouTubeCookiePath || None
ColorTheme || GreenTheme
UseSFX || True
UseProxy || False
UseCookie || False
ProxyHost || public.proxy.net
ProxyPort || 8080
ProxyUseCredentials || False
ProxyCredentialsUser || User
ProxyCredentialsPassword || Password
UseMP3Tags || True
UseLastFMAPI || False
LastFMAPIKey || False
        """
        try:
            with open(f'{program_directory}\\SystemData\\app.config', "w") as f:

                f.write(f'{AppConfigReader.COMMENT}\n{DEFAULT_VALUES}')
            return True
        except Exception as e:
            logging.error(f'Error Creating app.config: {e}')
            PopupView.show_error_box(f'Fatal Error', f'Error creating app.config File: {e}')
            return False
        



if __name__ == "__main__":
    print(MainInstallUtils.CheckIfFirstTimeRun(os.getcwd()))
    print(os.getcwd())
