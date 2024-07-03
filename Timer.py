import threading

'''
t = threading.Thread(target=func, args=(1,2))
t.run # Runs function
t.start # Runs function on different thread
'''

class Timer(threading.Thread):
    def __init__(self):
        super().__init__()

    def start_timer(self):
