import customtkinter
from tkinter import font
from collections import Counter
import random
import datetime
import Constants
from Data import Data

class Task(customtkinter.CTkFrame):
    def __init__(self, master, list, list_data):
        super().__init__(master=master)
        self.list = list
        self.list_data = list_data
        self.master = master

    def load_tasks_frame(self):
        list_name = self.list_data['name']

        self.list.lists_frame.destroy()
        self.list.welcome_label.destroy()

        self.master.adjust_window_geomtry(extended=True)

        self.tasks_frame = customtkinter.CTkFrame(self.list.main_frame, width=350, height=550, fg_color="#383736")
        self.tasks_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.tasks_frame.pack_propagate(False)

        tasks_title = customtkinter.CTkLabel(self.tasks_frame, text=f'{list_name} | Tasks',
            font=self.master.get_font(size=25)).pack(pady=30)
        
        tasks_back = customtkinter.CTkButton(self.tasks_frame, text="BACK", width=100, height=5, corner_radius=0,
            font=self.master.get_font(size=15, bold=True), fg_color="red", hover_color="dark red",
            command=lambda: self.list.reload_list_frame(self.tasks_frame)).place(relx=0.02,rely=0.92,anchor='w')
        
        add_task = customtkinter.CTkButton(self.tasks_frame, text="+", height=20, width=65, corner_radius=0,
            font=self.master.get_font(size=18, bold=True), fg_color="#00D1FF", text_color="white",
            hover_color="#26A6C2", command=lambda: self.load_create_task_menu(list_name)).place(relx=0.5,rely=0.92,anchor=customtkinter.CENTER)
        
    def load_create_task_menu(self, list_name: str):
        self.tasks_frame.destroy()

        self.master.adjust_window_geomtry()

        self.create_task_frame = customtkinter.CTkFrame(self.list.main_frame, width=500, height=400, fg_color="#383736")
        self.create_task_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.create_task_frame.pack_propagate(False)

        create_task_title = customtkinter.CTkLabel(self.create_task_frame, text="CREATE TASK",
            font=self.master.get_font(size=25)).pack(pady=10)

        create_task_close = customtkinter.CTkButton(self.create_task_frame, text="X", width=35, corner_radius=0,
            font=self.master.get_font(size=22, bold=True), fg_color="red", hover_color="dark red",
            command=lambda: self.reload_list_frame(self.create_task_frame)).place(relx=0.99,rely=0.06,anchor='e')

        self.master.seperator(self.create_task_frame)

        self.name_var = customtkinter.StringVar()
        self.description_var = customtkinter.StringVar()
        self.priority_var = customtkinter.StringVar()

        create_task_name = customtkinter.CTkEntry(self.create_task_frame, placeholder_text="NAME", corner_radius=0,
            width=400, border_width=0, fg_color="#D9D9D9", placeholder_text_color="black", text_color="black",
            font=self.master.get_font(size=25, bold=True), textvariable=self.name_var, justify=customtkinter.CENTER)
        create_task_name.place(relx=0.5,rely=0.25,anchor=customtkinter.CENTER)

        create_task_description = customtkinter.CTkEntry(self.create_task_frame, placeholder_text="DESCRIPTION", corner_radius=0,
            width=400, border_width=0, fg_color="#D9D9D9", placeholder_text_color="black", text_color="black",
            font=self.master.get_font(size=25, bold=True), textvariable=self.description_var, justify=customtkinter.CENTER)
        create_task_description.place(relx=0.5,rely=0.35,anchor=customtkinter.CENTER)

        create_task_priority = customtkinter.CTkEntry(self.create_task_frame, placeholder_text="PRIORITY", corner_radius=0,
            width=400, border_width=0, fg_color="#D9D9D9", placeholder_text_color="black", text_color="black",
            font=self.master.get_font(size=25, bold=True), textvariable=self.priority_var, justify=customtkinter.CENTER)
        create_task_priority.place(relx=0.5,rely=0.45,anchor=customtkinter.CENTER)

        create_task_complete = customtkinter.CTkButton(self.create_task_frame, text="COMPLETE", text_color="white",
            width=200, font=self.master.get_font(), 
            command=self.create_task_complete_activated).place(relx=0.5,rely=0.9,anchor=customtkinter.CENTER)
    
    def create_task_complete_activated(self):
        print(self.name_var.get())
        print(self.description_var.get())
        print(self.priority_var.get())

class List(customtkinter.CTkFrame):
    def __init__(self, master, username: str):
        super().__init__(master=master)
        self.username = username
        self.master = master

        self.load_list_menu()

    def load_list_menu(self):
        self.main_frame = customtkinter.CTkFrame(self.master, width=600, height=500, fg_color="transparent")
        self.main_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.main_frame.pack_propagate(False)

        self.load_list_frame()

    def load_list_frame(self):
        data = self.master.user_data.get()

        self.master.adjust_window_geomtry()

        self.lists_frame = customtkinter.CTkFrame(self.main_frame, width=500, height=400, fg_color="#383736")
        self.lists_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)

        self.welcome_label = customtkinter.CTkLabel(self.main_frame, text=f'Welcome {self.username}', 
            font=customtkinter.CTkFont(family="Arial", size=25, weight="normal"))
        self.welcome_label.pack(pady=10)

        create_list = customtkinter.CTkButton(self.lists_frame, text="CREATE LIST", width=200, height=35,
            font=customtkinter.CTkFont(family="Arial", size=15, weight="bold"), 
            command=self.load_create_list_menu).place(relx=0.5,rely=0.9,anchor=customtkinter.CENTER)

        if data['lists']:
            self.lists_container = customtkinter.CTkScrollableFrame(self.lists_frame, width=400, height=290,
                scrollbar_button_color="#2d2c2c", fg_color="transparent")
            self.lists_container.place(relx=0.5,rely=0.45,anchor=customtkinter.CENTER)
            self.load_saved_lists(data)
        else:
            lists_empty = customtkinter.CTkLabel(self.lists_frame, text="You have no lists \ncreate one to start setting tasks",
                font=self.master.get_font()).place(relx=0.5,rely=0.45,anchor=customtkinter.CENTER)
            
    def reload_list_frame(self, current_displaying_frame):
        current_displaying_frame.destroy()
        self.load_list_frame()

    def load_create_list_menu(self):
        self.lists_frame.destroy()
        self.welcome_label.destroy()

        self.master.adjust_window_geomtry()

        self.create_list_frame = customtkinter.CTkFrame(self.main_frame, width=500, height=300, fg_color="#383736")
        self.create_list_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.create_list_frame.pack_propagate(False)

        create_list_title = customtkinter.CTkLabel(self.create_list_frame, text="CREATE LIST",
            font=self.master.get_font(size=25)).pack(pady=10)

        create_list_close = customtkinter.CTkButton(self.create_list_frame, text="X", width=35, corner_radius=0,
            font=self.master.get_font(size=22, bold=True), fg_color="red", hover_color="dark red",
            command=lambda: self.reload_list_frame(self.create_list_frame)).place(relx=0.99,rely=0.07,anchor='e')

        self.master.seperator(self.create_list_frame)

        create_list_name = customtkinter.CTkEntry(self.create_list_frame, placeholder_text="NAME", corner_radius=0,
            width=400, border_width=0, fg_color="#D9D9D9", placeholder_text_color="black", text_color="black",
            font=self.master.get_font(size=25, bold=True), 
            justify=customtkinter.CENTER)
        create_list_name.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)

        create_list_complete = customtkinter.CTkButton(self.create_list_frame, text="COMPLETE", text_color="white",
            width=200, font=self.master.get_font(), 
            command=lambda: self.create_list_complete_activated(create_list_name.get())).place(relx=0.5,rely=0.9,anchor=customtkinter.CENTER)

    def create_list_status(self, status_error: str, list_name: str = None):
        if hasattr(self, 'status_error') and self.status_error.winfo_exists():
            self.status_error.destroy()
        self.status_error = customtkinter.CTkLabel(self.create_list_frame, text=Constants.DisplayErrors[status_error].format(name=list_name),
            font=self.master.get_font(), fg_color="transparent")
        self.status_error.place(relx=0.5,rely=0.65,anchor=customtkinter.CENTER)

    def create_list_complete_activated(self, name: str):
        original_name = name
        name = name.lower()
        data = self.master.user_data.get()
        if len(name) > Constants.App["ListNameMinimumLength"] and len(name) < Constants.App["ListNameMaximumLength"]:
            if not name in data['lists']:
                data['lists'][name] = {'name': original_name, 'tasks': {}, 'date_created': datetime.datetime.now()}
                self.master.user_data.update(data)
                self.reload_list_frame(self.create_list_frame)
            else:
                self.create_list_status("App_InvalidListName", list_name=name)
        else:
            self.create_list_status("App_InvalidListNameLength")

    def get_unfinished_tasks_count(self, tasks) -> int:
        return Counter(task_data['completed'] for task_data in tasks.values())[False]
    
    def load_saved_lists(self, data):
        for list_name, list_data in data['lists'].items():
            task = Task(master=self.master, list=self, list_data=list_data)

            list_item = customtkinter.CTkFrame(self.lists_container, width=400, height=100, fg_color="#5c5b5a")
            list_item.pack(pady=8)
            list_item.pack_propagate(False)

            customtkinter.CTkLabel(list_item, text=list_data['name'],
                    font=self.master.get_font(family="Roboto", size=17, bold=True)).place(relx=0.02,rely=0.15,anchor="w")

            unfinished_tasks_count = list_data['tasks'] and self.get_unfinished_tasks_count(list_data['tasks'])
            customtkinter.CTkLabel(list_item, text=not unfinished_tasks_count and "You have no tasks" 
                    or (unfinished_tasks_count > 0 and f'{unfinished_tasks_count} Unfinished Tasks' or 'All tasks completed'), 
                    font=self.master.get_font(size=16)).place(relx=0.02,rely=0.85,anchor="w")

            customtkinter.CTkButton(list_item, text="TASKS", width=70, height=20, corner_radius=0,
                    fg_color="#ECB528", hover_color="#C8940F", text_color="white", command=task.load_tasks_frame,
                    font=self.master.get_font(size=12, bold=True)).place(relx=0.78, rely=0.15,anchor="e")

            customtkinter.CTkButton(list_item, text="DELETE", width=70, height=20, corner_radius=0,
                    fg_color="#D74E4E", hover_color="#A92727", text_color="white", command=lambda: self.list_delete_activated(list_name),
                    font=self.master.get_font(size=12, bold=True)).place(relx=0.97, rely=0.15,anchor="e")

    def list_delete_activated(self, list_name: str):
        print(f'list delete clicked for: {list_name}')

class App(customtkinter.CTk):
    def __init__(self, username: str):
        super().__init__()
        self.username = username

        self.title("App")
        self.adjust_window_geomtry()
        self.resizable(width=False, height=False)

        self.user_data = Data(username)
        
        self.load_fonts()
        self.list = List(master=self, username=username)
        
        self.change_appearance("Dark")
        self.mainloop()

    def adjust_window_geomtry(self, extended: bool = False):
        self.geometry(f'{Constants.WindowWidth}x{extended and Constants.ExtendedWindowHeight or Constants.WindowHeight}')

    def get_font(self, family: str = None, size: int = 20, bold: bool = False):
        return customtkinter.CTkFont(family=family or Constants.BaseFont, size=size, 
                weight=f'{bold and "bold" or "normal"}')
    
    def seperator(self, master):
        seperator = customtkinter.CTkFrame(master, height=2, width=450, fg_color="white")
        seperator.pack(padx=0.5,pady=0.15)
        return seperator

    def load_fonts(self):
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.actual()

    def change_appearance(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    App("Test")