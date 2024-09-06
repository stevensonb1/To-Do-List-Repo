"""
This module provides the "Loading" class to handle a loading animation using
a rotating image. The animation runs in a separate thread to avoid blocking the
main GUI thread.

Imports:
- Image (from PIL): For image processing and manipulation.
- customtkinter: For custom Tkinter widgets.
- tkinter: For Tkinter base functionalities.
- threading: For creating and managing threads.
- time: For handling time-related operations.

Classes:
- Loading: A thread-based class that manages a rotating loading animation.

Attributes:
- SPEED (int): Rotation speed of the loading animation.

Methods:
- __init__(self, label): Initializes the Loading animation with a label.
- rotate_image(self, image, angle: int): Rotates the provided image by the given angle.
- update_image(self, angle: int): Updates the label with the rotated image.
- end_loading(self): Stops the loading animation and destroys the label.
- run(self): Runs the animation loop in a separate thread.

Author: Blake Stevenson
Date: 2024-09-06
Version: 1.0
License: MIT
"""

from PIL import Image
import customtkinter
import threading
import time


light_image = Image.open("images/loading.png")
dark_image = Image.open("images/loading.png")

my_image = customtkinter.CTkImage(
    light_image=light_image,
    dark_image=dark_image,
    size=(50, 50)
)


class Loading(threading.Thread):
    """
    Handles the animation of a rotating image displayed in a Tkinter label.
    Runs the animation in a separate thread to keep the GUI responsive.
    """

    # Constants
    SPEED = 3

    def __init__(self, label):
        """
        Initializes the Loading animation with a label.
        """
        super().__init__()
        self.label = label
        self.is_active = True

    def rotate_image(self, image, angle: int):
        """
        Rotates the provided image by the given angle.
        """
        rotated_image = image.rotate(angle, expand=True)
        return customtkinter.CTkImage(
            light_image=rotated_image,
            dark_image=rotated_image,
            size=(100, 100)
        )
    
    def update_image(self, angle: int):
        """
        Updates the label with the rotated image.
        """
        if not self.is_active:
            return
        rotated_image = self.rotate_image(light_image, angle)
        self.label.configure(image=rotated_image)
        self.label.image = rotated_image

    def end_loading(self):
        """
        Stops the loading animation and destroys the label.
        """
        self.is_active = False
        self.label.destroy()

    def run(self):
        """
        Runs the animation loop in a separate thread.
        Rotates the image and updates the label at regular intervals.
        """
        angle = 0
        while self.is_active:
            self.update_image(angle)
            angle += 10
            if angle >= 360:
                angle = 0
            time.sleep(0.1 / self.SPEED)
