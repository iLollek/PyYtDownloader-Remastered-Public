import subprocess
import os
import sys
import psutil
from playsound import playsound
import threading
import logging
import time
import socket
import socks
import urllib.request
import requests

def get_default_browser_windows():
    try:
        # Query the Windows Registry to find the default browser
        result = subprocess.check_output(
            r'reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice" /v ProgId',
            shell=True, stderr=subprocess.STDOUT
        ).decode()

        # Extract the ProgId from the command output
        prog_id = result.strip().split('    ')[-1]

        # Define a dictionary of known browser ProgIds or unique parts of them
        browsers = {
            'FirefoxURL': 'firefox',
            'ChromeHTML': 'chrome',
            'OperaStable': 'opera',
            'MSEdgeHTM': 'edge',
            'SafariHTML': 'safari'
        }

        # Check if any known browser identifier is part of the ProgId
        for key in browsers:
            if key in prog_id:
                return browsers[key]

        # If no known browser is found, return the ProgId for manual checking
        return False
    except subprocess.CalledProcessError as e:
        return f"Error fetching default browser: {e}"

def test_proxy(proxy):
    # Parse the proxy address and port
    proxy_address, proxy_port = proxy.split("://")[1].split(":")
    
    # Initialize a socket with SOCKS5 proxy
    socks.set_default_proxy(socks.SOCKS5, proxy_address, int(proxy_port))
    socket.socket = socks.socksocket
    
    # URL to test connection
    test_url = "https://ilollek.net"
    
    try:
        start_time = time.time()
        # Open a connection using the proxy
        response = urllib.request.urlopen(test_url)
        end_time = time.time()
        
        # Calculate latency in milliseconds
        latency_ms = round((end_time - start_time) * 1000)
        
        # Return True and latency if the connection was successful
        return True, latency_ms
        
    except Exception as e:
        # If connection failed, return False
        return False

class ResourceObtainer:

    def __init__(self):
        self.env = self.determine_prod_or_dev_env()
        if self.env == "DEV":
            self.basepath = self.development_resource_path() + "\\"
        elif self.env == "PROD":
            self.basepath = self.productive_resource_path() + "\\"

    def productive_resource_path(self):
        """ Gets the AppData Resource Path """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
            return base_path
        except Exception:
            base_path = os.path.abspath(".")
            return base_path

    def development_resource_path(self) -> str:
        """ Gets the Docs Resource Path """

        return os.path.dirname(os.getcwd()) + f"\\Docs"

    def determine_prod_or_dev_env(self) -> str:
        """Internal Function used to determine if the Script is running in a DEV or PROD Environment.
        
        Returns:
            - Environment (str): The Environment (PROD or DEV)"""
        if getattr(sys, 'frozen', False):
            return "PROD"
        else:
            return "DEV"

    def GetResource(self, filename: str) -> str:
        """Returns the path to the Resource based on the Environment.

        Args:
            - filename (str): The name of the File.
        
        Returns:
            - filepath (str): The Path to the Resource."""

        return self.basepath + filename
            
    
class ResourceMonitor:

    def RamUsedByProcess(pid: int) -> float:
        """Returns the Amount of RAM used by a Process via it's PID.
        
        Args:
            - pid (int): The Process ID (PID)
        
        Returns:
            - RAM (float): RAM Used in MiB"""
        
        return psutil.Process(pid).memory_info().rss / 1024 ** 2
    
class SoundModule:

    def PlaySound(filepath: str):
        """Plays a Sound on the Computer. Is Non-Blocking.
        
        Args:
            - filepath (str): The Filepath to the .mp3 File."""
        logging.info(f'Playing Sound at {filepath}')
        playsound(filepath, block=False)
        logging.info(f'Played Sound Successfully!')

class VersioningSystem:

    def GetVersionFromServer() -> str:
        """Gets the current PyYtDownloader-Remastered Version from the Server (ilollek.net)
        If a Connection to ilollek.net can't be established, it just skips the check and doesn't notify the User about it. You will see it in Log though.
        
        Returns:
            - Version (str): The Current Version as a string."""
        try:
            response = requests.get("https://ilollek.net/PYD-REM-ASSETS/VERSION")
            if response.status_code == 200:
                return response.text.strip()
            else:
                logging.error("Failed to retrieve version from server. Status code:", response.status_code)
        except requests.ConnectionError:
            logging.error("Failed to establish a connection to the server.")

    def CompareVersion(version: str) -> bool:
        """Compares the Version. If a newer Version is available, returns True. Otherwise False.
        
        Args:
            - version (str): The Current Version
            
        Returns:
            - newer_version_available (bool): True if a newer Version is available, otherwise False"""
        current_version = float(version)
        latest_version_str = VersioningSystem.GetVersionFromServer()
        if latest_version_str:
            latest_version = float(latest_version_str)
            if latest_version > current_version:
                logging.info("A newer version is available: %s", latest_version_str)
                return True
        logging.info("The current version is up to date.")
        return False
        

    
if __name__ == "__main__":
    print(f'RAM Used: {ResourceMonitor.RamUsedByProcess(os.getpid())} MiB')