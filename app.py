"""
This module provides functionality to manage and display lists and
tasks within a customtkinter based application.

Author: Blake Stevenson
Date: 2024-09-06
Version: 1.0
License: MIT
"""

import customtkinter
import constants
import re as Regex
import utility as util
import pywinstyles
import threading

from tkinter import font    
from collections import Counter
from datetime import datetime
from data import Data
from timer import Timer
from tkcalendar import Calendar
from PIL import Image
from loading import Loading
from queue import Queue


# Private functions
def is_valid(input: str):
    """
    Uses regex library to validate input does not contain any of the.
    """
    return Regex.compile(r"^[^<>/{}[\]~`]*$").match(input)
    

def check_name_length(name: str):
    """
    Returns boolean depending on if name fits within requirements.
    """
    return (len(name) > constants.App["NameMinimumLength"] 
        and len(name) < constants.App["NameMaximumLength"])


def check_desc_length(desc: str):
    """
    Returns boolean depending on if desc fits within requirements.
    """
    return len(desc) < constants.App["DescriptionMaximumLength"]


# Variables
due_date_timers = {}


# Constants
STATE_COLOURS = [
    "#8a8a8a", 
    "#d4d400",
    "#e68a00", 
    "#6c3b3b",
    "#004d00", 
]

COLOUR_STATE_INFOS = [
    "Due date is over a day",
    "Due date is within an hour and a day",
    "Due date is less than an hour away",
    "Task is due",
    "Task is completed"
]


class Task(customtkinter.CTkFrame):
    """
    A class representing a task within a to-do list
    """
    PRIORITY_LEVELS = [str(level+1) for level in range(5)]

    DELETE_ICON = customtkinter.CTkImage(
        size=(18,17),
        light_image=Image.open('images/trash.png'), 
        dark_image=Image.open('images/trash.png'))
    
    CALENDAR_ICON = customtkinter.CTkImage(
        light_image=Image.open('images/calendar.png'), 
        dark_image=Image.open('images/calendar.png'))
    
    LOADING_ICON = customtkinter.CTkImage(
        light_image=Image.open("images/loading.png"), 
        dark_image=Image.open("images/loading.png"))

    def __init__(self, master, data, main, list, list_name: str):
        """
        Initialises the task class.
        """
        super().__init__(master=master)
        self.list = list
        self.list_name = list_name
        self.master = master
        self.user_data = data
        self.main = main

    def get_task_data(self, task_name: str) -> tuple[dict, dict, str]:
        """
        Retrieves task data based on the task name

        Returns:
            tuple: A tuple containing user data, task data, and task ID.
        """
        user_data = self.user_data.get()
        list_data = user_data['lists'][self.list_name]
        
        if not list_data:
            return
        
        for task_id, task_data in list_data['tasks'].items():
            if task_data.get('name') == task_name:
                return user_data, task_data, task_id

    def get_task_state(self, task_name: str) -> int:
        """
        Determines the state of the task based on its due date.
        """
        data, task_data, *_ = self.get_task_data(task_name)
        if task_data['completed']:
            return len(STATE_COLOURS)-1
        due_date = task_data['due_date']

        due_datetime_str = f"{due_date['date']} {due_date['time']}"
        due_datetime = datetime.strptime(due_datetime_str, "%d/%m/%Y %I:%M %p")

        current_datetime = datetime.now()
        time_diff = (due_datetime - current_datetime).total_seconds()

        state = None
        if time_diff > 86400:
            state = 1
        elif 3600 < time_diff <= 86400: 
            state = 2
        elif 0 < time_diff <= 3600:
            state = 3
        else:
            state = 4
        return state-1
    
    def get_completed_tasks(self) -> dict:
        """
        Retrieves all completed tasks from the task list.
        """
        data = self.user_data.get()
        list_data = data['lists'][self.list_name]
        completed_tasks = {}
        
        for task_name, task_data in list_data['tasks'].items():
            if task_data['completed']:
                completed_tasks[task_name] = task_data
        
        return completed_tasks

    def load_tasks_frame(self):
        """
        Loads and displays the frame containing all tasks in the list.
        """
        data = self.user_data.get()
        list_data = data['lists'][self.list_name]

        self.list.lists_frame.destroy()
        self.list.welcome_label.destroy()

        self.main.adjust_window_geometry(extended=True)

        self.tasks_frame = customtkinter.CTkFrame(
            self.list.main_frame,
            width=350, 
            height=550, 
            fg_color="#383736"
        )
        self.tasks_frame.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
        self.tasks_frame.pack_propagate(False)

        customtkinter.CTkLabel(
            self.tasks_frame,
            text=f'{list_data["name"]} | Tasks',
            font=self.main.get_font(size=25)
        ).pack(pady=30)

        def back_clicked():
            self.list.reload_list_frame(self.tasks_frame)

        customtkinter.CTkButton(
            self.tasks_frame, 
            text="BACK", 
            width=100, 
            height=5, 
            corner_radius=0, 
            font=self.main.get_font(size=15, bold=True),
            fg_color="red", 
            hover_color="dark red",
            command=back_clicked
        ).place(relx=0.02, rely=0.92, anchor='w')

        def create_task():
            self.load_task_modify_menu(list_data['name'])

        customtkinter.CTkButton(
            self.tasks_frame, 
            text="+",
            height=20, 
            width=65, 
            corner_radius=0, 
            font=self.main.get_font(size=18, bold=True),
            fg_color="#00D1FF", 
            text_color="white", 
            hover_color="#26A6C2",
            command=create_task 
        ).place(relx=0.5, rely=0.92, anchor=customtkinter.CENTER)

        if list_data['tasks']:
            self.tasks_container = customtkinter.CTkScrollableFrame(
                self.tasks_frame, 
                width=300, 
                height=350,
                scrollbar_button_color="#2d2c2c", 
                fg_color="transparent"
            )
            self.load_saved_tasks(list_data)
        else:
            customtkinter.CTkLabel(
                self.tasks_frame, 
                text="You have no tasks",
                font=self.main.get_font()
            ).place(relx=0.5, rely=0.45, anchor=customtkinter.CENTER)
        
    def load_task_modify_menu(self, list_name: str = None, task_name: str = None):
        """
        Lodas the frame for modifying or creating a task.
        """
        self.tasks_frame.destroy()
        self.main.adjust_window_geometry()

        self.modify_task_frame = customtkinter.CTkFrame(
            self.list.main_frame,
            width=500, 
            height=400, 
            fg_color="#383736"
        )
        self.modify_task_frame.place(
            relx=0.5,
            rely=0.5, 
            anchor=customtkinter.CENTER
        )
        self.modify_task_frame.pack_propagate(False)

        print("TASK_NAME", task_name)
        result = self.get_task_data(task_name) if task_name else ({}, {}, None)
        print(result)
        if result is None:
            result = ({}, {}, None)
        _, task_data, task_id = result

        due_date = task_data and task_data['due_date']
        task_description = task_data and task_data['description']
        priority_level = task_data and task_data['priority']
        task_date, task_time = (
            (due_date and due_date['date'], due_date and due_date['time'])
            if due_date else (None, None) 
        )

        customtkinter.CTkLabel(
            self.modify_task_frame,
            text="EDIT TASK" if task_name else "CREATE TASK",
            font=self.main.get_font(size=25)
        ).pack(pady=10)

        def close_clicked(): 
            self.reload_tasks_frame(self.modify_task_frame)

        customtkinter.CTkButton(
            self.modify_task_frame, 
            text="X", 
            width=35, 
            corner_radius=0,
            font=self.main.get_font(size=22, bold=True), 
            fg_color="red", 
            hover_color="dark red",
            command=close_clicked
        ).place(relx=0.99, rely=0.06, anchor='e')

        self.main.seperator(self.modify_task_frame)

        placeholder_text_color = task_name and "black" or "grey"

        task_name_var = customtkinter.StringVar(value=task_name)
        task_description_var = customtkinter.StringVar(
            value=task_description if task_description else "Task Description"
        )

        print(task_name)

        self.task_name = customtkinter.CTkEntry(
            self.modify_task_frame, 
            corner_radius=0, 
            width=400,
            border_width=0, 
            fg_color="#D9D9D9", 
            text_color="black", 
            textvariable=task_name and task_name_var,
            placeholder_text=task_name or "Task Name",
            placeholder_text_color=placeholder_text_color,
            font=self.main.get_font(size=25, bold=True), 
            justify=customtkinter.CENTER
        )
        self.task_name.place(relx=0.5, rely=0.25, anchor=customtkinter.CENTER)

        self.task_description = customtkinter.CTkEntry(
            self.modify_task_frame, 
            corner_radius=0, 
            width=400,
            border_width=0, 
            fg_color="#D9D9D9", 
            text_color="black" if task_description else "grey",   
            textvariable=task_name and task_description_var,
            placeholder_text=task_description or "Task Description", 
            placeholder_text_color=placeholder_text_color,
            font=self.main.get_font(size=25, bold=True), 
            justify=customtkinter.CENTER
        )
        self.task_description.place(
            relx=0.5, 
            rely=0.35, 
            anchor=customtkinter.CENTER
        )

        priority_string_var = customtkinter.StringVar(
            value=str(priority_level) if priority_level else "1"
        )

        self.task_priority = customtkinter.CTkComboBox(
            self.modify_task_frame, 
            values=self.PRIORITY_LEVELS, 
            variable=priority_string_var, 
            corner_radius=0,
            width=150, 
            border_width=0, 
            fg_color="#D9D9D9", 
            text_color="black",
            font=self.main.get_font(size=25, bold=True)
        )
        self.task_priority.place(
            relx=0.25, 
            rely=0.45, 
            anchor=customtkinter.CENTER
        )

        customtkinter.CTkLabel(
            self.modify_task_frame, 
            width=50, 
            height=20, 
            fg_color="transparent", 
            bg_color="transparent", 
            text="Due Date", 
            text_color="white", 
            justify=customtkinter.LEFT
        ).place(relx=0.1, rely=0.5)

        self.task_date = customtkinter.CTkLabel(
            self.modify_task_frame, 
            width=75, 
            height=35, 
            fg_color="#D9D9D9", 
            text_color="black", 
            text=task_date or datetime.now().strftime("%d/%m/%Y")
        )
        self.task_date.place(relx=0.17, rely=0.6, anchor=customtkinter.CENTER)

        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M")
        self.valid_time = task_time or (
            f'{current_time.strftime("%I:%M")} ' +
            f'{datetime.strptime(formatted_time, "%H:%M").strftime("%p")}'
        )
        
        self.time = customtkinter.StringVar(value=self.valid_time)
        
        self.task_time = customtkinter.CTkEntry(
            self.modify_task_frame, 
            width=75, 
            height=35, 
            fg_color="#D9D9D9", 
            text_color="black", 
            textvariable=self.time, 
            corner_radius=0
        )
        self.task_time.place(relx=0.35, rely=0.6, anchor=customtkinter.CENTER)
        self.task_time.bind('<Return>', self.validate_time)

        self.calendar = customtkinter.CTkButton(
            self.modify_task_frame, 
            text="", 
            corner_radius=0,
            width=20, 
            image=self.CALENDAR_ICON,
            command=self.load_calendar
        )
        self.calendar.place(relx=0.475, rely=0.6, anchor=customtkinter.CENTER)

        customtkinter.CTkLabel(
            self.modify_task_frame,
            text="Please enter the time in following format:\n" +
                "Hour:Minute AM/PM (e.g., 08:30 AM or 02:15 PM)",
            text_color="grey", font=('Helvetica', 12, 'bold', 'italic'),
            justify=customtkinter.LEFT
        ).place(relx=0.37, rely=0.7, anchor=customtkinter.CENTER)

        def complete_clicked():
            self.task_complete_activated(task_id)

        customtkinter.CTkButton(
            self.modify_task_frame,
            text="SAVE" if task_name else "COMPLETE",
            text_color="white", 
            width=200, 
            font=self.main.get_font(),
            command=complete_clicked
        ).place(relx=0.5, rely=0.9, anchor=customtkinter.CENTER)

    def validate_time(self, event=None):
        """
        Validates the format of the time string.
        """
        time_str = self.time.get().upper()
        if "AM" in time_str or "PM" in time_str:
            try:
                formatted_time = datetime.strptime(
                    time_str, "%I:%M %p"
                ).strftime("%I:%M %p")
                self.valid_time = formatted_time
                self.time.set(value=formatted_time)
            except ValueError:
                self.time.set(value=self.valid_time)
        else:
            self.time.set(value=self.valid_time)

    def load_calendar(self):
        """
        Displays a calendar widget for selecting a due date.
        """
        def update_selected_date(event):
            self.task_date.configure(text=self.task_calendar.get_date())

        def destroy_calendar():
            self.task_calendar.destroy()
            self.close_calendar.destroy()

        if hasattr(self, 'task_calendar'):
            destroy_calendar()

        self.task_calendar = Calendar(
            self.modify_task_frame,
            selectmode='day',
            mindate=datetime.now(),
            showweeknumbers=False,
            cursor='hand2',
            date_pattern='dd/mm/y'
        )
        self.task_calendar.place(
            relx=0.5, 
            rely=0.5, 
            anchor=customtkinter.CENTER
        )
        self.task_calendar.bind('<<CalendarSelected>>', update_selected_date)

        self.close_calendar = customtkinter.CTkButton(
            self.modify_task_frame,
            text="Close Calendar",
            width=100,
            height=20,
            hover_color="red",
            command=destroy_calendar
        )
        self.close_calendar.place(
            relx=0.5, 
            rely=0.75, 
            anchor=customtkinter.CENTER
        )

    def create_task_template(self, task_data: dict):
        """
        Creates and displays a task item in the UI.
        """
        task_name = task_data['name']
        completed_check = customtkinter.IntVar(value=task_data['completed'])
        task_state = self.get_task_state(task_name)

        # Callback for handling task completion status change
        def task_completed():
            data, task_data, *other = self.get_task_data(task_name)
            task_data['completed'] = completed_check.get() == 1
            self.user_data.update(data)
            self.reload_tasks_frame(self.tasks_frame)

        # Task item container with rounded corners and padding
        task_item = customtkinter.CTkFrame(
            self.tasks_container,
            width=400,
            height=100,
            fg_color=STATE_COLOURS[task_state],
            corner_radius=15,
            border_color="gray",
            border_width=2
        )

        self.hidden_widgets.append([task_item, 8])
        task_item.pack_propagate(False)
        task_item.pack(pady=10)

        customtkinter.CTkLabel(
            task_item,
            text=task_name,
            font=self.main.get_font(family="Roboto", size=18, bold=True)
        ).place(relx=0.05, rely=0.2, anchor="w")

        customtkinter.CTkLabel(
            task_item,
            text=util.split_string(task_data['description'], 25),
            font=self.main.get_font(family="Roboto", size=14),
            wraplength=280,
            justify=customtkinter.LEFT
        ).place(relx=0.05, rely=0.45, anchor="w")

        date_obj = datetime.strptime(task_data['due_date']['date'], "%d/%m/%Y")
        customtkinter.CTkLabel(
            task_item,
            text=date_obj.strftime("%b %d"),
            font=self.main.get_font(family="Roboto", size=14, bold=True),
            text_color="#D3D3D3"
        ).place(relx=0.53, rely=0.19, anchor="center")

        def edit_clicked():
            self.load_task_modify_menu(task_name=task_name)

        customtkinter.CTkButton(
            task_item, 
            text="EDIT", 
            fg_color="#00BFFF",
            hover_color="#1E90FF", 
            text_color="white",
            corner_radius=5, 
            width=60, 
            height=25,
            command=edit_clicked
        ).place(relx=0.75, rely=0.2, anchor="center")

        def delete_clicked():
            self.task_delete_activated(task_name)

        customtkinter.CTkButton(
            task_item, text="", image=self.DELETE_ICON,
            fg_color="#FF5C5C", text_color="#CCCCCC", hover_color="#CC4949",
            corner_radius=5,  width=15, height=20,
            command=delete_clicked
        ).place(relx=0.92, rely=0.2, anchor="center")

        customtkinter.CTkCheckBox(
            task_item, text="",
            fg_color="gray", hover_color="green", corner_radius=5,
            width=10, variable=completed_check, command=task_completed
        ).place(relx=0.88, rely=0.75, anchor="w")

    def cleanup_task_timer(self, task_id: str):
        """
        Cleans up any timers or background processes within tasks.
        """
        timer = due_date_timers[task_id]
        if timer:
            timer.clean()

    def task_delete_activated(self, task_name: str):
        data, *_, task_id = self.get_task_data(task_name)
        list_data = data['lists'][self.list_name]

        list_data['tasks'].pop(task_id, None)
        self.user_data.update(data)

        self.reload_tasks_frame(self.tasks_frame)
        self.cleanup_task_timer(task_id)

    def load_saved_tasks(self, list_data):
        """
        Loads and displays all saved tasks from the list data.
        """
        prioritised_dict = {}

        for task_name, task_data in list_data['tasks'].items():
            if task_data['completed'] is True:
                continue

            priority = int(task_data['priority'])
            prioritised_dict.setdefault(priority, {})[task_name] = task_data

        self.hidden_widgets = []

        loading_label = customtkinter.CTkLabel(
            self.tasks_frame, text='',
            width=100, height=100,
            bg_color="transparent", fg_color="transparent",
            image=self.LOADING_ICON
        )
        loading_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
        pywinstyles.set_opacity(loading_label, color="#383736")

        loading = Loading(loading_label)
        loading.daemon = True
        loading.start()

        for level, data in sorted(prioritised_dict.items()):
            if not data:
                continue

            header = customtkinter.CTkLabel(
                self.tasks_container, width=400, height=20,
                text=f'LEVEL {level}',
                font=self.main.get_font(size=15, bold=True)
            )
            header.pack()

            separator = customtkinter.CTkFrame(
                self.tasks_container, width=400, height=2,
                fg_color="white"
            )
            separator.pack(pady=2)

            for task_name, task_data in data.items():
                self.create_task_template(task_data)

        self.load_completed_tasks()

        def load_widgets():
            self.tasks_container.place(
                relx=0.5, 
                rely=0.5, 
                anchor=customtkinter.CENTER
            )

            for widget in self.hidden_widgets:
                if isinstance(widget, list):
                    widget[0].pack(pady=widget[1])
                else:
                    widget.pack()

            loading.end_loading()

        threading.Timer(0.1 * len(list_data['tasks']), load_widgets).start()

    def load_completed_tasks(self):
        """
        Loads and displays all completed tasks from the list data.
        """
        completed_tasks = self.get_completed_tasks()

        if not completed_tasks:
            return

        header = customtkinter.CTkLabel(
            self.tasks_container, width=400, height=20,
            text='COMPLETED', 
            font=self.main.get_font(size=15, bold=True)
        )
        header.pack()

        separator = customtkinter.CTkFrame(
            self.tasks_container, width=400, height=2,
            fg_color="white"
        )
        separator.pack(pady=2)

        for task_data in completed_tasks.values():
            self.create_task_template(task_data)
        
    def reload_tasks_frame(self, current_displaying_frame):
        """
        Reloads the tasks frame, usually after modifying a task.
        """
        current_displaying_frame.destroy()
        self.load_tasks_frame()
        
    def display_task_status(
        self,
        status_error: str,
        msg: str = None,
        type: str = None,
        rely: int = 0.65
    ):
        """
        Displays status messages or errors to the user.
        """
        if hasattr(self, 'status_error') and self.status_error.winfo_exists():
            self.status_error.destroy()

        self.status_error = customtkinter.CTkLabel(
            self.modify_task_frame, 
            fg_color="transparent",
            text=constants.DisplayErrors[status_error].format(msg=msg, type=type),
            font=self.main.get_font()
        )
        self.status_error.place(
            relx=0.5, 
            rely=rely, 
            anchor=customtkinter.CENTER
        )

    def task_complete_activated(self, unique_id: str = None):
        """
        Displays error messages if invalid input as saves task to list
        data with a unique identifier.
        """
        self.validate_time()

        data = self.user_data.get()

        task_name = self.task_name.get()
        task_description = self.task_description.get()
        task_priority = self.task_priority.get()

        if len(task_name) == 0:
            self.display_task_status("App_InvalidTaskInput", rely=0.8)
            return

        if not check_name_length(task_name):
            self.display_task_status(
                "App_InvalidNameLength",
                msg="Task name",
                rely=0.8
            )
            return

        if not check_desc_length(task_description):
            self.display_task_status(
                "App_InvalidDescriptionLength",
                msg="Task description",
                rely=0.8
            )
            return

        if not is_valid(task_name):
            self.display_task_status(
                "App_InvalidInput",
                type="Name",
                rely=0.8
            )
            return

        list_data = data['lists'][self.list_name]
        has_data = bool(unique_id)

        if not unique_id:
            unique_id = util.generate_unique_id()
            timer = Timer(
                date=self.task_date.cget('text'),
                time=self.time.get(),
                name=task_name,
                fn=self.main.task_due_notification
            )
            timer.start()
            due_date_timers[unique_id] = timer

            if any(
                sub_dic.get('name').lower() == task_name.lower()
                for sub_dic in list_data['tasks'].values()
            ):
                self.display_task_status(
                    "App_InvalidName",
                    type="task",
                    msg=task_name,
                    rely=0.8
                )
                return
        else:
            timer = due_date_timers[unique_id]
            if not timer:
                return
            
            due_date = self.task_date.cget('text')
            due_time = self.time.get()
            timer.update_due_date(due_date, due_time)

        completed_state = (
            has_data and list_data['tasks'][unique_id]['completed']
        )

        list_data['tasks'][unique_id] = {
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

        self.user_data.update(data)
        self.reload_tasks_frame(self.modify_task_frame)

class List(customtkinter.CTkFrame):
    """
    A class that represents a list management UI within the app.
    """

    def __init__(self, master, data: dict, main, username: str):
        """
        Initialises the list frame and sets up timers for tasks based 
        on due daes.
        """
        super().__init__(master=master)
        self.master = master
        self.user_data = data
        self.username = username
        self.main = main

        data = self.user_data.get()
        for list_data in data['lists'].values():
            for task_id, task_data in list_data['tasks'].items():
                due_date = task_data['due_date']
                timer = Timer(
                    date=due_date['date'], 
                    time=due_date['time'],
                    name=task_data['name'], 
                    fn=self.main.task_due_notification
                )
                timer.start()
                due_date_timers[task_id] = timer

        self.load_list_menu()

    def load_list_menu(self):
        """
        Initialises and displays the main list menu frame.
        """
        self.main_frame = customtkinter.CTkFrame(
            self.master, 
            width=600, 
            height=500, 
            fg_color="transparent"
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
        self.main_frame.pack_propagate(False)

        self.load_list_frame()

    def load_list_frame(self):
        """
        Loads and displays the list frame with all user lists.
        """
        data = self.user_data.get()

        self.main.adjust_window_geometry()

        self.lists_frame = customtkinter.CTkFrame(
            self.main_frame, 
            width=500, 
            height=400, 
            fg_color="#383736"
        )
        self.lists_frame.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

        if  (
                not hasattr(self, 'welcome_label') 
                or not self.welcome_label.winfo_exists()
            ):
            self.welcome_label = customtkinter.CTkLabel(
                self.main_frame, 
                text=f'Welcome {self.username}', 
                font=customtkinter.CTkFont(
                    family="Arial", 
                    size=25, 
                    weight="normal"
                )
            )
            self.welcome_label.pack(pady=10)

        customtkinter.CTkButton(
            self.lists_frame,
            text="CREATE LIST",
            width=200,
            height=35,
            font=customtkinter.CTkFont(
                family="Arial", 
                size=15, 
                weight="bold"
            ), 
            command=self.load_create_list_menu
        ).place(relx=0.5, rely=0.9, anchor=customtkinter.CENTER)

        if data['lists']:
            self.lists_container = customtkinter.CTkScrollableFrame(
                self.lists_frame, 
                width=400, 
                height=290,
                scrollbar_button_color="#2d2c2c", 
                fg_color="transparent"
            )
            self.lists_container.place(
                relx=0.5, 
                rely=0.45, 
                anchor=customtkinter.CENTER
            )
            self.load_saved_lists(data)
        else:
            customtkinter.CTkLabel(
                self.lists_frame, 
                text="You have no lists \ncreate one to start setting tasks",
                font=self.main.get_font()
            ).place(relx=0.5, rely=0.45, anchor=customtkinter.CENTER)
            
    def reload_list_frame(self, current_displaying_frame):
        """
        Reloads the current list frame.
        """
        current_displaying_frame.destroy()
        self.load_list_frame()

    def load_create_list_menu(self):
        """
        Displays the menu for creating a new list.
        """
        self.lists_frame.destroy()
        self.welcome_label.destroy()

        self.main.adjust_window_geometry()

        self.create_list_frame = customtkinter.CTkFrame(
            self.main_frame, 
            width=500, 
            height=300, 
            fg_color="#383736"
        )
        self.create_list_frame.place(
            relx=0.5, 
            rely=0.5, 
            anchor=customtkinter.CENTER
        )
        self.create_list_frame.pack_propagate(False)

        customtkinter.CTkLabel(
            self.create_list_frame, 
            text="CREATE LIST",
            font=self.main.get_font(size=25)
        ).pack(pady=10)

        def close_clicked():
            self.reload_list_frame(self.create_list_frame)

        customtkinter.CTkButton(
            self.create_list_frame,
            text="X", 
            width=35, 
            corner_radius=0,
            font=self.main.get_font(size=22, bold=True),
            fg_color="red", 
            hover_color="dark red",
            command=close_clicked
        ).place(relx=0.99, rely=0.07, anchor='e')

        self.main.seperator(self.create_list_frame)

        create_list_name = customtkinter.CTkEntry(
            self.create_list_frame, 
            placeholder_text="NAME", 
            corner_radius=0,
            width=400, 
            border_width=0, 
            fg_color="#D9D9D9", 
            placeholder_text_color="black", 
            text_color="black",
            font=self.main.get_font(size=25, bold=True),
            justify=customtkinter.CENTER
        )
        create_list_name.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

        def complete_clicked():
            self.create_list_complete_activated(create_list_name.get())

        customtkinter.CTkButton(
            self.create_list_frame, 
            text="COMPLETE", 
            text_color="white", 
            width=200, 
            font=self.main.get_font(), 
            command=complete_clicked
        ).place(relx=0.5, rely=0.9, anchor=customtkinter.CENTER)

    def display_list_status(self, 
        status_error: str, 
        msg: str = None,
        type: str = None
    ):
        """
        Displays status messages or errors.
        """
        if hasattr(self, 'status_error') and self.status_error.winfo_exists():
            self.status_error.destroy()

        self.status_error = customtkinter.CTkLabel(
            self.create_list_frame, 
            text=constants.DisplayErrors[status_error].format(
                msg=msg, type=type
            ),
            font=self.main.get_font(), 
            fg_color="transparent"
        )
        self.status_error.place(
            relx=0.5, 
            rely=0.65, 
            anchor=customtkinter.CENTER
        )

    def create_list_complete_activated(self, list_name: str):
        """
        Handles the completion of list creation.
        """
        data = self.user_data.get()
        
        if not check_name_length(list_name):
            self.display_list_status("App_InvalidNameLength", msg="List")
            return
        
        if list_name.lower() in data['lists']:
            self.display_list_status(
                "App_InvalidName", 
                type="list", 
                msg=list_name
            )
            return
        
        data['lists'][list_name.lower()] = {
            'name': list_name,
            'tasks': {},
            'date_created': datetime.now()
        }
        self.user_data.update(data)
        self.reload_list_frame(self.create_list_frame)

    def get_unfinished_tasks_count(self, tasks) -> int:
        """
        Returns the count of unfinished tasks from the given task dictionary.
        """
        return Counter(
            task_data['completed'] for task_data in tasks.values()
        )[False]
    
    def load_saved_lists(self, data):
        """
        Loads and displays saved lists from the user data
        """
        for list_name, list_data in data['lists'].items():
            task = Task(
                master=self.master,
                data=self.user_data, 
                main=self.main,
                list=self, 
                list_name=list_name
            )

            list_item = customtkinter.CTkFrame(
                self.lists_container, 
                width=400, 
                height=100, 
                fg_color="#5c5b5a"
            )
            list_item.pack(pady=8)
            list_item.pack_propagate(False)

            customtkinter.CTkLabel(
                list_item, 
                text=list_data['name'],
                font=self.main.get_font(family="Roboto", size=17, bold=True)
            ).place(relx=0.02, rely=0.15, anchor="w")

            unfinished_tasks_count = (
                list_data['tasks'] 
                and self.get_unfinished_tasks_count(list_data['tasks'])
            )

            customtkinter.CTkLabel(
                list_item, 
                text=(
                    isinstance(unfinished_tasks_count, dict) 
                    and "You have no tasks" 
                    or (unfinished_tasks_count > 0 
                        and f'{unfinished_tasks_count} unfinished tasks' 
                        or 'All tasks completed'
                    )
                ), 
                font=self.main.get_font(size=16)
            ).place(relx=0.02, rely=0.85, anchor="w")

            customtkinter.CTkButton(
                list_item, 
                text="TASKS", 
                width=70, 
                height=20, 
                corner_radius=0,
                fg_color="#ECB528", 
                hover_color="#C8940F", 
                text_color="white", 
                command=task.load_tasks_frame,
                font=self.main.get_font(size=12, bold=True)
            ).place(relx=0.78, rely=0.15,anchor="e")

            def delete_clicked():
                self.list_delete_activated(list_name)

            customtkinter.CTkButton( 
                list_item,
                text="DELETE", 
                width=70, 
                height=20, 
                corner_radius=0,
                fg_color="#D74E4E", 
                hover_color="#A92727", 
                text_color="white", 
                command=delete_clicked,
                font=self.main.get_font(size=12, bold=True)
            ).place(relx=0.97, rely=0.15, anchor="e")

    def list_delete_activated(self, list_name: str):
        """
        Handles the deletion of a list.
        """
        data = self.user_data.get()
        data['lists'].pop(list_name, None)

        self.user_data.update(data)
        self.reload_list_frame(self.lists_frame)

class Notification(customtkinter.CTk):
    """
    A class to manage and display notifications to the user.
    """

    # Constants
    DISPLAY_TIME = 5

    def __init__(self, root):
        """
        Initalises the notification class.
        """
        super().__init__()
        self.root = root
        self.queue = Queue()
        self.is_displaying = False

        self.notification_frame = customtkinter.CTkFrame(
            root, 
            width=100, 
            height=50,
            bg_color="transparent", 
            fg_color="transparent"
        )
        self.notification_frame.pack(
            side=customtkinter.BOTTOM, 
            fill=customtkinter.X
        )

        self.notification_label = customtkinter.CTkLabel(
            self.notification_frame, 
            text="", 
            height=40, 
            font=('Helvetica', 20, 'bold')
        )
        self.notification_label.pack()

    def show_notification(self, message: str):
        """
        Adds a new notification to the queue and dispalys 
        it if no other nofication is currently showing
        """
        self.queue.put(message)
        if not self.is_displaying:
            self.display_next_notification()
    
    def display_next_notification(self):
        """
        Displays next notification in the queue.
        """
        if not self.queue.empty():
            self.is_displaying = True
            message = self.queue.get()

            self.notification_label.configure(text=message)
            self.notification_frame.after(
                self.DISPLAY_TIME * 1000, 
                self.hide_notification
            )

    def hide_notification(self):
        """
        Hides the current notification and displays the next one if available.
        """
        self.notification_label.configure(text="")
        self.is_displaying = False
        self.display_next_notification()

class App:
    """
    A class to manage the main app, 
    including UI elements and user interactions.
    """

    def __init__(self, main, username: str):
        """
        Initialises the app class.
        """
        super().__init__()
        self.main = main
        self.username = username
             
        # Runtime events
        self.notification_ready = threading.Event()

        self.user_data = Data(username)
        self.load_fonts()
        self.list = List(
            master=self.main.root, 
            main=self,
            data=self.user_data, 
            username=username
        )
        
        self.notification = Notification(self.main.root)
        self.notification_ready.set()

        customtkinter.CTkButton(
            self.main.root,
            text="FAQs",
            width=100, 
            height=25, 
            command=self.open_faqs
        ).place(relx=0.92, rely=0.88, anchor=customtkinter.CENTER)

        customtkinter.CTkButton(
            self.main.root, 
            text="Log out",
            width=100, 
            height=25, 
            command=self.logout
        ).place(relx=0.92, rely=0.95, anchor=customtkinter.CENTER)

    def open_faqs(self):
        """
        Opens the FAQs section, displaying information about 
        task colours and priorities.
        """
        self.main.save_current_state()

        # Reset window size so widgets of FAQs fit correctly
        self.adjust_window_geometry(extended=False)

        def load_state_colour_meaning():
            frame = customtkinter.CTkFrame(
                self.main.root,
                width=250, 
                height=350
            )
            frame.pack_propagate(False)
            frame.place(relx=0.37, rely=0.5, anchor=customtkinter.CENTER)

            colours = customtkinter.CTkFrame(
                frame,
                width=150,
                height=300,
                fg_color="transparent", 
                bg_color="transparent"
            )
            colours.place(relx=0.25, rely=0.55, anchor=customtkinter.CENTER)

            def create_color_state(index: int):
                customtkinter.CTkFrame(
                    colours,
                    width=20, 
                    height=20,
                    fg_color=STATE_COLOURS[index], 
                    bg_color=STATE_COLOURS[index]
                ).grid(row=index, pady=20, padx=10)

            info = customtkinter.CTkFrame(
                frame,
                width=150, 
                height=300,
            )
            info.place(relx=0.6, rely=0.55, anchor=customtkinter.CENTER)

            def create_color_state_info(index: int):
                customtkinter.CTkLabel(
                    info, 
                    text=util.split_string(COLOUR_STATE_INFOS[index], 15),
                    width=30, 
                    height=20
                ).grid(row=index, pady=10, padx=10)

            for i in range(len(STATE_COLOURS)):
                create_color_state(i)
                create_color_state_info(i)

            # Title
            customtkinter.CTkLabel(
                frame, 
                text="Task Background Colours",
                font=customtkinter.CTkFont(
                    family="Arial", 
                    size=20, 
                    weight="normal"
                )
            ).pack(pady=10)

            return frame

        def load_priority_meaning():
            frame = customtkinter.CTkFrame(
                self.main.root,
                width=200, 
                height=175
            )
            frame.pack_propagate(False)
            frame.place(relx=0.67, rely=0.325, anchor=customtkinter.CENTER)

            customtkinter.CTkLabel(
                frame,
                text=(
                    "The drop-down list in the\n"
                    "task creation is the priority\n"
                    "ordered by priority: higher\n"
                    "priority means the\n"
                    "task is less important."
                ),
                width=150, 
                height=150
            ).place(relx=0.5, rely=0.6, anchor=customtkinter.CENTER)

            # Title
            customtkinter.CTkLabel(
                frame, 
                text="Task Priority",
                font=customtkinter.CTkFont(
                    family="Arial", 
                    size=20, 
                    weight="normal"
                )
            ).pack(pady=10)

            return frame

        # Removes all displaying GUI from window
        self.main.hide_current_state()

        title = customtkinter.CTkLabel(
            self.main.root, 
            text="FAQs", 
            font=customtkinter.CTkFont(
                family="Arial", 
                size=25, 
                weight="normal"
            )
        )
        title.pack(pady=15)
        
        seperator = self.seperator(self.main.root)

        meaning_1 = load_state_colour_meaning()
        meaning_2 = load_priority_meaning()

        def back_fn():
            # Prevent from multiple function calls
            self.faq_back.destroy()
            title.destroy()
            seperator.destroy()
            meaning_1.destroy()
            meaning_2.destroy()

            # Restores the previous UI state
            self.main.restore_previous_state()

        self.faq_back = customtkinter.CTkButton(
            self.main.root,
            text="Back", 
            width=100, 
            height=30,
            command=back_fn
        )
        self.faq_back.place(relx=0.1, rely=0.95, anchor="w")

    def logout(self):
        """
        Logs out the current user and opens the login screen
        """
        # Importing login when logout is called to prevent circular imports
        from login import Login
        self.main.remove_current_state()
        Login(self.main)
        
    def task_due_notification(self, task_name: str):
        """
        Displays a notification when a task is due.
        """
        # waits for notification ready event to fire
        # calls show_nofication method to display GUI
        # that a task is due
        def notification_async():
            self.notification_ready.wait()
            self.notification.show_notification(f'"{task_name}" is due')
        
        threading.Thread(target=notification_async, daemon=True).start()

    def adjust_window_geometry(self, extended: bool = False):
        """
        Adjust the window size of the main app
        """
        self.main.adjust_window_geometry(extended)

    def get_font(self, family: str = None, size: int = 20, bold: bool = False):
        """
        Retrieves a font with applied properties.
        """
        return customtkinter.CTkFont(
            family=family or constants.BaseFont, 
            size=size, 
            weight=f'{bold and "bold" or "normal"}'
        )
    
    def seperator(self, master):
        """
        Creates and returns a seperator widget.
        """
        seperator = customtkinter.CTkFrame(
            master, 
            height=2, 
            width=450, 
            fg_color="white"
        )
        seperator.pack(padx=0.5, pady=0.15)
        return seperator

    def load_fonts(self):
        """
        Loads the default font for the app.
        """
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.actual()
