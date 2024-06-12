import pickle

class Data():
    def __init__(self, username: str):
        if username != None:
            print(f'Initialized data class for user: {username}')
            self.save_data(f'userdata/{username}', self.__create_empty_object())
            self.__update_data(username)

    def __create_empty_object(self):
        return {
            "list_count": 1
        }
    
    def __update_data(self, username: str):
        self.data = self.load_data(f'userdata/{username}')
        print(self.data)
    
    def __get__(self):
        return self.data
    
    def __merge_changes(self, changes):
        pass
    
    def save_data(self, filename: str, obj):
        try:
            with open(filename, "wb") as f:
                pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as err:
            print("Error while saving data to file:", filename, "[ERROR:]", err)

    def load_data(self, filename: str):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except Exception as err:
            print("Error while loading data from file:", filename, "[ERROR]:", err)