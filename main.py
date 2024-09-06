"""
This module defines the "Main" class, which initializes the root window,
manages its size and state, and handles widget management. It also launches
the `Login` class for user authentication.

Imports:
- customtkinter: Custom Tkinter widgets for modern GUI.
- constants: Contains constants for app configuration.
- Login: Class for user login and account management.
- App: Class for the main application.

Classes:
    Main: Handles the creation and management of the main app window.

Attributes:
    root (customtkinter.CTk): The main application window.
    window_extended (bool): Indicates whether the extended view is active.
    previous_window_extended (bool): Stores the previous window extension state.
    previous_widgets (list): Stores the previous state of widgets.

Methods:
    __init__(): Initializes the main class and the login window.
    adjust_window_geometry(extended: bool = False): Adjusts the window size 
                                                    based on the extended view.
    remove_current_state(): Removes all widgets currently 
                            displayed in the root window.
    save_current_state(): Saves the current state of the window and its widgets.
    hide_current_state(): Hides all widgets without removing them.
    restore_previous_state(): Restores the previous state 
                              of the window and its widgets.

Author: Blake Stevenson
Date: 2024-09-06
Version: 1.0
License: MIT
"""

import customtkinter
import constants

from login import Login
from app import App

customtkinter.set_appearance_mode("dark")

class Main:
    """    
    It initializes the root window, manages the window size,
    and handles widget states.
    """
    
    def __init__(self):
        """
        Initializes the main class by creating the root window and
        initializing the login class.
        """
        super().__init__()
        self.root = customtkinter.CTk()
        self.root.title(constants.AppName)
        self.root.resizable(width=False, height=False)

        Login(self)

    def adjust_window_geometry(self, extended: bool = False):
        """
        Adjusts the window geometry based on whether the extended
        view is active or not.
        """
        self.window_extended = extended
        
        width = constants.WindowWidth
        height = (constants.ExtendedWindowHeight if extended 
                  else constants.WindowHeight)
        
        self.root.geometry(f"{width}x{height}")

    def remove_current_state(self):
        """
        Removes all widgets currently displayed in the main root window.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def save_current_state(self):
        """
        Saves the current state of the window, including its size
        and the properties of its children widgets.
        """
        self.previous_window_extended = self.window_extended
        self.previous_widgets = []
        
        for widget in self.root.winfo_children():
            manager = widget.winfo_manager()
            layout_info = None

            if manager == 'pack':
                layout_info = widget.pack_info()
            elif manager == 'grid':
                layout_info = widget.grid_info()
            elif manager == 'place':
                layout_info = widget.place_info()

            self.previous_widgets.append((widget, manager, layout_info))

    def hide_current_state(self):
        """
        Hides all widgets currently displayed in the main root window
        without removing them.
        """
        for widget in self.root.winfo_children():
            if widget.winfo_manager() == 'pack':
                widget.pack_forget()
            elif widget.winfo_manager() == 'place':
                widget.place_forget()
            elif widget.winfo_manager() == 'grid':
                widget.grid_forget()

    def restore_previous_state(self):
        """
        Restores the previous state of the window, including its size
        and the properties of its widgets.
        """
        self.adjust_window_geometry(self.previous_window_extended)

        for widget, manager, layout_info in self.previous_widgets:
            if manager == 'pack':
                widget.pack(**layout_info)
            elif manager == 'grid':
                if 'in' in layout_info:
                    del layout_info['in']
                widget.grid(**layout_info)
            elif manager == 'place':
                layout_info.pop('width', None)
                layout_info.pop('height', None)

                for key in ['x', 'y', 'relx', 'rely']:
                    if key in layout_info:
                        try:
                            layout_info[key] = float(layout_info[key])
                        except ValueError:
                            print(f"skipping invalid key")
                widget.place(**layout_info)

if __name__ == "__main__":
    Main().root.mainloop()
