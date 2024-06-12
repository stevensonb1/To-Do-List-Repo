import customtkinter
from tkinter import font
import Constants
from Data import Data

class List(customtkinter.CTkFrame):
    def __init__(self, master, username: str):
        super().__init__(master)
        self.username = username
        self.mater = master

        self.load_list_menu()

    def load_list_menu(self):
        self.welcome_label = customtkinter.CTkLabel(self.master, text=f'Welcome {self.username}', 
                font=customtkinter.CTkFont(family=self.master.default_font, size=18, weight="normal"))
        self.welcome_label.place(relx=0.5,rely=0.1,anchor=customtkinter.CENTER)

class App(customtkinter.CTk):
    def __init__(self, username: str):
        super().__init__()
        self.username = username

        #Data(username)

        self.title("App")
        self.geometry(f"{Constants.WindowWidth}x{Constants.WindowHeight}")
        
        self.load_fonts()
        self.list = List(self, username)

        self.change_appearance("Dark")
        self.mainloop()

    def load_fonts(self):
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.actual()

    def change_appearance(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)