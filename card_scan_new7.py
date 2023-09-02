import cv2
import os
import logging
from google.cloud import vision
from google.cloud import vision_v1 as vision
import sqlite3
from datetime import datetime
from difflib import get_close_matches
#import fuzzywuzzy as fuzz
from fuzzywuzzy import fuzz
import pygame.mixer
import pyttsx3
import tkinter as tk
from tkinter import simpledialog
import keyboard
from tkinter import messagebox




class SuppressComtypesLogs(logging.Filter):
    def filter(self, record):
        return 'comtypes.client._events' not in record.msg

# Initialize pygame mixer
pygame.mixer.init()
pygame.display.init()


# Set up logging
logging.basicConfig(filename='program.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
logger = logging.getLogger()
logger.addFilter(SuppressComtypesLogs())
logging.getLogger('comtypes').setLevel(logging.CRITICAL)

# Load Google Cloud Vision credentials from environment variables
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_google_cloud_credentials.json"
client = vision.ImageAnnotatorClient()

import tkinter as tk

import tkinter as tk
from tkinter import messagebox

def mark_card_as_ignored():
    success = update_ignore_flag()
    if success:
        messagebox.showinfo("Success", "Last card marked as ignored!")
    else:
        messagebox.showerror("Error", "Failed to mark the card as ignored!")

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

def check_existing_card(card_id, variant_id, instance):
    conn = sqlite3.connect('wow_cards.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM collection_inventory WHERE ignore = 0 and card_id = ? AND variant_id = ? AND instance = ?", (card_id, variant_id, instance))
    count = cursor.fetchone()[0]

    logging.info(f"Checked existing card with card_id: {card_id}, variant_id: {variant_id}, instance: {instance}. Count found: {count}")

    conn.close()

    return count > 0

def update_ignore_flag():
    logging.info("Attempting to update the 'ignore' flag for the last inserted card.")
    conn = sqlite3.connect('wow_cards.db')
    cursor = conn.cursor()
    
    # Get the row with the latest timestamp
    cursor.execute("SELECT MAX(scan_date) FROM collection_inventory")
    latest_timestamp = cursor.fetchone()[0]
    
    if latest_timestamp:
        # Update the 'ignore' column for the row with the latest timestamp
        cursor.execute("UPDATE collection_inventory SET ignore=1 WHERE scan_date=?", (latest_timestamp,))
        conn.commit()
        logging.info(f"Updated 'ignore' flag for card with timestamp {latest_timestamp}.")
    else:
        logging.error("No recent cards found in the collection_inventory table.")
    
    conn.close()




def capture_image():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        cv2.imshow('Press NumPad Enter to Capture or q to Quit', frame)
        
        key = cv2.waitKey(1)
        if key == 13:  # NumPad Enter Key
            img_name = "captured_img.jpg"
            cv2.imwrite(img_name, frame)
            logging.info(f"Image captured and saved as {img_name}")
            break
        elif key == ord('q'):
            logging.info("Exiting program")
            cap.release()
            cv2.destroyAllWindows()
            exit()

    cap.release()
    cv2.destroyAllWindows()
    return img_name

def clean_text(text):
    return ''.join(e for e in text if e.isalnum() or e.isspace()).lower()


def send_to_gcv(image_path):
    logging.info(f"Attempting to send image {image_path} to Google Cloud Vision.")

    # Ensure the file exists
    if not os.path.exists(image_path):
        logging.error(f"Image file {image_path} not found.")
        return []

    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    
    try:
        response = client.text_detection(image=image)
    except Exception as e:
        logging.error(f"Error occurred while sending image to Google Cloud Vision: {e}")
        return []

    # Check for errors in the response
    if response.error.message:
        logging.error(f"Google Cloud Vision API returned an error: {response.error.message}")
        return []

    texts = response.text_annotations

    if texts:
        logging.info(f"Texts found in the image: {[text.description for text in texts]}")
        return [text.description for text in texts]
    else:
        logging.warning("No text found in the image.")
        return []

def get_set_abbreviation(texts, possible_abbreviations):
    cleaned_texts = clean_text(texts)
    logging.info(f"Cleaned text for abbreviation matching: {cleaned_texts}")

    # Convert multi-word abbreviations to a consistent format.
    formatted_abbreviations = [abbr.replace(" ", "").lower() for abbr in possible_abbreviations]

    # First, attempt exact matching.
    for index, abbreviation in enumerate(formatted_abbreviations):
        logging.info(f"Checking for abbreviation: {abbreviation}")
        if abbreviation in cleaned_texts:
            logging.info(f"Matched set abbreviation: {possible_abbreviations[index]}")
            return possible_abbreviations[index]

    # If exact matching failed, attempt fuzzy matching.
    for index, abbreviation in enumerate(formatted_abbreviations):
        score = fuzz.token_set_ratio(cleaned_texts, abbreviation)
        logging.info(f"Fuzzy match score for {abbreviation}: {score}")
        if score > 85:  # You can adjust this threshold as needed.
            logging.info(f"Matched set abbreviation using fuzzy matching: {possible_abbreviations[index]}")
            return possible_abbreviations[index]

    # If both exact and fuzzy matching failed, prompt the user.
    while True:
        chosen_abbreviation = choose_set_abbreviation(possible_abbreviations)

        if chosen_abbreviation in possible_abbreviations:
            return chosen_abbreviation
        else:
            print(f"{chosen_abbreviation} is not a valid abbreviation. Please try again.")

def choose_set_block_name(possible_block_names):
    # Function to be called when a button is clicked
    def on_click(block_name):
        nonlocal chosen_block_name
        chosen_block_name = block_name
        root.destroy()

    chosen_block_name = None
    root = tk.Tk()
    root.title("Choose Block Name")

    for block_name in possible_block_names:
        btn = tk.Button(root, text=block_name, command=lambda bn=block_name: on_click(bn))
        btn.pack(pady=10)

    root.mainloop()
    return chosen_block_name



# Splitting the 'query_database' function into smaller functions

# 1. Database Connection
def connect_to_database():
    logging.info("Connecting to the 'wow_cards' SQLite database.")
    conn = sqlite3.connect('wow_cards.db')
    cursor = conn.cursor()
    return conn, cursor

# 2. Query Card Name
# Modified 'query_card_name' to always return three values

def query_card_name(cursor, texts):
    lines_from_text = texts[0].split('\n')
    for potential_card_name in lines_from_text:
        logging.info(f"Querying 'wow_cards' for potential card name: {potential_card_name}")
        cursor.execute("SELECT DISTINCT set_id FROM wow_cards WHERE card_name=?", (potential_card_name,))
        result = cursor.fetchall()
        if result:
            card_name = potential_card_name
            if len(result) == 1:  # Card name is unique
                set_id = result[0][0]
                return card_name, set_id, None
            else:
                cursor.execute("SELECT DISTINCT set_abbreviation FROM card_versions WHERE card_name=?", (potential_card_name,))
                result = cursor.fetchall()
                set_abbreviations = [row[0] for row in result]
                return card_name, None, set_abbreviations
    return None, None, None


# 4. Query Card ID
def query_card_id(cursor, card_name, matched_abbreviation):
    cursor.execute("SELECT card_id FROM card_versions WHERE card_name=? AND set_abbreviation=?", (card_name, matched_abbreviation))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

# 5. Handle Variants
def handle_variants(cursor, card_id):
    cursor.execute("SELECT variant_id, instance FROM possible_card_variants WHERE card_id=?", (card_id,))
    variants = cursor.fetchall()
    if len(variants) == 1 and variants[0][0] == 5:
        variant_id, instance = variants[0]
        return variant_id, instance
    else:
        unique_variant_ids = list(set([v[0] for v in variants]))
        variant_id = None
        while variant_id not in unique_variant_ids:
            variant_id = int(input(f"Please select a variant ID from {unique_variant_ids}: "))
        instance = next(v[1] for v in variants if v[0] == variant_id)
        return variant_id, instance

# 6. Insert into Collection Inventory
def insert_into_inventory(cursor, conn, card_id, variant_id, instance, card_name):
    current_date = datetime.now()
    logging.info(f"Inserting into 'collection_inventory'. Card Name:{card_name}, Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Scan Date: {current_date}")
    cursor.execute("INSERT INTO collection_inventory (card_id, variant_id, instance, scan_date) VALUES (?, ?, ?, ?)", 
                   (card_id, variant_id, instance, current_date))
    conn.commit()
    logging.info(f"Insertion successful. Card Name: {card_name}, Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Date: {current_date}")

# Updated 'query_database' function
# Incorporating the missed section into the 'query_database' function

# Modifying the 'query_database' function to handle 'matched_abbreviation' initialization

def query_database(texts):
    conn, cursor = connect_to_database()
    
    # Query card name
    card_name, set_id, set_abbreviations = query_card_name(cursor, texts)
    
    matched_abbreviation = None
    # If card name is found but set_id is not matched, get set abbreviation
    if card_name and not set_id:
        matched_abbreviation = get_set_abbreviation(texts, set_abbreviations)
        if matched_abbreviation:
            set_id = query_card_id(cursor, card_name, matched_abbreviation)
    
    # Query card ID
    card_id = query_card_id(cursor, card_name, matched_abbreviation)
    
    # Handle variants
    variant_id, instance = handle_variants(cursor, card_id)
    
    # Insert into collection inventory
    insert_into_inventory(cursor, conn, card_id, variant_id, instance, card_name)
    
    # Check if the card already exists and play appropriate audio
    if check_existing_card(card_id, variant_id, instance):
        play_audio('old_match.mp3')
        speak(f"{card_name}")
    else:
        play_audio('new_match.mp3')
        speak(f"{card_name}")

    conn.close()


# Note: The 'get_set_abbreviation' and 'check_existing_card' functions are assumed to exist elsewhere in the script.


# Note: The 'get_set_abbreviation' function is assumed to exist elsewhere in the script.



    # Step 8: Insert into collection_inventory
    current_date = datetime.now()
    logging.info(f"Inserting into 'collection_inventory'. Card Name:{card_name}, Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Scan Date: {current_date}")
    cursor.execute("INSERT INTO collection_inventory (card_id, variant_id, instance, scan_date) VALUES (?, ?, ?, ?)", 
                    (card_id, variant_id, instance, current_date))
    conn.commit()

    logging.info(f"Insertion successful. Card Name: {card_name}, Set ID: {set_id}, Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Date: {current_date}")
    # Check if this is a new card or an existing one

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    while True:
        logging.info("Starting the card scanning process.")
        
        # Capture image
        capture_image()
        
        # Extract text from image using Google Cloud Vision
        extracted_texts = send_to_gcv("captured_img.jpg")
        
        if extracted_texts:
            query_database(extracted_texts)
