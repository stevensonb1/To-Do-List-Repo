from PIL import Image
import customtkinter, tkinter, threading, time

light_image = Image.open("images/loading.png")
dark_image = Image.open("images/loading.png")

my_image = customtkinter.CTkImage(
    light_image=light_image,
    dark_image=dark_image,
    size=(50, 50)
)

class Loading(threading.Thread):
    # Constants
    SPEED = 3

    def __init__(self, label):
        super().__init__()
        self.label = label
        self.is_active = True

    def rotate_image(self, image, angle: int):
        rotated_image = image.rotate(angle, expand=True)
        return customtkinter.CTkImage(light_image=rotated_image, 
            dark_image=rotated_image, size=(100, 100))
    
    def update_image(self, angle: int):
        if not self.is_active:
            return
        rotated_image = self.rotate_image(light_image, angle)
        self.label.configure(image=rotated_image)
        self.label.image = rotated_image

    def end_loading(self):
        self.is_active = False
        self.label.destroy()

    def run(self):
        angle = 0
        while self.is_active:
            self.update_image(angle)
            angle += 10
            if angle >= 360:
                angle = 0
            time.sleep(0.1/self.SPEED)