import requests
import logging

class LastFMTrackInfoEngine:
    """
    The LastFMTrackInfoEngine class is responsible for fetching track information 
    using the Last.fm API.

    Attributes:
        api_key (str): The Last.fm API key.
        track_name (str): The name of the track.
        artist_name (str): The name of the artist.
        track_info (dict): The detailed track information fetched from Last.fm.
    """

    BASE_URL = "http://ws.audioscrobbler.com/2.0/"

    def __init__(self, api_key: str, track_name: str, artist_name: str):
        """
        Initializes the LastFMTrackInfoEngine with the given API key, track name, 
        and artist name.

        Args:
            api_key (str): The Last.fm API key.
            track_name (str): The name of the track.
            artist_name (str): The name of the artist.
        """
        self.api_key = api_key
        self.track_name = track_name
        self.artist_name = artist_name
        self.track_info = None

        if self.is_api_key_valid():
            self.track_info = self.fetch_track_info()
        else:
            logging.error("Invalid API key provided. Track information will not be fetched.")

    def is_api_key_valid(self) -> bool:
        """
        Checks if the provided API key is valid by making a simple request 
        to the Last.fm API.

        Returns:
            bool: True if the API key is valid, False otherwise.
        """
        params = {
            "method": "track.getInfo",
            "api_key": self.api_key,
            "artist": "test",
            "track": "test",
            "format": "json"
        }
        response = requests.get(self.BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'error' in data and data['error'] == 10:  # Invalid API key error code
                logging.error("Invalid API key.")
                return False
            logging.info("API key is valid.")
            return True
        else:
            logging.error(f"Failed to validate API key: {response.status_code}")
            return False

    def fetch_track_info(self) -> dict:
        """
        Fetches track information from the Last.fm API.

        Returns:
            dict: The track information, or None if the track could not be determined.
        """
        params = {
            "method": "track.getInfo",
            "api_key": self.api_key,
            "artist": self.artist_name,
            "track": self.track_name,
            "format": "json"
        }
        response = requests.get(self.BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'track' in data:
                logging.info("Track information fetched successfully.")
                return data['track']
            else:
                logging.warning("Track information could not be determined.")
                return None
        else:
            logging.error(f"Failed to fetch track information: {response.status_code}")
            return None

    def get_track_name(self) -> str:
        """
        Returns the name of the track.

        Returns:
            str: The name of the track, or None if not available.
        """
        return self.track_info.get('name') if self.track_info else None

    def get_artist_name(self) -> str:
        """
        Returns the name of the artist.

        Returns:
            str: The name of the artist, or None if not available.
        """
        return self.track_info.get('artist', {}).get('name') if self.track_info else None

    def get_album_name(self) -> str:
        """
        Returns the name of the album.

        Returns:
            str: The name of the album, or None if not available.
        """
        return self.track_info.get('album', {}).get('title') if self.track_info else None

    def get_top_genre(self) -> str:
        """
        Returns the top genre (tag) associated with the track.

        Returns:
            str: The top genre (tag) for the track, or None if not available.
        """
        if not self.track_info:
            return None

        tags = self.track_info.get('toptags', {}).get('tag', [])
        if tags:
            top_tag = tags[0].get('name')
            return top_tag
        return None

    def get_track_duration(self) -> int:
        """
        Returns the duration of the track in seconds.

        Returns:
            int: The duration of the track in seconds, or None if not available.
        """
        duration_str = self.track_info.get('duration') if self.track_info else None
        return int(duration_str) // 1000 if duration_str else None

    def get_track_url(self) -> str:
        """
        Returns the URL of the track.

        Returns:
            str: The URL of the track, or None if not available.
        """
        return self.track_info.get('url') if self.track_info else None

    def get_playcount(self) -> int:
        """
        Returns the play count of the track.

        Returns:
            int: The play count of the track, or None if not available.
        """
        playcount_str = self.track_info.get('playcount') if self.track_info else None
        return int(playcount_str) if playcount_str else None

    def get_listeners(self) -> int:
        """
        Returns the number of listeners of the track.

        Returns:
            int: The number of listeners of the track, or None if not available.
        """
        listeners_str = self.track_info.get('listeners') if self.track_info else None
        return int(listeners_str) if listeners_str else None
# Example usage
if __name__ == "__main__":
    api_key = "YOUR_LAST_FM_API_KEY"
    track_name = "Shape of You"
    artist_name = "Ed Sheeran"
    track_info_engine = LastFMTrackInfoEngine(api_key, track_name, artist_name)

    print(f"Track Name: {track_info_engine.get_track_name()}")
    print(f"Artist Name: {track_info_engine.get_artist_name()}")
    print(f"Album Name: {track_info_engine.get_album_name()}")
    print(f"Track Duration: {track_info_engine.get_track_duration()} seconds")
    print(f"Track URL: {track_info_engine.get_track_url()}")
    print(f"Play Count: {track_info_engine.get_playcount()}")
    print(f"Listeners: {track_info_engine.get_listeners()}")
