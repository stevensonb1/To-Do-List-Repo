import pickle

class Data():
    def __init__(self, username: str):
        self.username = username

    def template(self):
        return {
            'lists': {}
        }

    def get(self):
        if self.load() == None:
            self.save(self.template())
        return self.load()

    def update(self, data):
        self.save(data)

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