from yt_dlp import YoutubeDL
from AppConfigReader import AppConfigReader
import os
from hurry.filesize import filesize
import logging
import PopupView
import yt_dlp


URL = "https://www.youtube.com/watch?v=jS8tpzzaqXM" # Sewerslvt Yandere Complex
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLb_hRe2_K8d3-_IfRosHQetELEJwT9UaC" # State of Anarchy Lobby Music (Playlist)
LIKES_DISABLED_URL = "https://www.youtube.com/watch?v=ucUZA26Za3I" # Some weird indian youtube video i found...
COMMENTS_DISABLED_URL = "https://youtu.be/0BNsnWppO0k?si=Yz5qj_uRLC15vNCU" # Sewerslvt - inpeace

def CheckIfVideo(video_url: str) -> str:
    """Checks if the Link is a valid YouTube Video, and not a Playlist Link or to another platform.
    
    Args:
        - video_url (str): The URL of the Video

    Returns:
        - Is Video (str): "Video" if Video, "Playlist" if Playlist, "None" (as a string) if not a YouTube Link."""
    if "list" in video_url:
        return "Playlist"
    elif "youtu.be" in video_url or "youtube.com" in video_url:
        return "Video"
    else:
        return "None"

class VideoInfoFetcher():
    """Used to fetch Different Information about the YouTube Video. Only Supports Link to a single YouTube Video."""

    def __init__(self, YouTubeVideoLink: str, config: AppConfigReader):
        self.YouTubeVideoLink = YouTubeVideoLink
        self.config = config
        if config.GetConfigKeyValue("UseProxy") != "False":
            if config.GetConfigKeyValue("ProxyUseCredentials") == "True":
                proxy = f"socks5://{config.GetConfigKeyValue('ProxyCredentialsUser')}:{config.GetConfigKeyValue('ProxyCredentialsPassword')}@{config.GetConfigKeyValue('ProxyHost')}:{config.GetConfigKeyValue('ProxyPort')}"
            else:
                proxy = f"socks5://{config.GetConfigKeyValue('ProxyHost')}:{config.GetConfigKeyValue('ProxyPort')}"
            self.ydl_opts = {"quiet": True, "include_ads": False, "proxy": proxy}
        else:
            self.ydl_opts = {"quiet": True, "include_ads": False}
        if config.GetConfigKeyValue("UseCookie") != "False":
            logging.info("Fetching Cookie File...")
            self.ydl_opts["cookiefile"] = config.GetConfigKeyValue("YouTubeCookiePath")
        with YoutubeDL(self.ydl_opts) as ydl:
            self.infodict = ydl.extract_info(self.YouTubeVideoLink, download=False)
        
    def GetTitle(self) -> str:
        """Gets the Title of the YouTube Video.
        
        Returns:
            - Title (str): The Title of the YouTube Video."""
        
        return self.infodict["title"]
    
    def GetLikes(self) -> str:
        """Gets the Amount of Likes on the YouTube Video. Converted to String by default. If Likes are Disabled, it will return "Likes Disabled".
        
        Returns:
            - Likes (str): The Amount of Likes of the YouTube Video."""

        return str(self.infodict["like_count"]) if self.infodict["like_count"] != None else "Likes Disabled"
    
    def GetChannel(self) -> str:
        """Gets the Name of the Channel that uploaded the YouTube Video.
        
        Returns:
            - Channel (str): The Name of the YouTube Channel."""
        
        return self.infodict["channel"]
    
    def GetDescription(self) -> str:
        """Gets the Description of the YouTube Video.
        
        Returns:
            - Description (str): The Description of the YouTube Video."""
        
        return str(self.infodict["description"])
    
    def GetThumbnailLink(self) -> str:
        """Gets the Link to the Thumbnail of the YouTube Video.
        
        Returns:
            - Thumbnail Link (str): The Link to the Thumbnail"""
        
        return str(self.infodict["thumbnail"])
    
    def GetDurationString(self) -> str:
        """Gets the Duration String of the YouTube Video.
        
        Returns:
            - Duration String (str): A Duration String. Example: 4:20"""
        
        return str(self.infodict["duration_string"])
    
    def GetViews(self) -> str:
        """Gets the Amount of Views of the YouTube Video
        
        Returns:
            - Views (str): The Amount of Views."""
        
        return str(self.infodict["view_count"])
    
    def GetCommentCount(self) -> str:
        """Gets the Amount of Comments of the YouTube Video. If Comments are Disabled, it will return "Comments Disabled"
        
        Returns:
            - Comment Count (str): The Amount of Comments"""
        
        return str(self.infodict["comment_count"]) if self.infodict["comment_count"] != None else "Comments Disabled"
    
    def GetVideoID(self) -> str:
        """Gets the Video ID.
        
        Returns:
            - Video ID (str): The YouTube-Video ID"""
        
        return str(self.infodict["id"])
    
class YouTubeVideoDownloader():

    def __init__(self, YouTubeVideoLink: str, format: str, callback_into_main_script, postprocessor_callback, config: AppConfigReader):


        config.ReadAppConfig()

        self.YouTubeVideoLink = YouTubeVideoLink
        self.format = format
        self.callback_into_main_script = callback_into_main_script
        self.config = config
        self.postprocessor_callback = postprocessor_callback
        self.output_dir = config.GetConfigKeyValue("CustomOutputPath")
        self.system_data_dir = os.path.join(os.getcwd(), "SystemData")
        self.ydl_opts = {"quiet": True, "include_ads": False, 'progress_hooks': [self.ProgressHook], 'paths': {"home" : f'{config.GetConfigKeyValue("CustomOutputPath")}'}}
        if self.format == "mp3":
            self.ydl_opts["postprocessor_hooks"] = [self.postprocessor_callback]
            self.ydl_opts["format"] = "mp3/bestaudio/best"
            self.ydl_opts["audio_format"] = "mp3"
            self.ydl_opts["ffmpeg_location"] = f"SystemData\\ffmpeg.exe"
            self.ydl_opts["postprocessors"] = [{
                'key' : 'FFmpegExtractAudio',
                'preferredcodec' : 'mp3'
            }]
        elif self.format == "mp4":
            self.ydl_opts["format"] = "mp4"
        if config.GetConfigKeyValue("UseProxy") != "False":
            if config.GetConfigKeyValue("ProxyUseCredentials") == "True":
                proxy = f"socks5://{config.GetConfigKeyValue('ProxyCredentialsUser')}:{config.GetConfigKeyValue('ProxyCredentialsPassword')}@{config.GetConfigKeyValue('ProxyHost')}:{config.GetConfigKeyValue('ProxyPort')}"
            else:
                proxy = f"socks5://{config.GetConfigKeyValue('ProxyHost')}:{config.GetConfigKeyValue('ProxyPort')}"
            self.ydl_opts["proxy"] = proxy
        if config.GetConfigKeyValue("UseCookie") != "False":
            logging.info("Fetching Cookie File...")
            self.ydl_opts["cookiefile"] = config.GetConfigKeyValue("YouTubeCookiePath")
        
    def show_formats(self):
        """Used for debugging. Shows the available Formats."""
        with YoutubeDL(self.ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.YouTubeVideoLink, download=False)
            formats = info_dict.get('formats', [])
            print("Available formats:")
            for f in formats:
                print(f"{f['format_id']} - {f['format']} - {f['ext']}")

    def ProgressHook(self, info_dict: dict):
        """The yt_dlp Progress Hook. Uses a Callback to return the progress_information back into the Main Script."""
        print(f'Progress Hook got Called.')

        progress_information = {}
        progress_information["status"] = info_dict["status"]
        progress_information["downloaded_bytes"] = filesize.size(info_dict.get("downloaded_bytes", 0)) + "B"
        progress_information["total_bytes"] = filesize.size(info_dict["total_bytes"]) + "B"
        progress_information["filename"] = info_dict["filename"]
        progress_information["default_template"] = info_dict["_default_template"]
        progress_information["download_speed"] = str(info_dict["_speed_str"]).replace(' ', '')
        progress_information["percent"] = str(info_dict["_percent_str"]).replace(' ', '')
        progress_information["time_spent"] = str(info_dict["_elapsed_str"]).replace(' ', '')
        progress_information["id"] = str(info_dict["info_dict"]["id"])

        if self.callback_into_main_script:
            self.callback_into_main_script(progress_information)

    def DownloadVideo(self):
        """Downloads the Video and starts the Process. Please use with Threading!"""
        try:
            logging.info(f'Attempting to Download {self.YouTubeVideoLink}')
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(self.YouTubeVideoLink)
            logging.info(f'Download of {self.YouTubeVideoLink} successful.')
        except yt_dlp.utils.DownloadError as e:
            logging.error(f'yt_dlp Error occoured while trying to download Video {self.YouTubeVideoLink}: {e}')
            PopupView.show_error_box(f'yt_dlp DownloadError', f'While trying to Download the Video {self.YouTubeVideoLink} a yt_dlp DownloadError occoured: {e}\n\nPyYtDownloader-Remastered will continue, although it is recommended you restart the Program.')
        except Exception as e:
            logging.error(f'An Exception occoured while Downloading Video {self.YouTubeVideoLink}: {e}')

class PlaylistManager():

    def __init__(self, YouTubePlaylistLink: str, config: AppConfigReader):
        self.YouTubePlaylistLink = YouTubePlaylistLink
        self.config = config
        if config.GetConfigKeyValue("UseProxy") != "False":
            self.ydl_opts = {"quiet": True, "include_ads": False, "proxy": f"socks5://{config.GetConfigKeyValue('ProxyHost')}:{config.GetConfigKeyValue('ProxyPort')}"}
        else:
            self.ydl_opts = {"quiet": True, "include_ads": False}
        if config.GetConfigKeyValue("UseCookie") != "False":
            print("Creating cookie file (DOWNLOAD PLAYLIST)")
            self.ydl_opts["cookiefile"] = config.GetConfigKeyValue("YouTubeCookiePath")
        self.ydl_opts["ignoreerrors"] = True
        with YoutubeDL(self.ydl_opts) as ydl:
            self.infodict = ydl.extract_info(self.YouTubePlaylistLink, download=False)
        
    def GetChannel(self) -> str:
        """Gets the Name of the Channel that created the YouTube Playlist.
        
        Returns:
            - Channel (str): The Name of the YouTube Channel."""
        
        return self.infodict["channel"]
    
    def GetAmountOfVideos(self) -> str:
        """Gets the number of videos in the YouTube Playlist.
        
        Returns:
            - VideoCount (int): The number of videos in the playlist."""
        
        return str(len(self.infodict.get('entries', []))) if 'entries' in self.infodict else "0"

    def GetDescription(self) -> str:
        """Gets the Description of the YouTube Playlist.
        
        Returns:
            - Description (str): The Description of the YouTube Playlist."""
        
        return str(self.infodict["description"])
        
    def GetVideoLinkList(self) -> list[str]:
        """Gets all the YouTube-Video Links of the Playlist.
        
        Returns:
            - VideoLinkList (list[str]): A List containing Links to YouTube-Videos."""
        
        videos = []

        for video in self.infodict['entries']:
            try:
                videos.append(video["webpage_url"])
            except TypeError or KeyError as e:
                # The Video is unavailable (i.e. Private, Age-Restricted or whatever), so we can skip it since we can't get any info on it (and we can't download it anyways)
                pass

        return videos
        


        





if __name__ == "__main__":
    config = AppConfigReader("app.config")
    # VideoInfoObject = VideoInfoFetcher("https://youtu.be/qLwICn6g-No?si=lIYbKfauPLJBI3xS", config)
    # title = VideoInfoObject.GetTitle()
    # likes = VideoInfoObject.GetLikes()
    # channel = VideoInfoObject.GetChannel()
    # description = VideoInfoObject.GetDescription()
    # thumbnail_link = VideoInfoObject.GetThumbnailLink()
    # duration = VideoInfoObject.GetDurationString()
    # views = VideoInfoObject.GetViews()
    # comments = VideoInfoObject.GetCommentCount()
    # video_id = VideoInfoObject.GetVideoID()
    # print(f'Title: {title}')
    # print(f'Likes: {likes}')
    # print(f'Channel: {channel}')
    # print(f'Description: {description}')
    # print(f'Thumbnail Link: {thumbnail_link}')
    # print(f'Duration: {duration}')
    # print(f'Views: {views}')
    # print(f'Comment Count: {comments}')
    # print(f'Video ID: {video_id}')

    # YouTubeVideoDownloaderInstance = YouTubeVideoDownloader(URL, "mp3", None, config)
    # YouTubeVideoDownloaderInstance.show_formats()
    # YouTubeVideoDownloaderInstance.DownloadVideo()

    YouTubePlaylistObject = PlaylistManager("https://www.youtube.com/playlist?list=PLHCE3pRb5Sym57ZCByOeeUSObiSYkpZx5", config)
    print(YouTubePlaylistObject.GetChannel())
    print(YouTubePlaylistObject.GetAmountOfVideos())
    print(YouTubePlaylistObject.GetDescription())
    print(YouTubePlaylistObject.GetVideoLinkList())