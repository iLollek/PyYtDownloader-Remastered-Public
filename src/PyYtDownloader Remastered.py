import os
import sys
import threading
import logging
import customtkinter as ctk
import signal
import re
import yt_dlp
import time
import json
import webbrowser
import tkinter as tk

# PyYtDownloader-Remastered Imports
import GUI
import SplashLoadingScreen
import YouTubeEngine
from AppConfigReader import AppConfigReader
import MiscUtils
import PopupView
from Installer import MainInstallUtils, FFMpegInstaller
from MP3TagEngine import MP3TagEngine
from LastFMAPI import LastFMTrackInfoEngine

if getattr(sys, 'frozen', False):
    print(f'Running in Productive (PROD) Environment (.exe)')
    program_directory = os.path.dirname(os.path.abspath(sys.executable))
    ENV = "PROD"
    logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, force=True)
    if '_PYIBoot_SPLASH' in os.environ:
        import pyi_splash
        logging.info(f'Opened Splash Screen (PyInstaller)')
else:
    print(f'Running in Development (DEV) Environment (.py)')
    program_directory = os.path.dirname(os.path.abspath(__file__))
    ENV = "DEV"
    logging.basicConfig(stream=sys.stdout, format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, force=True)
os.chdir(program_directory)

VERSION = "1.3"
VideoInfoInstances = []
VideoDownloaderInstances = []
ResourceObtainerInstance = MiscUtils.ResourceObtainer()
postprocessing_finished_videos = []

def closing_protocol():
    """Closes PyYtDownloader-Remastered and executes some last saving lines of Code."""
    logging.info(f'Closing PyYtDownloader Remastered')
    os.kill(os.getpid(), signal.SIGTERM) # This is the last line that gets executed.

def clean_string(input_str):
    # Define a regular expression pattern to match ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    # Remove ANSI escape sequences from the input string
    cleaned_str = ansi_escape.sub('', input_str)
    
    return cleaned_str

def check_first_time_run():
    logging.info(f'Checking if PyYtDownloader-Remastered is being run for the first Time...')
    if MainInstallUtils.CheckIfFirstTimeRun(program_directory) == True:
        logging.warn(f'PyYtDownloader-Remastered is probably being run for the first time!')
        PopupView.show_info_box(f'PyYtDownloader-Remastered: First time run', f'Thank you for Downloading PyYtDownloader-Remastered!\n\nAll needed System-Files will now be created automatically. If you want to download .mp3 (Audio Files) from YouTube, you need to install FFmpeg. You can do that in the Settings.\n\nIf you are not running PyYtDownloader-Remastered for the first Time and you see this Window, you might have deleted the SystemData Folder or the app.config File.')
        logging.info(f'Creating System Data Folder...')
        MainInstallUtils.CreateSystemDataFolder(program_directory)
        logging.info(f'Creating app.config File...')
        MainInstallUtils.CreateAppConfigFile(program_directory)
        logging.info(f'Creating Desktop Shortcut...')
        MainInstallUtils.CreateDesktopShortcut(program_directory)
        logging.info(f'Installed Successfully.')
        PopupView.show_info_box(f'Installation Successful!', f'PyYtDownloader-Remastered has installed successfully. Please restart the Program.\n\nPyYtDownloader-Remastered is Software made by iLollek')
        closing_protocol()
    else:
        logging.info(f'PyYtDownloader-Remastered is not run for the first time.')
check_first_time_run()  

def get_app_config():
    logging.info(f'Retrieving config Instance...')
    global config
    config = AppConfigReader("app.config")
    logging.info(f'Checking Integrity...')
    config.ReadAppConfig()
    if config.VerifyIntegrity() == True:
        logging.info(f'Read app.config successfully!')
    else:
        logging.error(f'Unable to verify Integrity of app.config File!')
        PopupView.show_error_box("Fatal Error: app.config", f'Unable to verify the Integrity of your app.config File. PyYtDownloader-Remastered is unable to run without a valid and verified app.config File. Please attempt to fix the app.config File or delete it.')
        os.startfile(program_directory)
        closing_protocol()
get_app_config()

def run_gui():
    logging.info("Main Window Opened.")
    global root
    global app
    root = ctk.CTk()
    app = GUI.App(root, download_button_function, extended_video_info_callback, GUI.GetAndChangeColorTheme(config))
    root.mainloop()
    logging.info("Main Window Closed.")
    closing_protocol()

def TestProxy():
    if config.GetConfigKeyValue("UseProxy") != "False":
        if config.GetConfigKeyValue("ProxyUseCredentials") == "True":
            proxy = f'socks5://{config.GetConfigKeyValue("ProxyCredentialsUser")}:{config.GetConfigKeyValue("ProxyCredentialsPassword")}@{config.GetConfigKeyValue("ProxyHost")}:{config.GetConfigKeyValue("ProxyPort")}'
        else:
            proxy = f"socks5://{config.GetConfigKeyValue('ProxyHost')}:{config.GetConfigKeyValue('ProxyPort')}"

        result = MiscUtils.test_proxy(proxy)

    if result:
        latency = result[1]
        if latency > 800:
            PopupView.show_warning_box(f'Proxy Slow', f'The Proxy you are using has a Ping of {latency}ms, so your downloads might be slow. Consider using a different Proxy if possible.\n\nYour Proxy was able to connect to www.google.com, however this does not mean that you will be able to download a YouTube Video.')
        else:
            PopupView.show_info_box(f'Proxy Info', f'The Proxy you are using was able to connect to www.google.com successfully with a Ping of {latency}ms.\n\nThis does not mean that you will be able to download a YouTube Video.')
    else:
        PopupView.show_error_box(f'Proxy Error', f'The Proxy you are using was unable to connect to www.google.com! Please change your Proxy inside of the app.config File and restart PyYtDownloader-Remastered.')
        closing_protocol()

def TestLastFMAPIKey():
    logging.info(f'Testing LastFM API Key...')
    if config.GetConfigKeyValue("LastFMAPIKey") != "None":
        lastfmengine = LastFMTrackInfoEngine(config.GetConfigKeyValue("LastFMAPIKey"), "Yandere Complex", "Sewerslvt")
        if lastfmengine.is_api_key_valid() == False:
            logging.warn(f'Unable to send API Request with the provided LastFM API Key! ({config.GetConfigKeyValue("LastFMAPIKey")})')
            PopupView.show_error_box(f'LastFM API Error', f'Your LastFM API Key in the app.config File does not work - PyYtDownloader-Remastered is unable to send a API-Request to the LastFM API. Please check if the Key you provided ({config.GetConfigKeyValue("LastFMAPIKey")}) is correct.')
            closing_protocol()
    else:
        logging.warn(f'LastFM API Key is None')
        PopupView.show_error_box("LastFM API Error", "Your LastFM API Key in the app.config File is not set. To use the extended MP3TagEngine via the LastFM API, you need a LastFM API Key that is also set in the app.config File. A Tab in your Webbrowser to the according Website will open upon closing this Popup.")
        webbrowser.open("https://www.last.fm/api/accounts")
        closing_protocol()

def Startup():
    splash_screen_app.ChangeModule("Initializing...")
    
    splash_screen_app.ChangeModule("Checking Version...")
    if MiscUtils.VersioningSystem.CompareVersion(VERSION) == True:
        splash_screen_app.update()
        visit_website = PopupView.question_box(f'Update available!', f'A new PyYtDownloader-Remastered Version is available for Downloading!\n\nYour Version: {VERSION}\nAvailable Version: {MiscUtils.VersioningSystem.GetVersionFromServer()}\n\nWould you like to visit the Download Page?')
        if visit_website == "yes":
            webbrowser.open(f'https://ilollek.net/pyd-rem/download.html')

    if config.GetConfigKeyValue('UseProxy') != "False":
        splash_screen_app.ChangeModule("Testing Proxy...")
        TestProxy()

    if config.GetConfigKeyValue("UseLastFMAPI") == "True":
        splash_screen_app.ChangeModule("Testing LastFM API Key...")
        TestLastFMAPIKey()
        logging.info(f'LastFM API Key valid!')

    splash_screen_app.destroy()

def run_splash_screen(startup_function_callback):
    logging.info("Splash Loading Screen Window Opened.")

    global splash_screen_app

    splash_screen_app = SplashLoadingScreen.SplashScreen(startup_function_callback)
    splash_screen_app.mainloop()

    logging.info("Splash Loading Screen Window Closed.")
#splash_screen_gui_thread = threading.Thread(target=run_splash_screen, args=[Startup]).start()
if ENV == "PROD":
    pyi_splash.close()
    logging.info(f'Closed Splash Screen (PyInstaller)')
run_splash_screen(Startup)

def search_for_videoinfoinstance_by_id(id: str) -> YouTubeEngine.VideoInfoFetcher:
    logging.info(f'Searching for Video ID {id} in {len(VideoInfoInstances)} VideoInfoInstances')
    
    matching_instances = filter(lambda x: x.GetVideoID() == id, VideoInfoInstances)
    
    matching_instance = next(matching_instances, None)
    
    if matching_instance:
        logging.info('Found VideoInfoInstance')
        return matching_instance
    else:
        logging.info('VideoInfoInstance not found, returning None')
        return None

def AddToLogBoxAndUpdate(content: str):
    app.userlogs.append(content)
    app.UpdateSideboxInformation()

def update_window_top_title_RAM():
    logging.info(f'Started Window RAM Updater Thread')
    while True:
        title = root.title().split(f' | ')[0]
        root.title(f'{title} | RAM: {round(MiscUtils.ResourceMonitor.RamUsedByProcess(os.getpid()))} MiB')
        root.update()
        time.sleep(1)


def extended_video_info_callback(video_id: str):

    VideoInfoInstance = search_for_videoinfoinstance_by_id(video_id)

    if VideoInfoInstance != None:

        InfoString = f'Extended Video Information for:\n{VideoInfoInstance.GetTitle()}\n\nUploaded by:\n{VideoInfoInstance.GetChannel()}\n\nViews:\n{VideoInfoInstance.GetViews()}\n\nComments:\n{VideoInfoInstance.GetCommentCount()}\n\nLikes:\n{VideoInfoInstance.GetLikes()}\n\nLength:\n{VideoInfoInstance.GetDurationString()} Minutes\n\nDescription:\n{VideoInfoInstance.GetDescription()}'
        
        app.ClearSidebox()

        app.InsertIntoSidebox(InfoString)

        root.update()

    else:
        app.ClearSidebox()

        root.update()

def add_mp3_tags(filepath, video_id):
    """Adds MP3 Tags using the MP3TagEngine"""
    # https://www.youtube.com/watch?v=XipL0Lbd9NY
    # https://youtu.be/oIYlSJPMQ38?si=yX-WW56pnf82w65b

    _, file_extention = os.path.splitext(filepath)
    filepath = filepath.replace(file_extention, ".mp3")

    video_info = search_for_videoinfoinstance_by_id(video_id)

    logging.info(f'Adding MP3 Tags: {filepath}')
    mp3engine = MP3TagEngine(filepath)
    if config.GetConfigKeyValue("UseLastFMAPI") == "True":
        logging.info("Using Extended MP3TagEngine (LastFMTrackInfoEngine / Online Mode / API Mode)")
        if config.GetConfigKeyValue("LastFMAPIKey") != "None":
            logging.info(f'Fetching Track Information by sending API Request to LastFM...')
            lastfmengine = LastFMTrackInfoEngine(config.GetConfigKeyValue("LastFMAPIKey"), video_info.GetTitle(), video_info.GetChannel())
            if lastfmengine.fetch_track_info() == None:
                logging.warn(f'Unable to find a hit using LastFM API for: {video_info.GetTitle()}')
                AddToLogBoxAndUpdate(f'Unable to add Tags via LastFM for {video_info.GetTitle()}')
            else:
                logging.info(f'LastFM API Hit for: {video_info.GetTitle()}')
                mp3engine.add_song_title(lastfmengine.get_track_name())
                mp3engine.add_artist_name(lastfmengine.get_artist_name())
                mp3engine.add_album_name(lastfmengine.get_album_name())
                mp3engine.add_genre(lastfmengine.get_top_genre())
                AddToLogBoxAndUpdate(f'Added MP3 Tags (using API Mode) to {video_info.GetTitle()}')
        else:
            PopupView.show_error_box("LastFM API Error", "Your LastFM API Key in the app.config File is not set. To use the extended MP3TagEngine via the LastFM API, you need a LastFM API Key that is also set in the app.config File. A Tab in your Webbrowser to the according Website will open upon closing this Popup.")
            webbrowser.open("https://www.last.fm/api/accounts")
    else:
        logging.info(f'Using Basic MP3TagEngine (Offline Mode / No API Mode)')
        mp3engine.add_artist_name(video_info.GetChannel())
        mp3engine.add_song_title(video_info.GetTitle())
        logging.info(f'Added Tags Successfully.')
        AddToLogBoxAndUpdate(f"Added MP3 Tags (using No API Mode) to {video_info.GetTitle()}")



def download_progress_callback(downloadinformation: dict):

    VideoInfoInstance = search_for_videoinfoinstance_by_id(downloadinformation["id"])

    if app.CheckIfVideoIDInTable(VideoInfoInstance.GetVideoID()) == True:
        app.UpdateTableRowByID(VideoInfoInstance.GetChannel(), VideoInfoInstance.GetTitle(), clean_string(downloadinformation["download_speed"]), clean_string(downloadinformation["time_spent"]), clean_string(downloadinformation["percent"]), f'{clean_string(downloadinformation["downloaded_bytes"])} / {clean_string(downloadinformation["total_bytes"])}', downloadinformation["status"], downloadinformation["id"])
    else:
        app.InsertIntoMainbox(VideoInfoInstance.GetChannel(), VideoInfoInstance.GetTitle(), clean_string(downloadinformation["download_speed"]), clean_string(downloadinformation["time_spent"]), clean_string(downloadinformation["percent"]), f'{clean_string(downloadinformation["downloaded_bytes"])} / {clean_string(downloadinformation["total_bytes"])}', downloadinformation["status"], downloadinformation["id"])

    if downloadinformation["status"] == "finished":
        if config.GetConfigKeyValue('UseSFX') == True or config.GetConfigKeyValue('UseSFX') == "True":
            MiscUtils.SoundModule.PlaySound(ResourceObtainerInstance.GetResource(f'DownloadComplete.mp3'))

    root.update()

def postprocessing_progress_callback(arg):

    downloadinformation = app.GetVideoInformationByID(arg["info_dict"]["id"])

    if app.CheckIfVideoIDInTable(downloadinformation["id"]) == True:
        app.UpdateTableRowByID(downloadinformation["channel"], downloadinformation["title"], downloadinformation["download_speed"], downloadinformation["time_spent"], downloadinformation["percent"], downloadinformation["bytes"], f'Post-Processing: {arg["status"]}', downloadinformation["id"])
    else:
        AddToLogBoxAndUpdate(f'Started Post-Processing: {downloadinformation["title"]}')
        app.InsertIntoMainbox(downloadinformation["channel"], downloadinformation["title"], downloadinformation["download_speed"], downloadinformation["time_spent"], downloadinformation["percent"], downloadinformation["bytes"], f'Post-Processing: {arg["status"]}', downloadinformation["id"])

    if arg["status"] == "finished" and arg["info_dict"]["id"] not in postprocessing_finished_videos and downloadinformation["status"] == "Post-Processing: finished":
        postprocessing_finished_videos.append(arg["info_dict"]["id"])
        AddToLogBoxAndUpdate(f'Finished Post-Processing: {downloadinformation["title"]}')

        if config.GetConfigKeyValue("UseMP3Tags") == True or config.GetConfigKeyValue("UseMP3Tags") == "True":
            add_mp3_tags(arg["info_dict"]["_filename"], arg["info_dict"]["id"])

        if config.GetConfigKeyValue('UseSFX') == True or config.GetConfigKeyValue('UseSFX') == "True":
            MiscUtils.SoundModule.PlaySound(ResourceObtainerInstance.GetResource(f'PostProcessingComplete.mp3'))

    root.update()
    

def download_button_function():
    logging.info(f'Download Button has been Pressed')
    AddToLogBoxAndUpdate(f'Preparing Download...')
    videolink = app.GetEntryContent()
    link_type = YouTubeEngine.CheckIfVideo(videolink)
    logging.info(f'Videolink: {videolink} - Type: {link_type}')
    AddToLogBoxAndUpdate(f'Link-Type: {link_type}')
    format = app.GetVideoOrAudio()

    if format == "mp3" and FFMpegInstaller.CheckIfFFmpegIsInstalled("SystemData") == False:
        PopupView.show_warning_box(f'FFmpeg not Installed!', f'You are trying to Download Audio only (.mp3) while not having FFmpeg Installed. You can still only Download Audio, however it will be in the .webm Format (or similar), or you might be unable to and the Program will cause an Exception. Please Install FFmpeg via the Settings Menu.')

    app.ClearEntry()

    if link_type == "Video":
        try:
            AddToLogBoxAndUpdate(f'Fetching Video Information...')
            root.update()
            VideoInfoInstance = YouTubeEngine.VideoInfoFetcher(videolink, config)
            VideoDownloaderInstance = YouTubeEngine.YouTubeVideoDownloader(videolink, format, download_progress_callback, postprocessing_progress_callback, config)

            VideoInfoInstances.append(VideoInfoInstance)
            VideoDownloaderInstances.append(VideoDownloaderInstance)

            downloader_thread = threading.Thread(target=VideoDownloaderInstance.DownloadVideo).start()

            logging.info(f'Started Downloader Thread for: {VideoInfoInstance.GetTitle()}')
            AddToLogBoxAndUpdate(f'Starting Downloader Thread for: {VideoInfoInstance.GetTitle()}')
        except yt_dlp.utils.DownloadError as e:
            logging.error(f'yt_dlp DownloadError: {e}')
            PopupView.show_error_box(f'yt_dlp DownloadError!', f'A yt_dlp DownloadError occoured: {e}\n\nPyYtDownloader Remastered will now close.')
            closing_protocol()
    elif link_type == "Playlist":

        root.update()

        PlaylistInstance = YouTubeEngine.PlaylistManager(videolink, config)
        videos_in_playlist = PlaylistInstance.GetAmountOfVideos()
        videos_download_link = PlaylistInstance.GetVideoLinkList()

        counter = 0

        for video_link in videos_download_link:
            VideoInfoInstance = YouTubeEngine.VideoInfoFetcher(video_link, config)
            VideoDownloaderInstance = YouTubeEngine.YouTubeVideoDownloader(video_link, format, download_progress_callback, postprocessing_progress_callback, config)

            VideoInfoInstances.append(VideoInfoInstance)
            VideoDownloaderInstances.append(VideoDownloaderInstance)


            # You could run this in paralell if you want but it just bugs out everything. 
            # I personally believe that it's good enough if you can already download videos in parallel.
            downloader_thread = threading.Thread(target=VideoDownloaderInstance.DownloadVideo()).start()

            logging.info(f'Finished Downloading: {VideoInfoInstance.GetTitle()}')
            AddToLogBoxAndUpdate(f'Finished Downloading: {VideoInfoInstance.GetTitle()}')

            counter += 1

            root.update()

        root.update()
    elif link_type == "None":
        PopupView.show_warning_box(f'Not a YouTube-Link!', f'The Link you provided ({videolink}) is not a Link to a valid YouTube-Video.')

gui_thread = threading.Thread(target=run_gui).start()

tick_counter = 0

while True:
    if 'root' in globals():
        logging.info(f'Main GUI is now reachable inside Main Script (root). Ticks needed: {tick_counter}')
        root.title(f'PyYtDownloader Remastered ')
        RAMUpdaterThread = threading.Thread(target=update_window_top_title_RAM).start()
        root.update()
        AddToLogBoxAndUpdate(f'GUI Started. Ticks: {tick_counter}')
        break
    else:
        tick_counter += 1