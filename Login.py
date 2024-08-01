import customtkinter
import keyring
import Constants
from App import App

# Default
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

service_id = "version_1"

class Login(customtkinter.CTk):
    LIGHT_RED_COLOUR = "#f54c4c"
    LIGHT_GREY_COLOUR = "#383837"
    DEFAULT_TEXT_COLOUR = ("black", "grey")
    DEFAULT_BORDER_COLOUR = "gray37"

    def __init__(self):
        super().__init__()
        
        self.title("Login")
        self.geometry(f"{Constants.WindowWidth}x{Constants.WindowHeight}")
        self.resizable(width=False, height=False)

        self.main_frame = customtkinter.CTkFrame(self, width=300, height=350)
        self.main_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)
        self.main_frame.pack_propagate(False)

        self.title_label = customtkinter.CTkLabel(self.main_frame, text="Login to Account", font=("",20))
        self.title_label.pack(pady=50)
        
        self.content_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.place(relx=0.5,rely=0.5,anchor=customtkinter.CENTER)

        self.load_login_menu()

    def display_status_error(self, status_error: str):
        if not status_error in Constants.DisplayErrors:
            raise Exception(f'No status error for {status_error}')    
        self.status_error = customtkinter.CTkLabel(self.main_frame, text=Constants.DisplayErrors[status_error], text_color=self.LIGHT_RED_COLOUR)
        self.status_error.after(2000, self.status_error.destroy)
        self.status_error.pack(pady=100)
    
    def display_auth_error(self, widget):
        widget.configure(placeholder_text_color=self.LIGHT_RED_COLOUR,border_color=self.LIGHT_RED_COLOUR)

    def reset_auth(self, widget):
        widget.configure(placeholder_text_color=self.DEFAULT_TEXT_COLOUR,border_color=self.DEFAULT_BORDER_COLOUR)

    def auth_login_credentials(self):
        username = self.login_username.get()
        password = self.login_password.get()
        if len(username) == 0 or len(password) == 0:
            self.display_auth_error(self.login_username)
            self.display_auth_error(self.login_password)
        else:
            if keyring.get_password(service_id, username) == password:
                App(username)
            else:
                self.display_auth_error(self.login_username)
                self.display_auth_error(self.login_password)

    def auth_account_credentials(self):
        username = self.account_username.get()
        password = self.account_password.get()
        if len(username) == 0 or len(password) < 8:
            self.display_auth_error(self.account_username)
            self.display_auth_error(self.account_password)
            if len(password) < 8:
                self.display_status_error('Login_InvalidPasswordLength')
        else:
            self.account_username.delete(0, customtkinter.END)
            self.account_password.delete(0, customtkinter.END)
            self.reset_auth(self.account_username)
            self.reset_auth(self.account_password)
            if keyring.get_password(service_id, username) != None:
                self.display_status_error('Login_InvalidUsername')
            else:
                keyring.set_password(service_id, username, password)
                App(username)
        
    def delete_current_page(self):
        [widget.destroy() for widget in self.content_frame.winfo_children()]
            
    def change_title_text(self, str):
        self.title_label.configure(text=str)

    def load_login_menu(self):
        self.delete_current_page()
        self.change_title_text('Login to Account')
        self.login_username = customtkinter.CTkEntry(self.content_frame,
            placeholder_text="Username",
            font=("Helvetica", 14),
        )
        self.login_username.pack(pady=10)
        self.login_password = customtkinter.CTkEntry(self.content_frame,
            placeholder_text="Password",
            font=("Helvetica", 14),
            show="*",                              
        )
        self.login_password.pack()
        login_submit = customtkinter.CTkButton(self.content_frame, text="Submit",
            command=self.auth_login_credentials).pack(pady=10)
        create_account = customtkinter.CTkButton(self.content_frame, hover_color=self.LIGHT_GREY_COLOUR, fg_color="transparent",
            text="Create Account", font=('',15,'underline'), command=self.load_create_account_menu).pack()

    def load_create_account_menu(self):
        self.delete_current_page()
        self.change_title_text('Create an Account')
        self.account_username = customtkinter.CTkEntry(self.content_frame,
            placeholder_text="Enter Username",
            font=("Helvetica", 14),                            
        )
        self.account_username.pack(pady=10)
        self.account_password = customtkinter.CTkEntry(self.content_frame,
            placeholder_text="Enter Password",
            font=("Helvetica", 14),
            show="*"       
        )
        self.account_password.pack()
        account_register = customtkinter.CTkButton(self.content_frame, text="Register", 
            command=self.auth_account_credentials).pack(pady=10)
        login_account = customtkinter.CTkButton(self.content_frame, hover_color=self.LIGHT_GREY_COLOUR, fg_color="transparent", 
            text="Login Account", font=('',15,'underline'), command=self.load_login_menu).pack()
        
if __name__ == "__main__":
    login = Login()
    login.mainloop()