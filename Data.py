import pickle

class Data():
    def __init__(self, username: str):
        self.username = username

    def save(self, object):
        with open(f'{self.username}_data.pkl', "wb") as file:
            pickle.dump(object, file)
    
    def load(self):
        try:
            with open(f'{self.username}_data.pkl', "rb") as file:
                loaded_data = pickle.load(file)
                return loaded_data
        except FileNotFoundError:
            print(f'{self.username}_data.pkl does not exist. No data found.')