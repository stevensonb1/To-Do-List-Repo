import customtkinter
from tkinter import font
from collections import Counter
from datetime import datetime
import Constants
import re as Regex
from Data import Data
from Timer import Timer
from tkcalendar import Calendar
from PIL import Image
from Loading import Loading
from queue import Queue
import Utility as util, pywinstyles, random, time, threading

class Task(customtkinter.CTkFrame):
    PRIORITY_LEVELS = [str(level+1) for level in range(5)]

    STATE_COLOURS =  [
        "#5c5b5a", # Not due
        "#CCCC00", # Due date getting closer
        "#FF8C00", # Due date very close
        "#8B0000", # Is due or pass due date
        "#006400", # Completed
    ]

    # Preloaded images
    DELETE_ICON = customtkinter.CTkImage(
        light_image=Image.open('images/trash.png'), dark_image=Image.open('images/trash.png'))
    CALENDAR_ICON = customtkinter.CTkImage(
        light_image=Image.open('images/calendar.png'), dark_image=Image.open('images/calendar.png'))
    LOADING_ICON = customtkinter.CTkImage(
        light_image=Image.open("images/loading.png"), dark_image=Image.open("images/loading.png"))

    def __init__(self, master, list, list_name: str):
        super().__init__(master=master)
        self.list = list
        self.list_name = list_name
        self.master = master

    def get_task_data(self, task_name: str = None):
        # returns user_data, task_data, task_id
        user_data = self.master.user_data.get()
        list_data = user_data['lists'][self.list_name]
        if not list_data:
            return
        for task_id, task_data in list_data['tasks'].items():
            if task_data.get('name') == task_name:
                return user_data, task_data, task_id

    def get_task_state(self, task_name: str) -> int:
        data, task_data, *other = self.get_task_data(task_name)
        if task_data['completed']:
            return len(self.STATE_COLOURS)-1
        due_date = task_data['due_date']

        due_datetime_str = f"{due_date['date']} {due_date['time']}"
        due_datetime = datetime.strptime(due_datetime_str, "%d/%m/%Y %I:%M %p")

        current_datetime = datetime.now()
        time_diff = (due_datetime - current_datetime).total_seconds()

        state = None
        if time_diff > 86400: # more than a day
            state = 1
        elif 3600 < time_diff <= 86400: # between 1 hour and 1 day
            state = 2
        elif 0 < time_diff <= 3600: # less than 1 hour
            state = 3
        else: # past due date
            state = 4
        return state-1
    
    def get_completed_tasks(self) -> dict:
        data = self.master.user_data.get()
        list_data = data['lists'][self.list_name]
        completed_tasks = {}
        for task_name, task_data in list_data['tasks'].items():
            if task_data['completed']:
                completed_tasks[task_name] = task_data
        return completed_tasks

    def load_tasks_frame(self):
        data = self.master.user_data.get()
        list_data = data['lists'][self.list_name]

        self.list.lists_frame.destroy()
        self.list.welcome_label.destroy()

        self.master.adjust_window_geomtry(extended=True)

        self.tasks_frame = customtkinter.CTkFrame(self.list.main_frame, width=350, height=550, fg_color="#383736")
        self.tasks_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.tasks_frame.pack_propagate(False)

        tasks_title = customtkinter.CTkLabel(self.tasks_frame, text=f'{list_data["name"]} | Tasks',
            font=self.master.get_font(size=25)).pack(pady=30)
                
        tasks_back = customtkinter.CTkButton(self.tasks_frame, text="BACK", width=100, height=5, corner_radius=0,
            font=self.master.get_font(size=15, bold=True), fg_color="red", hover_color="dark red",
            command=lambda: self.list.reload_list_frame(self.tasks_frame)).place(relx=0.02,rely=0.92,anchor='w')
        
        add_task = customtkinter.CTkButton(self.tasks_frame, text="+", height=20, width=65, corner_radius=0,
            font=self.master.get_font(size=18, bold=True), fg_color="#00D1FF", text_color="white",
            hover_color="#26A6C2", command=lambda: self.load_task_modify_menu(list_data['name'])).place(relx=0.5,rely=0.92,anchor=customtkinter.CENTER)
        
        if list_data['tasks']:
            self.tasks_container = customtkinter.CTkScrollableFrame(self.tasks_frame, width=300, height=350,
                    scrollbar_button_color="#2d2c2c", fg_color="transparent")
            self.load_saved_tasks(list_data)
        else:
             customtkinter.CTkLabel(self.tasks_frame, text="You have no tasks",
                font=self.master.get_font()).place(relx=0.5,rely=0.45,anchor=customtkinter.CENTER)
        
    def load_task_modify_menu(self, list_name: str = None, task_name: str = None):
        self.tasks_frame.destroy()

        self.master.adjust_window_geomtry()

        self.modify_task_frame = customtkinter.CTkFrame(self.list.main_frame, width=500, height=400, fg_color="#383736")
        self.modify_task_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.modify_task_frame.pack_propagate(False)

        data, task_data, task_id = self.get_task_data(task_name) if task_name else ({}, {}, None)
        due_date = task_data and task_data['due_date']

        task_description = task_data and task_data['description']
        priority_level = task_data and task_data['priority']
        task_date, task_time = due_date and due_date['date'], due_date and due_date['time']

        # Title
        customtkinter.CTkLabel(self.modify_task_frame, text=task_name and "EDIT TASK" or "CREATE TASK",
            font=self.master.get_font(size=25)).pack(pady=10)

        # Close
        customtkinter.CTkButton(self.modify_task_frame, text="X", width=35, corner_radius=0,
            font=self.master.get_font(size=22, bold=True), fg_color="red", hover_color="dark red",
            command=lambda: self.reload_tasks_frame(self.modify_task_frame)).place(relx=0.99,rely=0.06,anchor='e')

        self.master.seperator(self.modify_task_frame)

        placeholder_text_color = task_name and "black" or "grey"

        task_name_var = customtkinter.StringVar(value=task_name)
        task_description_var = customtkinter.StringVar(value=task_description)

        self.task_name = customtkinter.CTkEntry(self.modify_task_frame, corner_radius=0,
            width=400, border_width=0, fg_color="#D9D9D9", text_color="black", 
            textvariable=task_name and task_name_var,
            placeholder_text=task_name or "Task Name",
            placeholder_text_color=placeholder_text_color,
            font=self.master.get_font(size=25, bold=True), justify=customtkinter.CENTER)
        self.task_name.place(relx=0.5,rely=0.25,anchor=customtkinter.CENTER)

        self.task_description = customtkinter.CTkEntry(self.modify_task_frame, corner_radius=0,
            width=400, border_width=0, fg_color="#D9D9D9", text_color="black",  
            textvariable=task_name and task_description_var,
            placeholder_text=task_description or "Task Description", 
            placeholder_text_color=placeholder_text_color,
            font=self.master.get_font(size=25, bold=True), justify=customtkinter.CENTER)
        self.task_description.place(relx=0.5,rely=0.35,anchor=customtkinter.CENTER)

        priority_string_var = customtkinter.StringVar(value=priority_level and str(priority_level) or "1")

        self.task_priority = customtkinter.CTkComboBox(self.modify_task_frame, 
            values=self.PRIORITY_LEVELS, variable=priority_string_var, corner_radius=0,
            width=150, border_width=0, fg_color="#D9D9D9", text_color="black",
            font=self.master.get_font(size=25, bold=True))
        self.task_priority.place(relx=0.25,rely=0.45,anchor=customtkinter.CENTER)

        # Due date title
        customtkinter.CTkLabel(self.modify_task_frame, width=50, height=20, fg_color="transparent",
            bg_color="transparent", text="Due Date", text_color="white", 
            justify=customtkinter.LEFT).place(relx=0.1, rely=0.5)

        self.task_date = customtkinter.CTkLabel(self.modify_task_frame, width=75, height=35, fg_color="#D9D9D9",
            text_color="black", text=task_date or datetime.now().strftime("%d/%m/%Y"))
        self.task_date.place(relx=0.17,rely=0.6,anchor=customtkinter.CENTER)

        current_time = datetime.now()
        self.valid_time = task_time or f'{current_time.strftime("%I:%M")} {datetime.strptime(current_time.strftime("%H:%M"), "%H:%M").strftime("%p")}'
        
        self.time = customtkinter.StringVar(value=self.valid_time)
        self.task_time = customtkinter.CTkEntry(self.modify_task_frame, width=75, height=35, fg_color="#D9D9D9",
            text_color="black", textvariable=self.time, corner_radius=0)
        self.task_time.place(relx=0.35,rely=0.6,anchor=customtkinter.CENTER)
        self.task_time.bind('<Return>', self.validate_time)

        self.calendar = customtkinter.CTkButton(self.modify_task_frame, text="", corner_radius=0,
            width=20, image=self.CALENDAR_ICON, command=self.load_calendar)
        self.calendar.place(relx=0.475,rely=0.6,anchor=customtkinter.CENTER)

        # Button to create or save information about the task
        customtkinter.CTkButton(self.modify_task_frame, text=task_name and "SAVE" or "COMPLETE", text_color="white",
            width=200, font=self.master.get_font(),
            command=lambda: self.task_complete_activated(task_id)
            ).place(relx=0.5,rely=0.9,anchor=customtkinter.CENTER)

    def validate_time(self, event):
        time_str = self.time.get().upper()
        if "AM" in time_str or "PM" in time_str:
            try:
                formatted_time = datetime.strptime(time_str, "%I:%M %p").strftime("%I:%M %p")
                self.valid_time = formatted_time
                self.time.set(value=formatted_time)
            except ValueError:
                self.time.set(value=self.valid_time)
        else:
            self.time.set(value=self.valid_time)

    def load_calendar(self):
        def update_selected_date(event):
            self.task_date.configure(text=self.task_calendar.get_date())

        if hasattr(self, 'task_calendar'):
            self.task_calendar.destroy()

        self.task_calendar = Calendar(self.modify_task_frame, selectmode='day', mindate=datetime.now(),
            showeeknumbers=False, cusror='hand2', date_pattern='dd/mm/y')
        self.task_calendar.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.task_calendar.bind('<<CalendarSelected>>', update_selected_date)

    def create_task_template(self, task_data: dict):
        task_name = task_data['name']

        completed_check = customtkinter.IntVar()
        completed_check.set(value=task_data['completed'])

        task_state = self.get_task_state(task_name)

        def task_completed():
            data, task_data, *other = self.get_task_data(task_name)
            task_data['completed'] = completed_check.get() == 1
            self.master.user_data.update(data)
            self.reload_tasks_frame(self.tasks_frame)

        task_item = customtkinter.CTkFrame(self.tasks_container, width=400, height=100, fg_color=self.STATE_COLOURS[task_state])
        self.hidden_widgets.append([task_item, 8])
        task_item.pack_propagate(False)

        customtkinter.CTkLabel(task_item, text=task_data['name'],
            font=self.master.get_font(family="Roboto", size=17, bold=True)).place(relx=0.02,rely=0.15,anchor="w")
        
        customtkinter.CTkLabel(task_item, text=util.split_string(task_data['description'], 25),
            font=self.master.get_font(family="Roboto", size=15), 
            justify=customtkinter.LEFT).place(relx=0.02,rely=0.4,anchor="w")
        
        date_obj = datetime.strptime(task_data['due_date']['date'], "%d/%m/%Y")
        customtkinter.CTkLabel(task_item, 
            text=date_obj.strftime("%b %d")).place(relx=0.6, rely=0.1, anchor=customtkinter.CENTER)
        
        customtkinter.CTkButton(task_item, text="EDIT", fg_color="light blue",
            text_color="black", corner_radius=0, width=50, command=lambda: self.load_task_modify_menu(task_name=task_name),
            height=10).place(relx=0.8, rely=0.1, anchor=customtkinter.CENTER)
        
        customtkinter.CTkButton(task_item, text="", image=self.DELETE_ICON, fg_color="red",
            text_color="black", corner_radius=0, width=15, command=lambda: self.task_delete_activated(task_name),
            height=5).place(relx=0.95, rely=0.1, anchor=customtkinter.CENTER)
        
        customtkinter.CTkCheckBox(task_item, text="", fg_color="gray",
            hover_color="green", variable=completed_check, 
            command=task_completed).place(relx=0.9,rely=0.83, anchor=customtkinter.W)

    def task_delete_activated(self, task_name: str):
        data, task_data, task_id = self.get_task_data(task_name)
        list_data = data['lists'][self.list_name]
        list_data['tasks'].pop(task_id, None)
        self.master.user_data.update(data)
        self.reload_tasks_frame(self.tasks_frame)

    def load_saved_tasks(self, list_data):
        prioritised_dict = {}
        for task_name, task_data in list_data['tasks'].items():
            if task_data['completed'] == True:
                continue
            priority = int(task_data['priority'])
            prioritised_dict.setdefault(priority, {})[task_name] = task_data
        
        self.hidden_widgets = []
        
        loading_label = customtkinter.CTkLabel(self.tasks_frame, text='',
            width=100,height=100,bg_color="transparent", fg_color="transparent", image=self.LOADING_ICON)
        loading_label.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        pywinstyles.set_opacity(loading_label, color="#383736")

        loading = Loading(loading_label)
        loading.daemon = True
        loading.start()

        for level, data in sorted(prioritised_dict.items()):
            if not data:
                continue
            # Header
            header = customtkinter.CTkLabel(self.tasks_container, width=400, height=20,
                text=f'LEVEL {level}', font=self.master.get_font(size=15, bold=True))
            self.hidden_widgets.append(header)
            tasks = customtkinter.CTkFrame(self.tasks_container, width=400, height=2, fg_color="white")
            self.hidden_widgets.append([tasks, 2])
            # Tasks
            for task_name, task_data in data.items():
                self.create_task_template(task_data)
                
        self.load_completed_tasks()

        def load_widgets():
            # Tasks have finished loading
            self.tasks_container.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)

            for widget in self.hidden_widgets:
                if type(widget) is list:
                    widget[0].pack(pady=widget[1])
                else:
                    widget.pack()

            loading.end_loading()

        # arbitrary delay depending on the size of tasks ran on different thread
        threading.Timer(0.1*len(list_data['tasks']), load_widgets).start()

    def load_completed_tasks(self):
        completed_tasks = self.get_completed_tasks()
        if not completed_tasks:
            return
        header = customtkinter.CTkLabel(self.tasks_container, width=400, height=20,
                text=f'COMPLETED', font=self.master.get_font(size=15, bold=True))
        self.hidden_widgets.append(header)
        tasks = customtkinter.CTkFrame(self.tasks_container, width=400, height=2, fg_color="white")
        self.hidden_widgets.append([tasks, 2])
        for task_data in completed_tasks.values():
            self.create_task_template(task_data)
        
    def reload_tasks_frame(self, current_displaying_frame):
        current_displaying_frame.destroy()
        self.load_tasks_frame()
        
    def display_task_status(self, status_error: str, task_name: str = None, type: str = None): 
        if hasattr(self, 'status_error') and self.status_error.winfo_exists():
            self.status_error.destroy()
        self.status_error = customtkinter.CTkLabel(self.modify_task_frame, text=Constants.DisplayErrors[status_error].format(name=task_name, type=type),
            font=self.master.get_font(), fg_color="transparent")
        self.status_error.place(relx=0.5,rely=0.65,anchor=customtkinter.CENTER)
    
    def on_task_due(self, task_name: str):
        print(f'{task_name} is due')

    def task_complete_activated(self, unique_id: str = None):
        data = self.master.user_data.get()

        task_name = self.task_name.get()
        task_description = self.task_description.get()
        task_priority = self.task_priority.get()

        if len(task_name) == 0 or len(task_description) == 0:
            self.display_task_status("App_InvalidTaskInputLength")
        else:
            if not self.master.check_name_length(task_name):
                self.display_task_status("App_InvalidNameLength", type="Name")
                return
            if not self.master.is_valid(task_name):
                self.display_task_status("App_InvalidInput", type="Name")
                return
            
            list_data = data['lists'][self.list_name]

            if not unique_id:
                Timer(date=self.task_date.cget('text'), time=self.time.get(),
                    name=task_name, fn=self.master.task_due_notification).start()

                if any(sub_dic.get('name') == task_name.lower() for sub_dic in list_data['tasks'].values()):
                    self.display_task_status("App_InvalidName", type="task", task_name=task_name)
                    return
            
            completed_state = unique_id and list_data['tasks'][unique_id]['completed']
            list_data['tasks'][unique_id or util.generate_unique_id()] = {
                'completed': completed_state or False,
                'name': task_name,
                'description': task_description,
                'priority': task_priority,
                'due_date': {
                    'date': self.task_date.cget('text'),
                    'time': self.time.get()
                },
                'date_created': datetime.now()
            }
            self.master.user_data.update(data)
            self.reload_tasks_frame(self.modify_task_frame)

class List(customtkinter.CTkFrame):
    def __init__(self, master, username: str):
        super().__init__(master=master)
        self.username = username
        self.master = master

        data = self.master.user_data.get()
        for list_data in data['lists'].values():
            for task_data in list_data['tasks'].values():
                due_date = task_data['due_date']
                Timer(date=due_date['date'], time=due_date['time'],
                    name=task_data['name'], fn=self.master.task_due_notification).start()

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

        if not hasattr(self, 'welcome_label') or not self.welcome_label.winfo_exists(): 
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
            customtkinter.CTkLabel(self.lists_frame, text="You have no lists \ncreate one to start setting tasks",
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

        customtkinter.CTkLabel(self.create_list_frame, text="CREATE LIST",
            font=self.master.get_font(size=25)).pack(pady=10)

        customtkinter.CTkButton(self.create_list_frame, text="X", width=35, corner_radius=0,
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

    def display_list_status(self, status_error: str, name: str = None, type: str = None):
        if hasattr(self, 'status_error') and self.status_error.winfo_exists():
            self.status_error.destroy()
        self.status_error = customtkinter.CTkLabel(self.create_list_frame, text=Constants.DisplayErrors[status_error].format(name=name, type=type),
            font=self.master.get_font(), fg_color="transparent")
        self.status_error.place(relx=0.5,rely=0.65,anchor=customtkinter.CENTER)

    def create_list_complete_activated(self, list_name: str):
        data = self.master.user_data.get()
        if not self.master.check_name_length(list_name):
            self.display_list_status("App_InvalidNameLength", name="List")
            return
        if list_name.lower() in data['lists']:
            self.display_list_status("App_InvalidName", type="list", name=list_name)
            return
        data['lists'][list_name.lower()] = {
            'name': list_name,
            'tasks': {},
            'date_created': datetime.now()
        }
        self.master.user_data.update(data)
        self.reload_list_frame(self.create_list_frame)

    def get_unfinished_tasks_count(self, tasks) -> int:
        return Counter(task_data['completed'] for task_data in tasks.values())[False]
    
    def load_saved_lists(self, data):
        for list_name, list_data in data['lists'].items():
            task = Task(master=self.master, list=self, list_name=list_name)

            list_item = customtkinter.CTkFrame(self.lists_container, width=400, height=100, fg_color="#5c5b5a")
            list_item.pack(pady=8)
            list_item.pack_propagate(False)

            customtkinter.CTkLabel(list_item, text=list_data['name'],
                    font=self.master.get_font(family="Roboto", size=17, bold=True)).place(relx=0.02,rely=0.15,anchor="w")

            unfinished_tasks_count = list_data['tasks'] and self.get_unfinished_tasks_count(list_data['tasks'])
            customtkinter.CTkLabel(list_item, text=isinstance(unfinished_tasks_count, dict) and "You have no tasks" 
                    or (unfinished_tasks_count > 0 and f'{unfinished_tasks_count} Unfinished Tasks' or 'All tasks completed'), 
                    font=self.master.get_font(size=16)).place(relx=0.02,rely=0.85,anchor="w")

            customtkinter.CTkButton(list_item, text="TASKS", width=70, height=20, corner_radius=0,
                    fg_color="#ECB528", hover_color="#C8940F", text_color="white", command=task.load_tasks_frame,
                    font=self.master.get_font(size=12, bold=True)).place(relx=0.78, rely=0.15,anchor="e")

            customtkinter.CTkButton(list_item, text="DELETE", width=70, height=20, corner_radius=0,
                    fg_color="#D74E4E", hover_color="#A92727", text_color="white", 
                    command=lambda list_name=list_name: self.list_delete_activated(list_name),
                    font=self.master.get_font(size=12, bold=True)).place(relx=0.97, rely=0.15,anchor="e")

    def list_delete_activated(self, list_name: str):
        data = self.master.user_data.get()
        data['lists'].pop(list_name, None)
        self.master.user_data.update(data)
        self.reload_list_frame(self.lists_frame)

class Notification(customtkinter.CTk):
    DISPLAY_TIME = 5

    def __init__(self, root):
        super().__init__()
        self.root = root
        self.queue = Queue()
        self.is_displaying = False

        self.notification_frame = customtkinter.CTkFrame(root, width=100, height=50,
            bg_color="transparent", fg_color="transparent")
        self.notification_frame.pack(side=customtkinter.BOTTOM, fill=customtkinter.X)
        self.notification_label = customtkinter.CTkLabel(self.notification_frame, 
            text="", height=40, font=('Helvetica', 20, 'bold'))
        self.notification_label.pack()

    def show_notification(self, message: str):
        self.queue.put(message)
        if not self.is_displaying:
            self.display_next_notification()
    
    def display_next_notification(self):
        if not self.queue.empty():
            self.is_displaying = True
            message = self.queue.get()
            self.notification_label.configure(text=message)
            self.notification_frame.after(self.DISPLAY_TIME*1000, self.hide_notification)

    def hide_notification(self):
        self.notification_label.configure(text="")
        self.is_displaying = False
        self.display_next_notification()

class App(customtkinter.CTk):
    def __init__(self, username: str):
        super().__init__()
        self.username = username

        self.title("App")
        self.adjust_window_geomtry()
        self.resizable(width=False, height=False)

        # runtime events
        self.notification_ready = threading.Event()

        self.user_data = Data(username)
        
        self.load_fonts()
        self.list = List(master=self, username=username)
        
        self.notification = Notification(self)
        self.notification_ready.set()

        self.change_appearance("Dark")
        self.mainloop()

    def task_due_notification(self, task_name: str):
        # waits for notification ready event to fire
        # calls show_nofication method to display GUI
        # that a task is due
        def notification_async():
            self.notification_ready.wait()
            self.notification.show_notification(f'"{task_name}" is due')
        threading.Thread(target=notification_async, daemon=True).start()

    def adjust_window_geomtry(self, extended: bool = False):
        self.geometry(f'''{Constants.WindowWidth}x{(extended 
            and Constants.ExtendedWindowHeight or Constants.WindowHeight)}''')

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

    def is_valid(self, input: str):
        return Regex.compile(r"^[^<>/{}[\]~`]*$").match(input)
    
    def check_name_length(self, name: str):
        return (len(name) > Constants.App["NameMinimumLength"] 
                and len(name) < Constants.App["NameMaximumLength"])

    def change_appearance(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    App("Test")