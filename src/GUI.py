# ! W A R N I N G !
# This is a Test to see if something like a DataGrid from WPF can be implemented Instead of a Listbox.
# If this ever comes to a good conclusion, the final Version will be put into the GUI.py File, and this will be deleted.
# Sincerely, iLollek


import customtkinter as ctk
import tkinter as tk
import SettingsWindow
from MiscUtils import ResourceObtainer
from CTkTable import *
from AppConfigReader import AppConfigReader
import threading
import logging

ResourceObtainerInstance = ResourceObtainer()

ctk.set_appearance_mode("System")

def GetAndChangeColorTheme(config):
    ColorTheme = config.GetConfigKeyValue("ColorTheme")
    if ColorTheme == "BlueTheme":
        print("Loading Blue Theme")
        ctk.set_default_color_theme("blue")
        return "blue"
    elif ColorTheme == "GreenTheme":
        print("Load Green Theme")
        ctk.set_default_color_theme("green")
        return "green"
    elif ColorTheme == "DarkBlueTheme":
        print("Load Dark Blue Theme")
        ctk.set_default_color_theme("dark-blue")
        return "darkblue"



class App:
    def __init__(self, root, download_button_callback, video_information_getter_callback, colortheme: str):
        root.title("PyYtDownloader Remastered - Starting...")
        root.geometry("1600x800")

        self.download_button_callback = download_button_callback
        self.video_information_getter_callback = video_information_getter_callback
        self.IsSettingsWindowOpen = False

        self.current_highlighted_row = 0

        self.userlogs = [] # Userlogs are Logs that are meant for the User to view in the sidebox when they press the row at index 0

        root.iconbitmap(ResourceObtainerInstance.GetResource("logo.ico"))

        # making the window resizable
        root.resizable(width=True, height=True)

        # Main Frame for LogBox
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="new")

        # LogBox (!!! CTkTable !!!)
        self.LogBox = CTkTable(self.main_frame, height=700, font=("system", 10), column=8, row=0, values=[["Channel", "Title", "Speed", "Elapsed Time", "Progress (%)", "Progress (Size)", "Status", "ID"]], corner_radius=0, command=self.show_video_information, hover_color=colortheme)
        self.LogBox.pack(expand=True, fill='both')
        self.LogBox.edit_row(row=0, height=10)

        # Video Frame
        self.video_frame = ctk.CTkFrame(root, width=300)
        self.video_frame.grid(row=0, column=1, sticky="nsew", padx=(0,20), pady=20)

        # Settings Button at the top of Video Frame
        self.SettingsButton = ctk.CTkButton(self.video_frame, text="Settings", command=self.open_settings)
        self.SettingsButton.pack(fill='x', padx=10, pady=(10,0))

        # VideoInfoBox inside Video Frame below Settings Button
        self.VideoInfoBox = ctk.CTkTextbox(self.video_frame, font=("system", 10))
        self.VideoInfoBox.pack(expand=True, fill='both', padx=10, pady=(10,0))

        # Bottom Frame for lower elements
        self.bottom_frame = ctk.CTkFrame(root)
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        # Entry Label
        self.entryLabel = ctk.CTkEntry(self.bottom_frame, placeholder_text="YouTube Link")
        self.entryLabel.pack(side='left', expand=True, fill='x', padx=(0,10))

        # Dropdown Menu
        self.dropdown = ctk.CTkOptionMenu(self.bottom_frame, values=["Video (mp4)", "Audio (mp3)"])
        self.dropdown.pack(side='left', expand=True, fill='x', padx=10)

        # Button
        self.actionButton = ctk.CTkButton(self.bottom_frame, text="Start Download from YouTube", command=self.perform_action)
        self.actionButton.pack(side='left', expand=True, fill='x', padx=(10,0))

        # Configure the grid to make the LogBox, VideoInfoBox, and bottom elements resize properly
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=4)  # LogBox has more weight
        root.grid_columnconfigure(1, weight=1)  # VideoInfoBox is slimmer
        root.grid_rowconfigure(1, weight=0)  # Bottom row

        self.VideoInfoBox.configure(state='disabled')

    def open_settings(self):
        # (iL) I don't think that I need to thread this. The Main GUI seems to work fine, even if this is open & running.
        if self.IsSettingsWindowOpen == False:
            self.IsSettingsWindowOpen = True
            app = SettingsWindow.App()
            app.mainloop()
            self.IsSettingsWindowOpen = False
            del app # (iL) I need to manually delete the app Instance since otherwise it throws some weird error. Maybe look into this?

    def show_video_information(self, data):

        video_id = self.LogBox.get_row(data["row"])[7]

        self.current_highlighted_row = data["row"]
        logging.info(f'Changed currently highlighted row to {self.current_highlighted_row}')

        if self.current_highlighted_row == 0:
            self.UpdateSideboxInformation()
        else:
            if self.video_information_getter_callback:
                videoinfodict = self.video_information_getter_callback(video_id)
            
    def UpdateSideboxInformation(self):
        """Updates the Sidebox Information. Automatically Checks if the highlighted Row is 0 - You can call this periodically."""

        # TODO: Add maximum amount of log history.

        if self.current_highlighted_row == 0:
            self.ClearSidebox()
            for entry in self.userlogs:
                self.InsertIntoSidebox(entry)

    def perform_action(self):

        if self.download_button_callback:
            threading.Thread(target=self.download_button_callback).start()

    def InsertIntoMainbox(self, uploaderchannelname: str, videotitle: str, currentdownloadspeed: str, elapsedtime: str, progresspercent:str, progressize: str, status: str, id: str):
        """Inserts Video Informational Content into the Table-Element on Screen.
        
        Args:
            - uploaderchannelname (str): The Channel Name of the YouTube-Video Uploader
            - videotitle (str): The Title of the YouTube-Video
            - currentdownloadspeed (str): The Current Download Speed
            - elapsedtime (str): The Elapsed Time
            - progresspercent (str): The Progress in Percent (%)
            - progressize (str): The Progress in Size (10MB / 20MB)
            - status (str): The YouTube-Engine Status
            - id (str): THe Video ID"""
        
        video_data = [uploaderchannelname, videotitle, str(currentdownloadspeed), elapsedtime, progresspercent, progressize, status, id]

        try:
            self.LogBox.add_row(index=1, height=10, values=video_data)
        except RuntimeError as e:
            logging.warning(f'RunTime Error when trying to Insert into the Mainbox (Download Progress Hook was too fast): {e}')

    def UpdateTableRowByID(self, uploaderchannelname: str, videotitle: str, currentdownloadspeed: str, elapsedtime: str, progresspercent:str, progressize: str, status: str, id: str):
        """Edits a Row's Data by it's ID.
        
        Args:
            - uploaderchannelname (str): The Channel Name of the YouTube-Video Uploader
            - videotitle (str): The Title of the YouTube-Video
            - currentdownloadspeed (str): The Current Download Speed
            - elapsedtime (str): The Elapsed Time
            - progresspercent (str): The Progress in Percent (%)
            - progressize (str): The Progress in Size (10MB / 20MB)
            - status (str): The YouTube-Engine Status
            - id (str): THe Video ID"""
        
        values = self.LogBox.get()
        row = 0
        try:
            for value in values:
                if id in value:
                    print(f'Found Video with ID {id} in TableRow: {row}')
                    self.LogBox.insert(row=row, column=0, value=uploaderchannelname)
                    self.LogBox.insert(row=row, column=1, value=videotitle)
                    self.LogBox.insert(row=row, column=2, value=currentdownloadspeed)
                    self.LogBox.insert(row=row, column=3, value=elapsedtime)
                    self.LogBox.insert(row=row, column=4, value=progresspercent)
                    self.LogBox.insert(row=row, column=5, value=progressize)
                    self.LogBox.insert(row=row, column=6, value=status)
                    self.LogBox.insert(row=row, column=7, value=id)
                    break
                row += 1
        except KeyError as e:
            logging.warning(f'KeyError when Inserting Table. Skipping this Update: {e}')

    def GetVideoInformationByID(self, video_id: str) -> dict:
        """Returns an Info-Dict based off of the Information shown in the GUI.
        
        Args:
            - video_id (str): The Video ID to search for
            
        Returns:
            - info_dict (dict): The Information Dictionary containing the Information visible on the GUI."""
        
        values = self.LogBox.get()
        row = 0
        try:
            for value in values:
                if video_id in value:
                    print(f'Found Video with ID {video_id} in TableRow: {row}')
                    video_values = self.LogBox.get_row(row)
                    info_dict = {}
                    info_dict["channel"] = video_values[0]
                    info_dict["title"] = video_values[1]
                    info_dict["download_speed"] = video_values[2]
                    info_dict["time_spent"] = video_values[3]
                    info_dict["percent"] = video_values[4]
                    info_dict["bytes"] = video_values[5]
                    info_dict["status"] = video_values[6]
                    info_dict["id"] = video_values[7]
                    return info_dict
                row += 1
        except KeyError as e:
            logging.warning(f'KeyError when Indexing Table: {e}')
    
    def CheckIfVideoIDInTable(self, video_id: str) -> bool:
        """Checks if the Video ID you provide in video_id is already present in the Table.
        
        Args:
            - video_id (str): The Video ID you want to check
            
        Returns:
            - Is Present (bool): True if it's present, False otherwise"""
        
        values = self.LogBox.get_column(column=7)
        if video_id in values:
            return True
        else:
            return False

    def InsertIntoSidebox(self, content: str):
        """Inserts a String of Content to the Sidebox and scrolls (yview) to it.
        
        Args:
            - content (str): The String of Content you want to display."""
        self.VideoInfoBox.configure(state='normal')
        self.VideoInfoBox.insert("end", content + "\n")
        self.VideoInfoBox.yview_moveto(1)
        self.VideoInfoBox.configure(state='disabled')

    def ClearSidebox(self):
        """Clears the Sidebox (VideoInfoBox) Entirely."""
        self.VideoInfoBox.configure(state='normal')
        self.VideoInfoBox.delete("0.0", "end")
        self.VideoInfoBox.configure(state='disabled')

    def GetVideoOrAudio(self) -> str:
        """Returns if the User wants to Download Video (mp4) or Audio (mp3)
        
        Returns:
            - Format (str): "mp4" for Video, "mp3" for Audio."""

        value = self.dropdown.get()
        match value:
            case "Video (mp4)":
                return "mp4"
            case "Audio (mp3)":
                return "mp3"

    def GetEntryContent(self) -> str:
        """Returns the Entry Content (The YouTube Link), but doesn't delete what has been inputted.
        
        Returns:
            - YouTube-Link (str): The YouTube Link to the Video or Playlist."""
        CONTENT = self.entryLabel.get()
        return CONTENT
    
    def ClearEntry(self):
        """Clears the Entry Label."""
        self.entryLabel.delete(0, "end")

if __name__ == "__main__":

    config = AppConfigReader("app.config")
    config.ReadAppConfig()

    root = ctk.CTk()
    app = App(root, None, None, None)

    example_video_data = [["Sewerslvt", "Lexapro Delirium", "4.20MB/s", "0:12", "Downloading"],
           ["Nails the Snail", "The Chill Vibes of Alterna ~ Splatoon 3 Music Mix", "3.19MB/s", "0:39", "Downloading"]]

    root.mainloop()
