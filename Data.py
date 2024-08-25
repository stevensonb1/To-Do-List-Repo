import pickle
import os

class Data():
    """
    A class to handle user data storage and retrieval using pickle
    for serialization.
    """
    DATA_FOLDER = 'Userdata'

    def __init__(self, username: str):
        """
        Initialises the data instance with a username and ensures the 
        data folder exists.
        """
        self.username = username
        self._ensure_data_folder_exists()
    
    def _ensure_data_folder_exists(self):
        """
        Creates the data folder if it does not arleady exist.
        """
        if not os.path.exists(self.DATA_FOLDER):
            os.makedirs(self.DATA_FOLDER)

    def _get_file_path(self):
        """
        Constructs the file path for the user's data file.
        """
        return os.path.join(self.DATA_FOLDER, f'{self.username}_data.pkl')

    def template(self):
        """
        Provides a template for the data structure
        """
        return {
            'lists': {}
        }

    def get(self):
        if self.load() is None:
            self.save(self.template())
        return self.load()

    def update(self, data):
        self.save(data)

    def save(self, object):
        with open(self._get_file_path(), "wb") as file:
            pickle.dump(object, file)
    
    def load(self):
        try:
            with open(self._get_file_path(), "rb") as file:
                loaded_data = pickle.load(file)
                return loaded_data
        except FileNotFoundError:
            print(f'{self.username}_data.pkl does not exist. No data found.')
            return None
