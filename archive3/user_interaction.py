import tkinter as tk
import pyttsx3
import pygame.mixer

pygame.mixer.init()
engine = pyttsx3.init()

def choose_set_abbreviation(possible_abbreviations):
    # Function to be called when a button is clicked
    def on_click(abbreviation):
        nonlocal chosen_abbreviation
        chosen_abbreviation = abbreviation
        root.destroy()

    chosen_abbreviation = None
    root = tk.Tk()
    root.title("Choose Set Abbreviation")

    for abbreviation in possible_abbreviations:
        btn = tk.Button(root, text=abbreviation, command=lambda abbr=abbreviation: on_click(abbr))
        btn.pack(pady=10)

    root.mainloop()
    return chosen_abbreviation

def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
