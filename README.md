# PyYtDownloader-Remastered
A Remaster of the Popular PyYtDownloader (Versions) made by iLollek. 

# Information about Application Generation
PyYtDownloader Remastered, PyYtDownloader-Remastered or PYD Remastered is Software made by iLollek.
It belongs to the Family of Shamshel-related Applications made by iLollek, therefore it's also called the fourth (4th) generation of iLollek Software.
The Shamshel Generation Software also includes Software like PyChat-Remastered.
Software made by iLollek that belongs to the Shamshel Generation is usually known by having a "Remastered" in the Name. Otherwise you can easily detect such Software by the use of a threaded Customtkinter GUI and/or a highly OOP approach.

Other Generations are:

- 1st Generation (Adam)
- 2nd Generation (Lilith)
- 3rd Generation (Sachiel)
- 4th Generation (Shamshel)

## 1st Generation (Adam)
The first Generation of iLollek Desktop Software is named "Adam" and mostly consisted of poorly written Python-Scripts consisting of one File and no self-defined Functions or Classes. This Generation has poor Documentation to this Day so the only notable Software Products are the edited Version of the Twitch Channel Point Miner & SecureNotes.

## 2nd Generation (Lilith)
The second Generation of iLollek Desktop Software is named "Lilith" and also suffers from poor Documentation to this Day. This Generation lived the longest. This Generation did not feature anything significant, mostly again consisting of poorly written Python Scripts in one File, although they did include some kind of self-defined Functions. Notable Products are xCloud.

## 3rd Generation (Sachiel)
The third Generation of iLollek Desktop Software is named "Sachiel" and that Generation was "the big gap" between the "old-gen" Software and "new-gen" Software we know today. Sachiel-Generation Software featured a heavy take on Object-Oriented Programming, Modularization and Clean-Code Principles, mostly adapted from C# & .NET Programming with an attempt to port said Guidelines and Concepts to Python. The only Notable Software in this short-lived Generation is BerichtsheftGenerator.

## 4th Generation (Shamshel)
The fourth Generation of iLollek Desktop Software is named "Shamshel". Shamshel-Generation Software is the current one (the time of creation of this Document & PyYtDownloader-Remastered). Software from this Generation features a more seamless Integration with Microsoft Windows such as Bundled EXEs, an automatic Installer and the usage of the Windows API.

# About PyYtDownloader-Remastered

## Languages
Currently, PyYtDownloader-Remastered is only available in the following Languages:
- English

We want to work on translating PyYtDownloader-Remastered into different Languages. Planned are German, however we would love more Contributors to contribute more languages!

## Main Dependencies
- FFMpeg
- yt-dlp
- customtkinter

## Usage
To download a Video, just input the Link to the YouTube Video (either in your Browsers URL Bar or the shortened Link that you get when using the "Share" function) and click "Download from YouTube" - Optionally, if you have FFmpeg installed, you can also choose to only Download the Audio in the .mp3 Format (might be useful for Downloading Music)

To Download FFmpeg, you can press the "Download FFmpeg" Button in the Settings Window.

## Settings & Configuration
Essentially, you can configure everything from the Settings Window, except for a few more "niche"-like optional Settings. If you want to edit the Settings directly, navigate to the Folder where PyYtDownloader-Remastered is installed and inside the SystemData Folder you will find the app.config File. Open said app.config File using a Text Editor of your choice.

Supported Browsers for the YouTube Cookie generation are:
- most Chromium Based Browsers, probably (like Google Chrome)
- Mozilla Firefox
- Microsoft Edge
- Internet Explorer
- Brave
- Opera GX

## Known Issues
### CTkTable's performance is poor
One known Issue is the poor performance of the CTkTable. Especially when Downlodaing a Playlist with parallel Downloading enabled, the Box slows everything down. When too many Video Objects are Displayed in the CTkTable, moving or resizing the Window barely works. I have [Addressed the Issue](https://github.com/Akascape/CTkTable/issues/74), and  [the Author of CTkTable](https://github.com/Akascape/) said he will work on it. Once a good Update becomes available, I will implement it.

# Authors & Credits
- [iLollek](https://github.com/ilollek): Main Developer of PyYtDownloader-Remastered, Repository Owner, Product Owner of PyYtDownloader-Remastered
- [Lucien_Lachance (lucienlach)](https://github.com/lucienlach): Tester for PyYtDownloader-Remastered
- [CTKDesigner](https://ko-fi.com/s/6fca1ae70f): No-Code Tool for Designing customtkinter GUIs
- [yt-dlp](https://github.com/yt-dlp/yt-dlp): Engine for interacting with YouTube
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter): Graphical User Interface
- [FFmpeg](https://github.com/FFmpeg/FFmpeg): Post-Processing Interface
- [CTkTable](https://github.com/Akascape/CTkTable): Used for Displaying Download Progress Data (Main Box)
