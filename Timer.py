import threading
from datetime import datetime
import time

class Timer(threading.Thread):
    """
    A timer class thats runs on a countdown to a specified due date and time.
    It can execute a callback function when the tiemr reaches the due date.
    """
    def __init__(self, 
        date: str = None, 
        time: str = None, 
        name: str = None, 
        fn = None
    ):
        """
        Initialises the timer instance.
        """
        super().__init__()
        self.due_date = date
        self.due_time = time
        self.name = name
        self.func = fn
        self._stop_event = threading.Event()

    def update_due_date(self, date: str, time: str):
        """
        Updates the due date and time for the timer.
        """
        self.due_date = date
        self.due_time = time

    def clean(self):
        """
        Stops the timer and terminates the thread.
        """
        self._stop_event.set()

    def check(self):
        """
        Recursively checks the time remaining until the due date and time.
        Executes the callback function if the timer expires.
        """
        due_datetime = datetime.strptime(
            f'{self.due_date} {self.due_time}', "%d/%m/%Y %I:%M %p")

        while not self._stop_event.is_set():
            current_datetime = datetime.now()
            time_remaining = (due_datetime - current_datetime).total_seconds()

            if time_remaining > 0:
                time.sleep(1) # Prevents crashing
                self.check()
            else:
                if self.func:
                    self.func(self.name)
                break

    def run(self):
       """
       Starts the timer by calling the check method.
       """
       self.check()
