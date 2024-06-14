import customtkinter
from tkinter import font
import random
import Constants
from Data import Data

class List(customtkinter.CTkFrame):
    def __init__(self, parent, username: str):
        super().__init__(master=parent)
        self.username = username
        self.master = parent

        self.load_list_menu()

    def load_list_menu(self):
        self.main_frame = customtkinter.CTkFrame(self.master, width=600, height=500, fg_color="transparent")
        self.main_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.main_frame.pack_propagate(False)

        self.welcome_label = customtkinter.CTkLabel(self.main_frame, text=f'Welcome {self.username}', 
                font=customtkinter.CTkFont(family="Arial", size=25, weight="normal"))
        self.welcome_label.pack(pady=10)

        self.lists_frame = customtkinter.CTkFrame(self.main_frame, width=500, height=400, fg_color="#383736")
        self.lists_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)

        self.create_list = customtkinter.CTkButton(self.lists_frame, text="CREATE LIST", width=200, height=35,
                font=customtkinter.CTkFont(family="Arial", size=15, weight="bold"))
        self.create_list.place(relx=0.5,rely=0.9,anchor=customtkinter.CENTER)

        self.lists_container = customtkinter.CTkScrollableFrame(self.lists_frame, width=400, height=290,
                scrollbar_button_color="#2d2c2c", fg_color="transparent")
        self.lists_container.place(relx=0.5,rely=0.45,anchor=customtkinter.CENTER)

        self.load_saved_lists()

    def load_saved_lists(self):
        for i in range(5):
            list_item = customtkinter.CTkFrame(self.lists_container, width=400, height=100, fg_color="#5c5b5a")
            list_item.pack(pady=8)
            list_item.pack_propagate(False)

            list_name_label = customtkinter.CTkLabel(list_item, text="List Name",
                    font=self.master.get_font(family="Roboto", size=17, bold=True))
            list_name_label.place(relx=0.02,rely=0.15,anchor="w")

            list_unfinished_tasks_label = customtkinter.CTkLabel(list_item, text=f'{random.randrange(1, 10)} Unfinished Tasks', 
                    font=self.master.get_font(size=16))
            list_unfinished_tasks_label.place(relx=0.02,rely=0.85,anchor="w")

            list_edit_button = customtkinter.CTkButton(list_item, text="EDIT", width=70, height=20, corner_radius=0,
                    fg_color="#ECB528", hover_color="#C8940F", text_color="white", command=lambda: self.list_edit_activated("name"),
                    font=self.master.get_font(size=12, bold=True))
            list_edit_button.place(relx=0.78, rely=0.15,anchor="e")

            list_delete_button = customtkinter.CTkButton(list_item, text="DELETE", width=70, height=20, corner_radius=0,
                    fg_color="#D74E4E", hover_color="#A92727", text_color="black", command=lambda: self.list_edit_activated("name"),
                    font=self.master.get_font(size=12, bold=True))
            list_delete_button.place(relx=0.97, rely=0.15,anchor="e")

    def list_edit_activated(self, list_name: str):
        print(f'list edit clicked for: {list_name}')

    def list_delete_activated(self, list_name: str):
        print(f'list delete clicked for: {list_name}')
            

class App(customtkinter.CTk):
    def __init__(self, username: str):
        super().__init__()
        self.username = username

        self.title("App")
        self.geometry(f"{Constants.WindowWidth}x{Constants.WindowHeight}")
        
        self.load_fonts()
        self.list = List(parent=self, username=username)

        self.user_data = Data("Tony_Account")
        if self.user_data.load() == None:
            print("User has no data, giving data..")
            self.user_data.save({"name": "Alice", "age": 30})
        print(f'user_data: {self.user_data.load()}')

        self.change_appearance("Dark")
        self.mainloop()

    def get_font(self, family: str = None, size: int = 20, bold: bool = False):
        return customtkinter.CTkFont(family=family or Constants.BaseFont, size=size, 
                                     weight=f'{bold and "bold" or "normal"}')

    def load_fonts(self):
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.actual()

    def change_appearance(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    App("Test")