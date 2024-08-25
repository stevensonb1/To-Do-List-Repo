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
    """
    The loading class represents a loading animation using an image
    that rotates. It runs in a seperate thread to avoid blocking
    the main GUI thread.
    """

    # Constants
    SPEED = 3

    def __init__(self, label):
        """
        Initialises the loading thread.
        """
        super().__init__()
        self.label = label
        self.is_active = True

    def rotate_image(self, image, angle: int):
        """
        Rotates the given image by the specified angle.
        """
        rotated_image = image.rotate(angle, expand=True)
        return customtkinter.CTkImage(light_image=rotated_image, 
            dark_image=rotated_image, size=(100, 100))
    
    def update_image(self, angle: int):
        """
        Updates the image dispalyed on the label with a rotated version
        """
        if not self.is_active:
            return
        
        rotated_image = self.rotate_image(light_image, angle)

        self.label.after(0, self._update_image, rotated_image)

    def _update_image(self, rotated_image):
        """
        Updates the labels image with the new rotated image.
        This method is called from the GUI thread using after for thread safety
        """
        if self.label.winfo_exists():
            self.label.configure(image=rotated_image)
            self.label.image = rotated_image

    def end_loading(self):
        """
        Stops the loading animation and destroys the label wdiget.
        """
        self.is_active = False
        self.label.destroy()

    def run(self):
        """
        Starts the loading animation by continuously updating the image with
        icremental rotations. Runs in a seperate thread.
        """
        angle = 0
        while self.is_active:
            self.update_image(angle)
            angle += 10
            if angle >= 360:
                angle = 0
            time.sleep(0.1/self.SPEED)
