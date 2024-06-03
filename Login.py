import customtkinter
import pickle
import keyring
from tkinter import font
from PIL import ImageTk, Image
try:
    import tkFont
except ModuleNotFoundError:
    import tkinter.font as tkFont

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

service_id = "version_1"


print("Jacob is cute")

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

class Login(customtkinter.CTk):
    LIGHT_RED_COLOUR = "#f54c4c"
    LIGHT_GREY_COLOUR = "#383837"
    DEFAULT_TEXT_COLOUR = ("black", "grey") #not default
    DEFAULT_BORDER_COLOUR = ("#979DA2", "#949A9F") #not default
    
    #Images
    #SHOW_PASSWORD_IMAGE = ImageTk.PhotoImage(Image.open('C:\Downloads\Icon'))

    def __init__(self):
        super().__init__()  
        self.app = App()
        self.app.load()
        self._loaded_login_page = False
        self._loaded_create_account_page = False
        self.display_password_toggle_widget()

    def display_login_invalidation(self):
        app = self.app.get()
        app.invalid_label = customtkinter.CTkLabel(app.login_frame, text="Invalid username or password", text_color=self.LIGHT_RED_COLOUR)
        app.invalid_label.after(2000, app.invalid_label.destroy)
        app.invalid_label.pack()
    
    def display_account_exist(self):
        app = self.app.get()
        app.account_exist_label = customtkinter.CTkLabel(app.login_frame, text="Username already exist", text_color=self.LIGHT_RED_COLOUR)
        app.account_exist_label.after(2000, app.account_exist_label.destroy)
        app.account_exist_label.pack()

    def display_entry_widget_error(self, widget):
        widget.configure(placeholder_text_color=self.LIGHT_RED_COLOUR,border_color=self.LIGHT_RED_COLOUR)

    def display_entry_widget_normal(self, widget):
        widget.configure(placeholder_text_color=self.DEFAULT_TEXT_COLOUR,border_color=self.DEFAULT_BORDER_COLOUR)

    def toggle_password(self):
        app = self.app.get()
        app.toggle_password.configure(text=app.toggle_password.cget('text')=='Show Password'
                                      and 'Hide Password' or 'Show Password')
        if self._loaded_login_page:
            if app.login_password_entry.cget('show') == '':
                app.login_password_entry.configure(show='*')
            else:
                app.login_password_entry.configure(show='')
        else:
            if app.acc_password_entry.cget('show') == '':
                app.acc_password_entry.configure(show='*')
            else:
                app.acc_password_entry.configure(show='')

    def auth_login(self):
        app = self.app.get()
        username = app.login_username_entry.get()
        password = app.login_password_entry.get()
        if len(username) == 0 or len(password) == 0:
            self.display_entry_widget_error(app.login_username_entry)
            self.display_entry_widget_error(app.login_password_entry)
           # self.display_login_invalidation()
        else:
            if keyring.get_password(service_id, username) == password:
                app.login_frame.destroy()
                self.app.username = username
                self.app.load_app_menu()
            else:
                self.display_entry_widget_error(app.login_username_entry)
                self.display_entry_widget_error(app.login_password_entry)
               # self.display_login_invalidation()

    def auth_create_acc(self):
        app = self.app.get()
        username = app.acc_username_entry.get()
        password = app.acc_password_entry.get()
        if len(username) == 0 or len(password) == 0:
            self.display_entry_widget_error(app.acc_username_entry)
            self.display_entry_widget_error(app.acc_password_entry)
           # self.display_login_invalidation()
        else:
            app.acc_username_entry.delete(0, customtkinter.END)
            app.acc_password_entry.delete(0, customtkinter.END)
            self.display_entry_widget_normal(app.acc_username_entry)
            self.display_entry_widget_normal(app.acc_password_entry)
            if keyring.get_password(service_id, username) != None:
                self.display_account_exist()
            else:
                keyring.set_password(service_id, username, password)
        
    def delete_current_page(self):
        app = self.app.get()
        if self._loaded_login_page:
            app.login_username_entry.destroy()
            app.login_password_entry.destroy()
            app.login_submit_button.destroy()
            app.create_account_button.destroy()
            self._loaded_login_page = False
        elif self._loaded_create_account_page:
            app.acc_username_entry.destroy()
            app.acc_password_entry.destroy()
            app.acc_register_button.destroy()
            app.login_button.destroy()
            self._loaded_create_account_page = False
            
    def change_title_text(self, str):
        app = self.app.get()
        app.title_label.configure(text=str)

    def create_login_menu(self):
        self.delete_current_page()
        self.change_title_text('Login to Account')
        self._loaded_login_page = True
        app = self.app.get()
        app.login_username_entry = customtkinter.CTkEntry(app.content_frame,
            placeholder_text="Username",
            font=("Helvetica", 14),
        )
        app.login_password_entry = customtkinter.CTkEntry(app.content_frame,
            placeholder_text="Password",
            font=("Helvetica", 14),
            show="*",                              
        )
        app.login_submit_button = customtkinter.CTkButton(app.content_frame, text="Submit", command=self.auth_login)
        app.create_account_button = customtkinter.CTkButton(app.content_frame, hover_color=self.LIGHT_GREY_COLOUR, fg_color="transparent", text="Create Account", font=('',15,'underline'), command=self.create_account_creation_menu)
        app.login_username_entry.pack(pady=10)
        app.login_password_entry.pack()
        app.login_submit_button.pack(pady=10)
        app.create_account_button.pack()

        app.mainloop()

    def create_account_creation_menu(self):
        self.delete_current_page()
        self.change_title_text('Create an Account')
        self._loaded_create_account_page = True
        app = self.app.get()
        app.acc_username_entry = customtkinter.CTkEntry(app.content_frame,
            placeholder_text="Enter Username",
            font=("Helvetica", 14),                            
        )
        app.acc_password_entry = customtkinter.CTkEntry(app.content_frame,
            placeholder_text="Enter Password",
            font=("Helvetica", 14),
            show="*"                                     
        )
        app.acc_register_button = customtkinter.CTkButton(app.content_frame, text="Submit", command=self.auth_create_acc)
        app.login_button = customtkinter.CTkButton(app.content_frame, hover_color=self.LIGHT_GREY_COLOUR, fg_color="transparent", text="Login Account", font=('',15,'underline'), command=self.create_login_menu)
        app.acc_username_entry.pack(pady=10)
        app.acc_password_entry.pack()
        app.acc_register_button.pack(pady=10)
        app.login_button.pack()

    def display_password_toggle_widget(self):
        app = self.app.get()
        app.toggle_password = customtkinter.CTkButton(app.content_frame, text='Show Password', command=self.toggle_password)
        app.toggle_password.pack()

class App(customtkinter.CTk):
    WIDTH = 700
    HEIGHT = 500

    def __init__(self):
        super().__init__()

    def load(self):
        self.title("app")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        self.login_frame = customtkinter.CTkFrame(self, width=300, height=350)
        self.login_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.login_frame.pack_propagate(False)
        self.title_label = customtkinter.CTkLabel(self.login_frame, text="Login to Account", font=("",20))
        self.title_label.pack(pady=50)
        self.content_frame = customtkinter.CTkFrame(self.login_frame, fg_color="transparent")
        self.content_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)

    def get(self):
        return self
        
    def load_app_menu(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2,3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.actual()

        self.username_label = customtkinter.CTkLabel(self.sidebar_frame, text="Welcome "+self.username, font=customtkinter.CTkFont(family=self.default_font, size=18, weight="normal"))
        self.username_label.grid(row=1, column=0)

        self.task_title = customtkinter.CTkLabel(self.sidebar_frame, text="Tasks", font=customtkinter.CTkFont(family=self.default_font, size = 15, weight="normal"))
        self.task_title.grid(row=2, column=0, pady=20)
        self.task_container = customtkinter.CTkScrollableFrame(self.sidebar_frame, width=120)
        self.task_container.grid(row=3, column=0)

        self.change_appearance_button = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark"],
                                                                    command=self.change_appearance_mode_event)
        self.change_appearance_button.grid(row=6, column=0, padx=20, pady=(10, 10))


        self.change_appearance_button.set("Dark")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def load_saved_tasks(self):
        print("Loading tasks")

if __name__ == "__main__":
    login = Login()
    login.create_login_menu()
