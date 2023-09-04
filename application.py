import tkinter as tk
from tkinter import ttk, Label, Button, Text
import cv2
from PIL import Image, ImageTk
import threading

# Importing the necessary functions from the provided scripts
from camera import capture_card_from_webcam

class CardScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window title and size
        self.title("Card Scanner App")
        self.geometry("800x600")

        # Capture Card Button
        self.capture_btn = Button(self, text="Capture Card", command=self.capture_card)
        self.capture_btn.pack(pady=20)

        # Image display label
        self.image_label = Label(self)
        self.image_label.pack(pady=20)

        # Card details display
        self.card_details = Text(self, height=10, width=50)
        self.card_details.pack(pady=20)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Welcome to Card Scanner App!")
        self.status_bar = Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def capture_card(self):
        # Capture the card using the webcam (this function will be threaded to avoid freezing the GUI)
        threading.Thread(target=self._threaded_capture).start()

    def _threaded_capture(self):
        card_image = capture_card_from_webcam()
        if card_image is not None:
            # Display the captured image in the GUI
            self.update_image_display(card_image)
        else:
            self.status_var.set("Failed to capture card image.")

    def update_image_display(self, card_image):
        # Convert the OpenCV image to a format suitable for Tkinter
        image = Image.fromarray(cv2.cvtColor(card_image, cv2.COLOR_BGR2RGB))
        image = image.resize((400, 300), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(image=image)
        self.image_label.config(image=self.photo)

# Run the application
app = CardScannerApp()
app.mainloop()
