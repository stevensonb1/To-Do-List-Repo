import pickle

class Data():
    def __init__(self, data):
        self.data = data
    
    def save_data(filename: str, obj):
        try:
            with open(filename, "wb") as f:
                pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as err:
            print("Error while saving data to file:", filename, "[ERROR:]", err)

    def load_data(filename: str):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except Exception as err:
            print("Error while loading data from file:", filename, "[ERROR]:", err)
