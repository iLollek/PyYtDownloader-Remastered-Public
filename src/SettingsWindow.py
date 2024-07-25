import customtkinter
from tkinter import filedialog
from AppConfigReader import AppConfigReader
import logging
import PopupView
import os
import yt_dlp
import MiscUtils
from Installer import FFMpegInstaller
import sys
import threading

ResourceObtainerInstance = MiscUtils.ResourceObtainer()

VERSION = "1.3"
INTERACTED_WITH_SETTINGSWINDOW = False

def SettingsWindowCheckAppConfig() -> bool:
    """Checks if app.config has been read correctly and instanciates a global config"""
    global config
    logging.info(f'Checking app.config File Content for Settings Window')
    config = AppConfigReader("app.config")
    if config.CheckForAppConfigFile():
        config.ReadAppConfig()
        logging.info(f'Read app.config for SettingsWindow successfully!')
    else:
        logging.warn(f'No app.config Found - The Main script should probably handle this, continuing with default values for now.')
        return False
    if config.VerifyIntegrity():
        logging.info(f'Integrity of app.config Verified Successfully!')
        return True
    else:
        logging.warn(f'Unable to verify Integrity of app.config for SettingsWindow.')
        return False

SettingsWindowCheckAppConfig()

def ChangeColorTheme():
    ColorTheme = config.GetConfigKeyValue("ColorTheme")
    print(f'ColorTheme: {ColorTheme}')
    if ColorTheme == "BlueTheme":
        print("Loading Blue Theme")
        customtkinter.set_default_color_theme("blue")
    elif ColorTheme == "GreenTheme":
        print("Load Green Theme")
        customtkinter.set_default_color_theme("green")
    elif ColorTheme == "DarkBlueTheme":
        print("Load Dark Blue Theme")
        customtkinter.set_default_color_theme("dark-blue")

ChangeColorTheme()

customtkinter.set_appearance_mode("System")


class App(customtkinter.CTk):

    HEIGHT = 350
    WIDTH = 600

    def __init__(self):
        super().__init__()
        self.title("PyYtDownloader Remastered - Settings")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.resizable(False, False)
        
        self.iconbitmap(ResourceObtainerInstance.GetResource("logo.ico"))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.Button1 = customtkinter.CTkButton(self, width=199, height=30, text='Apply Settings', command=self.ApplySettings)
        self.Button1.place(x=133, y=310)

        self.OptionMenu1 = customtkinter.CTkOptionMenu(self, values=["Blue Theme", "Dark Blue Theme", "Green Theme"], height=30)
        self.OptionMenu1.place(x=0, y=193)

        self.Switch1 = customtkinter.CTkSwitch(self, text='Use Proxy')
        self.Switch1.place(x=500, y=138)

        self.Switch2 = customtkinter.CTkSwitch(self, text='SFX')
        self.Switch2.place(x=500, y=81)

        self.Switch3 = customtkinter.CTkSwitch(self, text='Use Cookie')
        self.Switch3.place(x=494, y=195)

        self.Button2 = customtkinter.CTkButton(
            self, command=self.SetCustomOutputPath, width=141, text='Set Custom Output Path', bg_color=[
                'gray86', 'gray17'])
        self.Button2.place(x=0, y=73)

        self.Label1 = customtkinter.CTkLabel(self, width=600, height=50, text='FFmpeg: Not Installed!')
        self.Label1.place(x=0, y=0)

        self.Button3 = customtkinter.CTkButton(self, width=141, text='Extract YouTube Cookie', command=self.ImportYouTubeCookie)
        self.Button3.place(x=0, y=113)

        self.Button4 = customtkinter.CTkButton(self, text='Install FFmpeg', command=self.install_ffmpeg)
        self.Button4.place(x=0, y=150)

        self.Label2 = customtkinter.CTkLabel(self, text=f'PyYtDownloader Remastered - Version: {VERSION}')
        self.Label2.place(x=350, y=322)

        self.Label3 = customtkinter.CTkLabel(self, text="Output\Path\Placeholder")
        self.Label3.place(x=164, y=73)

        App.LoadAppConfigValuesIntoView(self)

        self.bind_all("<Any-ButtonPress>", self.saved_switch)

    def saved_switch(*args):
        global INTERACTED_WITH_SETTINGSWINDOW
        INTERACTED_WITH_SETTINGSWINDOW = True


    def on_closing(self):
        global INTERACTED_WITH_SETTINGSWINDOW
        if INTERACTED_WITH_SETTINGSWINDOW:
            reply = PopupView.question_box("Unsaved Changes", f'You have Unsaved Changes. Would you like to save them before closing?')
            if reply == "yes":
                self.ApplySettings()
            elif reply == "no":
                pass
        self.destroy()
        self.quit()

    def LoadAppConfigValuesIntoView(self):
        CustomOutputPath = config.GetConfigKeyValue("CustomOutputPath")
        ColorTheme = config.GetConfigKeyValue("ColorTheme")
        UseSFX = config.GetConfigKeyValue("UseSFX")
        UseProxy = config.GetConfigKeyValue("UseProxy")
        UseCookie = config.GetConfigKeyValue("UseCookie")

        self.Label3.configure(text=CustomOutputPath)
        if ColorTheme == "BlueTheme":
            customtkinter.set_default_color_theme("blue")
            self.OptionMenu1.set("Blue Theme")
        elif ColorTheme == "GreenTheme":
            customtkinter.set_default_color_theme("green")
            self.OptionMenu1.set("Green Theme")
        elif ColorTheme == "DarkBlueTheme":
            customtkinter.set_default_color_theme("dark-blue")
            self.OptionMenu1.set("Dark Blue Theme")

        if UseSFX == "True":
            self.Switch2.select()
        else:
            self.Switch2.deselect()
        
        if UseProxy == "True":
            self.Switch1.select()
        else:
            self.Switch1.deselect()
        
        if UseCookie == "False":
            self.Switch3.deselect()
        else:
            self.Switch3.select()

        if FFMpegInstaller.CheckIfFFmpegIsInstalled('SystemData') == True:
            self.Label1.configure(text="FFmpeg: Installed!")
        else:
            self.Label1.configure(text="FFmpeg: Not Installed!")


    def SetCustomOutputPath(self):
        filepath = filedialog.askdirectory()
        config.SetAppConfigValue("CustomOutputPath", filepath)
        config.WriteAppConfig()
        PopupView.show_info_box("Set Custom Output Path", f"Successfully set your new Output Path to {filepath}")

        self.LoadAppConfigValuesIntoView()

    def ImportYouTubeCookie(self):
        try:
            default_browser = MiscUtils.get_default_browser_windows()
            if default_browser == False:
                logging.warn(f'Unable to Identify your default Browser.')
                PopupView.show_error_box(f'Load YouTube Cookie', f'Unable to Identify your default Browser. Please try again with Mozilla Firefox set as your Windows default Browser.')
                return
            else:
                logging.info(f'Default Browser Identified: {default_browser}')

            cookie = yt_dlp.cookies.extract_cookies_from_browser(default_browser)
            cookie.save(f'{os.getcwd()}\\SystemData\\youtube_cookie.txt')

            with open(f'{os.getcwd()}\\SystemData\\youtube_cookie.txt', 'r') as f:
                data = f.read()

            config.SetAppConfigValue("YouTubeCookiePath", f'{os.getcwd()}\\SystemData\\youtube_cookie.txt')
            config.WriteAppConfig()
            PopupView.show_info_box("Load YouTube Cookie", f"Your Cookie File has been Extracted out of your Default Browser successfully. It has been encrypted and stored in your SystemData folder.")
        except Exception as e:
            logging.error(f'Unable to Load YouTube Cookie: {e}')
            PopupView.show_error_box("Load YouTube Cookie", f"Unable to Load YouTube Cookie (an Exception occoured): {e}")

    def ChangeSettingsWindowLabel(self, text: str):
        """Changes the SettingsWindowLabel (ffmpeg status label)
        
        Args:
            - text (str): The Text you want to display."""
        
        self.Label1.configure(text=text)
        self.update()


    def install_ffmpeg(self):
        if FFMpegInstaller.CheckIfFFmpegIsInstalled('SystemData') == False:
            try:
                PopupView.show_info_box("Install FFmpeg", f'Downloading FFmpeg might take a while. Your Antivirus might cause trouble because you are trying to download three .exe Files.')
                self.Label1.configure(text=f'FFmpeg: Installing FFmpeg, please wait...')
                self.update()
                t1 = threading.Thread(target=FFMpegInstaller.install_ffmpeg, args=["SystemData", self.ChangeSettingsWindowLabel]).start()
                self.LoadAppConfigValuesIntoView()
            except Exception as e:
                PopupView.show_error_box(f'Install FFmpeg', f'An Exception occoured: {e}')
        else:
            reply = PopupView.question_box("Install FFmpeg", f'You already have FFmpeg Installed. Do you want to delete FFmpeg so you can reinstall it?')
            if reply == "yes":
                PopupView.show_info_box("Install FFmpeg", f'Downloading FFmpeg might take a while. Your Antivirus might cause trouble because you are trying to download three .exe Files.')
                self.Label1.configure(text=f'FFmpeg: Installing FFmpeg, please wait...')
                self.update()
                FFMpegInstaller.install_ffmpeg('SystemData')
                PopupView.show_info_box("Install FFmpeg", f'Successfully Installed ffplay.exe, ffmpeg.exe & ffprobe.exe into your SystemData Directory.')
                self.LoadAppConfigValuesIntoView()
            elif reply == "no":
                PopupView.show_warning_box(f'Install FFmpeg', f'Aborted Operation.')

    def ApplySettings(self):
        global INTERACTED_WITH_SETTINGSWINDOW

        ThemeNameToThemeName = {
            "Blue Theme" : "BlueTheme",
            "Green Theme" : "GreenTheme",
            "Dark Blue Theme" : "DarkBlueTheme"
        }

        use_sfx = "True" if self.Switch2.get() == 1 else "False"
        use_proxy = "True" if self.Switch1.get() == 1 else "False"
        use_cookie = "True" if self.Switch3.get() == 1 else "False"

        config.SetAppConfigValue("UseSFX", use_sfx)
        config.SetAppConfigValue("UseProxy", use_proxy)
        config.SetAppConfigValue("UseCookie", use_cookie)
        config.SetAppConfigValue("ColorTheme", ThemeNameToThemeName[self.OptionMenu1.get()])
        config.WriteAppConfig()

        PopupView.show_info_box("Apply Settings", f'Your Settings have been written to the app.config successfully.\n\nIf you changed your Color Theme, this effect will be visible after a restart. Other settings should have taken effect immideatly.')

        INTERACTED_WITH_SETTINGSWINDOW = False



if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        program_directory = os.path.dirname(os.path.abspath(sys.executable))
    else:
        program_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(program_directory)
    app = App()
    app.mainloop()
