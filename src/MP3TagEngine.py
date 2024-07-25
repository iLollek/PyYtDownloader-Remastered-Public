# The MP3 Tag Engine is responsible for attaching MP3 File Tags like Artist or Song Name onto a MP3 File.

import eyed3 # You don't have to use eyed3 if you think another library fits more
import os
import logging

class MP3TagEngine:
    """
    The MP3TagEngine class is responsible for attaching MP3 file tags like 
    Artist or Song Name onto an MP3 file.

    Attributes:
        audiofile (eyed3.core.AudioFile): The loaded MP3 file.
    """

    def __init__(self, filepath: str):
        """
        Initializes the MP3TagEngine with the given file path.

        Args:
            filepath (str): The path to the MP3 file.

        Logs an error if the file does not exist or cannot be loaded.
        """
        if not os.path.isfile(filepath):
            logging.error(f"File {filepath} does not exist.")
            self.audiofile = None
        else:
            self.audiofile = eyed3.load(filepath)
            if self.audiofile is None:
                logging.error(f"Failed to load file {filepath}.")
            else:
                logging.info(f"Loaded file {filepath} successfully.")

    def add_artist_name(self, artist: str):
        """
        Adds the artist name tag to the MP3 file.

        Args:
            artist (str): The artist name to add.
        """
        if self.audiofile:
            self.audiofile.tag.artist = artist
            self.audiofile.tag.save()
            logging.info(f"Artist name '{artist}' added successfully.")
    
    def add_album_name(self, album: str):
        """
        Adds the album name tag to the MP3 file.

        Args:
            album (str): The album name to add.
        """
        if self.audiofile:
            self.audiofile.tag.album = album
            self.audiofile.tag.save()
            logging.info(f"Album name '{album}' added successfully.")
    
    def add_album_artist(self, album_artist: str):
        """
        Adds the album artist tag to the MP3 file.

        Args:
            album_artist (str): The album artist name to add.
        """
        if self.audiofile:
            self.audiofile.tag.album_artist = album_artist
            self.audiofile.tag.save()
            logging.info(f"Album artist '{album_artist}' added successfully.")
    
    def add_song_title(self, title: str):
        """
        Adds the song title tag to the MP3 file.

        Args:
            title (str): The song title to add.
        """
        if self.audiofile:
            self.audiofile.tag.title = title
            self.audiofile.tag.save()
            logging.info(f"Song title '{title}' added successfully.")
    
    def add_track_number(self, track_num: int, total_tracks: int = None):
        """
        Adds the track number tag to the MP3 file.

        Args:
            track_num (int): The track number.
            total_tracks (int, optional): The total number of tracks.
        """
        if self.audiofile:
            self.audiofile.tag.track_num = (track_num, total_tracks)
            self.audiofile.tag.save()
            logging.info(f"Track number '{track_num}' added successfully.")
    
    def add_genre(self, genre: str):
        """
        Adds the genre tag to the MP3 file.

        Args:
            genre (str): The genre to add.
        """
        if self.audiofile:
            self.audiofile.tag.genre = genre
            self.audiofile.tag.save()
            logging.info(f"Genre '{genre}' added successfully.")
    
    def add_release_year(self, year: int):
        """
        Adds the release year tag to the MP3 file.

        Args:
            year (int): The release year to add.
        """
        if self.audiofile:
            self.audiofile.tag.recording_date = eyed3.core.Date(year)
            self.audiofile.tag.save()
            logging.info(f"Release year '{year}' added successfully.")
    
    def add_comments(self, comments: str):
        """
        Adds comments to the MP3 file.

        Args:
            comments (str): The comments to add.
        """
        if self.audiofile:
            self.audiofile.tag.comments.set(comments)
            self.audiofile.tag.save()
            logging.info(f"Comments added successfully.")

    def add_lyrics(self, lyrics: str):
        """
        Adds lyrics to the MP3 file.

        Args:
            lyrics (str): The lyrics to add.
        """
        if self.audiofile:
            self.audiofile.tag.lyrics.set(lyrics)
            self.audiofile.tag.save()
            logging.info(f"Lyrics added successfully.")

# Example usage
if __name__ == "__main__":
    filepath = r"C:\Users\kwialre\Desktop\Initial D - Heartbeat [yESFRV-FKuI].mp3"
    mp3_engine = MP3TagEngine(filepath)
    mp3_engine.add_artist_name("Artist Name")
    mp3_engine.add_album_name("Album Name")
    mp3_engine.add_album_artist("Album Artist")
    mp3_engine.add_song_title("Song Title")
    mp3_engine.add_track_number(1, 10)
    mp3_engine.add_genre("Genre")
    mp3_engine.add_release_year(2023)
    mp3_engine.add_comments("These are comments.")
    mp3_engine.add_lyrics("These are the lyrics.")
