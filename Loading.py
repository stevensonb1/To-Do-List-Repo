from PIL import Image
import customtkinter, tkinter, threading, time

light_image = Image.open("images/loading.png")
dark_image = Image.open("images/loading.png")

my_image = customtkinter.CTkImage(
    light_image=light_image,
    dark_image=dark_image,
    size=(50, 50)
)

SPEED = 3

def rotate_image(image, angle):
    rotated_image = image.rotate(angle, expand=True)
    return customtkinter.CTkImage(light_image=rotated_image, 
        dark_image=rotated_image, size=(100, 100))

def update_image(label, angle):
    rotated_image = rotate_image(light_image, angle)
    label.configure(image=rotated_image)
    label.image = rotated_image

def load_async(label):
    angle = 0
    while True:
        update_image(label, angle)
        angle += 10
        if angle >= 360:
           angle = 0
        time.sleep(0.1/SPEED)

def load_gif(label):
   thread = threading.Thread(target=load_async, args=(label,))
   thread.daemon = True
   thread.start()