import customtkinter
from tkinter import font
import random

class App(customtkinter.CTk):
    def __init__(self, username: str):
        super().__init__()
        self.username = username

    def load_app_menu(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2,3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.actual()

        self.username_label = customtkinter.CTkLabel(self.sidebar_frame, text="Welcome "+self.username, font=customtkinter.CTkFont(family=self.default_font, size=18, weight="normal"))
        self.username_label.grid(row=1, column=0)

        self.task_title = customtkinter.CTkLabel(self.sidebar_frame, text="Tasks", font=customtkinter.CTkFont(family=self.default_font, size = 15, weight="normal"))
        self.task_title.grid(row=2, column=0, pady=20)
        self.task_container = customtkinter.CTkScrollableFrame(self.sidebar_frame, width=120)
        self.task_container.grid(row=3, column=0)

        self.change_appearance_button = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark"],
                                                                    command=self.change_appearance_mode_event)
        self.change_appearance_button.grid(row=6, column=0, padx=20, pady=(10, 10))

        self.change_appearance.set("Dark")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)