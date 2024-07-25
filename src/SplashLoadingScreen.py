import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from MiscUtils import ResourceObtainer

ResourceObtainerInstance = ResourceObtainer()

class SplashScreen(tk.Tk):
    def __init__(self, startup_function_callback):
        super().__init__()

        self.startup_function_callback = startup_function_callback

        self.is_initialized = False

        self.title("Splash Loading Screen")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.overrideredirect(True)  # Hide title bar

        # Load and display GIF image
        self.load_gif()

        # Add labels
        self.top_label = ttk.Label(self, text="PyYtDownloader-Remastered", font=("Helvetica", 20))
        self.top_label.pack(pady=(50, 0))

        self.bottom_label = ttk.Label(self, text="Initializing...", font=("Helvetica", 12))
        self.bottom_label.pack(pady=(0, 50))

        # Center window on screen
        self.center_window()

        self.is_initialized = True  # Set initialization status to True

        self.after(100, startup_function_callback)

    def load_gif(self):
        # Load GIF image
        gif_path = ResourceObtainerInstance.GetResource("loading_nezuko2.gif")
        original_gif = Image.open(gif_path)
        original_gif_frames = []

        try:
            while True:
                original_gif_frames.append(original_gif.copy())
                original_gif.seek(len(original_gif_frames))  # Go to next frame
        except EOFError:
            pass

        # Resize GIF frames using Lanczos resampling
        self.gif_frames = [ImageTk.PhotoImage(frame.resize((200, 200), Image.LANCZOS)) for frame in original_gif_frames]

        # Show GIF on a label
        self.gif_label = ttk.Label(self, image=self.gif_frames[0])
        self.gif_label.pack()

        # Animation
        self.animate(0)

    def animate(self, frame):
        self.update()
        self.gif_label.config(image=self.gif_frames[frame])
        self.after(100, lambda: self.animate((frame + 1) % len(self.gif_frames)))

    def center_window(self):
        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position x and y for the window to be centered
        x = int((screen_width - self.winfo_reqwidth()) / 2)
        y = int((screen_height - self.winfo_reqheight()) / 2)

        # Set the window position
        self.geometry(f"+{x}+{y}")

    def ChangeModule(self, module_name: str):
        """Changes the Module Name Displayed on Screen.
        
        Args:
            - module_name (str): The Name of the Module"""
        
        self.bottom_label.config(text = module_name)
        self.update()

    def CheckIfInitialized(self) -> bool:
        """Checks if the GUI window is initialized (appears on screen)
        
        Returns:
            - Is initialized (bool): True if initialized, false otherwise"""
        return self.is_initialized



if __name__ == "__main__":
    splash = SplashScreen(None)
    splash.mainloop()
