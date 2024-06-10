import customtkinter
import keyring
from App import App

# Default configuration
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

service_id = "version_1"

class Login(customtkinter.CTk):
    LIGHT_RED_COLOUR = "#f54c4c"
    LIGHT_GREY_COLOUR = "#383837"
    DEFAULT_TEXT_COLOUR = ("black", "grey") #not default
    DEFAULT_BORDER_COLOUR = ("#979DA2", "#949A9F") #not default

    WIDTH = 700
    HEIGHT = 500

    def __init__(self):
        super().__init__()
        
        self.title("app")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        self.login_frame = customtkinter.CTkFrame(self, width=300, height=350)
        self.login_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.login_frame.pack_propagate(False)
        self.title_label = customtkinter.CTkLabel(self.login_frame, text="Login to Account", font=("",20))
        self.title_label.pack(pady=50)
        self.content_frame = customtkinter.CTkFrame(self.login_frame, fg_color="transparent")
        self.content_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)

        self._loaded_login_page = False
        self._loaded_create_account_page = False
        self.load_login_menu()
        self.display_password_toggle_widget()

    def display_login_invalidation(self):
        self.invalid_label = customtkinter.CTkLabel(self.login_frame, text="Invalid username or password", text_color=self.LIGHT_RED_COLOUR)
        self.invalid_label.after(2000, self.invalid_label.destroy)
        self.invalid_label.pack()
    
    def display_account_exist(self):
        self.account_exist_label = customtkinter.CTkLabel(self.login_frame, text="Username already exist", text_color=self.LIGHT_RED_COLOUR)
        self.account_exist_label.after(2000, self.account_exist_label.destroy)
        self.account_exist_label.pack()

    def display_entry_widget_error(self, widget):
        widget.configure(placeholder_text_color=self.LIGHT_RED_COLOUR,border_color=self.LIGHT_RED_COLOUR)

    def display_entry_widget_normal(self, widget):
        widget.configure(placeholder_text_color=self.DEFAULT_TEXT_COLOUR,border_color=self.DEFAULT_BORDER_COLOUR)

    def toggle_password(self):
        self.toggle_password.configure(text=self.toggle_password.cget('text')=='Show Password'
                                      and 'Hide Password' or 'Show Password')
        if self._loaded_login_page:
            if self.login_password_entry.cget('show') == '':
                self.login_password_entry.configure(show='*')
            else:
                self.login_password_entry.configure(show='')
        else:
            if self.acc_password_entry.cget('show') == '':
                self.acc_password_entry.configure(show='*')
            else:
                self.acc_password_entry.configure(show='')

    def auth_login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()
        if len(username) == 0 or len(password) == 0:
            self.display_entry_widget_error(self.login_username_entry)
            self.display_entry_widget_error(self.login_password_entry)
           # self.display_login_invalidation()
        else:
            if keyring.get_password(service_id, username) == password:
                self.login_frame.destroy()
                App(username).load_app_menu()
            else:
                self.display_entry_widget_error(self.login_username_entry)
                self.display_entry_widget_error(self.login_password_entry)
               # self.display_login_invalidation()

    def auth_create_acc(self):
        username = self.acc_username_entry.get()
        password = self.acc_password_entry.get()
        if len(username) == 0 or len(password) == 0:
            self.display_entry_widget_error(self.acc_username_entry)
            self.display_entry_widget_error(self.acc_password_entry)
           # self.display_login_invalidation()
        else:
            self.acc_username_entry.delete(0, customtkinter.END)
            self.acc_password_entry.delete(0, customtkinter.END)
            self.display_entry_widget_normal(self.acc_username_entry)
            self.display_entry_widget_normal(self.acc_password_entry)
            if keyring.get_password(service_id, username) != None:
                self.display_account_exist()
            else:
                keyring.set_password(service_id, username, password)
        
    def delete_current_page(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            self._loaded_login_page = False
            self._loaded_create_account_page = False
            
    def change_title_text(self, str):
        self.title_label.configure(text=str)

    def load_login_menu(self):
        self.delete_current_page()
        self.change_title_text('Login to Account')
        self._loaded_login_page = True
        self.login_username_entry = customtkinter.CTkEntry(self.content_frame,
            placeholder_text="Username",
            font=("Helvetica", 14),
        )
        self.login_password_entry = customtkinter.CTkEntry(self.content_frame,
            placeholder_text="Password",
            font=("Helvetica", 14),
            show="*",                              
        )
        self.login_submit_button = customtkinter.CTkButton(self.content_frame, text="Submit", command=self.auth_login)
        self.create_account_button = customtkinter.CTkButton(self.content_frame, hover_color=self.LIGHT_GREY_COLOUR, fg_color="transparent", text="Create Account", font=('',15,'underline'), command=self.load_account_creation_menu)
        self.login_username_entry.pack(pady=10)
        self.login_password_entry.pack()
        self.login_submit_button.pack(pady=10)
        self.create_account_button.pack()

    def load_account_creation_menu(self):
        self.delete_current_page()
        self.change_title_text('Create an Account')
        self._loaded_create_account_page = True
        self.acc_username_entry = customtkinter.CTkEntry(self.content_frame,
            placeholder_text="Enter Username",
            font=("Helvetica", 14),                            
        )
        self.acc_password_entry = customtkinter.CTkEntry(self.content_frame,
            placeholder_text="Enter Password",
            font=("Helvetica", 14),
            show="*"                                     
        )
        self.acc_register_button = customtkinter.CTkButton(self.content_frame, text="Submit", command=self.auth_create_acc)
        self.login_button = customtkinter.CTkButton(self.content_frame, hover_color=self.LIGHT_GREY_COLOUR, fg_color="transparent", text="Login Account", font=('',15,'underline'), command=self.load_login_menu)
        self.acc_username_entry.pack(pady=10)
        self.acc_password_entry.pack()
        self.acc_register_button.pack(pady=10)
        self.login_button.pack()

    def display_password_toggle_widget(self):
        self.toggle_password = customtkinter.CTkButton(self.content_frame, text='Show Password', command=self.toggle_password)
        self.toggle_password.pack()

if __name__ == "__main__":
    login = Login()
    login.mainloop()