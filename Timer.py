import threading
from datetime import datetime
import time
import random

class Timer(threading.Thread):
    def __init__(self, date: str = None, time: str = None, name: str = None, fn = None):
        super().__init__()
        self.due_date = date
        self.due_time = time
        self.name = name
        self.func = fn

    def run(self):
        due_datetime = datetime.strptime(f'{self.due_date} {self.due_time}', "%d/%m/%Y %I:%M %p")

        current_datetime = datetime.now()
        time_remaining = (due_datetime - current_datetime).total_seconds()

        if time_remaining > 0:
            time.sleep(time_remaining)
        self.func(self.name)