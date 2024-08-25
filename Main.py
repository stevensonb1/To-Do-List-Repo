import customtkinter
import Constants
from Login import Login
from App import App

# GUI is dark mode by default
customtkinter.set_appearance_mode("dark")

class Main():
    def __init__(self):
        super().__init__()
        # Creates the main root "window" and initialises the login
        self.root = customtkinter.CTk()
        self.root.title(Constants.AppName)
        self.root.resizable(width=False, height=False)

        #Login(self)
        App(main=self, username="Test")

    def adjust_window_geometry(self, 
        extended: bool = False
    ):
        # Stores the window size and updates the root geometry
        self.window_extended = extended
        self.root.geometry(f'''{Constants.WindowWidth}x{(extended 
            and Constants.ExtendedWindowHeight or Constants.WindowHeight)}''')
        
    def remove_current_state(self):
        # Removes any widgets that are displayed in the main root
        for widget in self.root.winfo_children():
            widget.destroy()

    def save_current_state(self):
        # Stores window size and stores widget properties in a list
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
        # Hides any widgets that are displayed in the main root
        for widget in self.root.winfo_children():
            if widget.winfo_manager() == 'pack':
                widget.pack_forget()
            elif widget.winfo_manager() == 'place':
                widget.place_forget()
            elif widget.winfo_manager() == 'grid':
                widget.grid_forget()

    def restore_previous_state(self):
        # Resets the window size back to previous geometry
        self.adjust_window_geometry(self.previous_window_extended)

        # Places widgets that were hidden with the same properties
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
                            print(f"""skipping invalid value
                                    for {key}: {layout_info[key]}"""
                            )
                widget.place(**layout_info)

# Runs main class if file is manually ran
if __name__ == "__main__":
    Main().root.mainloop()
