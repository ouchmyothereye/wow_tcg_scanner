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
import threading
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


# Set up the tkinter window for logging
root = tk.Tk()
root.title("Card Scan Log")
text_widget = tk.Text(root, wrap=tk.WORD)
text_widget.pack(expand=True, fill=tk.BOTH)

def log_to_gui(message):
    text_widget.insert(tk.END, message + '\n')
    text_widget.see(tk.END)

# This function will be called to update the tkinter window
def log_message(message):
    logging.info(message)
    log_to_gui(message)

# Run the tkinter main loop in a separate thread
def run_tk_root():
    root.mainloop()

threading.Thread(target=run_tk_root).start()

# Load Google Cloud Vision credentials from environment variables
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_google_cloud_credentials.json"
client = vision.ImageAnnotatorClient()

import tkinter as tk
import threading

import tkinter as tk
import threading
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

    cursor.execute(f"SELECT COUNT(*) FROM collection_inventory WHERE card_id = ? AND variant_id = ? AND instance = ?", (card_id, variant_id, instance))
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



def query_database(texts):
    logging.info("Connecting to the 'wow_cards' SQLite database.")
    conn = sqlite3.connect('wow_cards.db')
    cursor = conn.cursor()

    # Step 4: Query wow_cards for card_name
    lines_from_text = texts[0].split('\n')

    matched_abbreviation = None
    card_name = None
    set_id = None

    for potential_card_name in lines_from_text:
        logging.info(f"Querying 'wow_cards' for potential card name: {potential_card_name}")
        cursor.execute("SELECT DISTINCT set_id FROM wow_cards WHERE card_name=?", (potential_card_name,))
        result = cursor.fetchall()
        if result:
            card_name = potential_card_name
            # If card name is unique, directly use the set_id
            if len(result) == 1:
                set_id = result[0][0]
                logging.info(f"Card name is unique. Set ID for {card_name}: {set_id}")
                break
            else:
                # If card name is not unique, continue with previous method to identify set abbreviation
                cursor.execute("SELECT DISTINCT set_abbreviation FROM card_versions WHERE card_name=?", (potential_card_name,))
                result = cursor.fetchall()
                set_abbreviations = [row[0] for row in result]
                logging.info(f"Possible set abbreviations for {card_name}: {set_abbreviations}")
                # Do not directly call get_set_abbreviation here; we will call it outside the loop
            break

    # If card_name is found but abbreviation is not matched, ask for it
    if card_name and not set_id:
        matched_abbreviation = get_set_abbreviation(texts, set_abbreviations)
        if matched_abbreviation:
            logging.info(f"Matched set abbreviation: {matched_abbreviation}")
            # Extract set_id based on matched abbreviation
            logging.info(f"Querying 'sets' for set abbreviation: {matched_abbreviation}")
            cursor.execute("SELECT card_versions.set_id, card_versions.block_name, card_versions.set_abbreviation FROM card_versions WHERE card_versions.set_abbreviation=?", (matched_abbreviation,))
            results = cursor.fetchall()


            cursor.execute("""
                SELECT card_versions.set_id, card_versions.block_name, card_versions.set_abbreviation 
                FROM card_versions 
                WHERE card_versions.card_name=? AND card_versions.set_abbreviation=?
            """, (card_name, matched_abbreviation,))

            specific_results = cursor.fetchall()

            if len(specific_results) == 1:
                set_id = specific_results[0][0]
                logging.info(f"Single Set ID {set_id} found for card name {card_name} and abbreviation {matched_abbreviation}.")
            else:
                options = list(set([f"{row[2]}/{row[1]}" for row in results]))  # Forming unique "set abbreviation / block_name" options
                chosen_option = choose_set_block_name(options)
                chosen_set_abbreviation, chosen_block_name = chosen_option.split("/")
                for row in specific_results:
                    if row[1] == chosen_block_name and row[2] == chosen_set_abbreviation:
                        set_id = row[0]
                        break
                logging.info(f"User selected Set ID {set_id} associated with block name {chosen_block_name} and set abbreviation {chosen_set_abbreviation}.")

                logging.info(f"Set ID found: {set_id}")

    if not card_name or not set_id:
        logging.error("Failed to identify the card or its set. Exiting.")
        return

    # Step 6: Identify card_id
    logging.info(f"Querying 'card_versions' for card name: {card_name} and set ID: {set_id}")
    cursor.execute("SELECT card_id FROM card_versions WHERE card_name=? AND set_id=?", (card_name, set_id))
    card_id = cursor.fetchone()
    if card_id:
        card_id = card_id[0]
        logging.info(f"Card ID found: {card_id}")
    else:
        logging.error(f"No card ID found for card name: {card_name} and set ID: {set_id}")
        return

    # Step 7: Determine variant_id
    logging.info(f"Querying 'possible_card_variants' for card ID: {card_id}")
    cursor.execute("SELECT variant_id, instance FROM possible_card_variants WHERE card_id=?", (card_id,))
    variants = cursor.fetchall()
    if not variants:
        logging.error(f"No variants found for card ID: {card_id}")
        return

    if len(variants) == 1 and variants[0][0] == 5:
        variant_id, instance = variants[0]
        logging.info(f"Only one variant with ID 5 found. Variant ID: {variant_id}, Instance: {instance}")
    else:
        unique_variant_ids = list(set([v[0] for v in variants]))
        logging.warning(f"Multiple variants found for card ID {card_id}: {unique_variant_ids}")
        variant_id = None
        while variant_id not in unique_variant_ids:
            variant_id = int(input(f"Please select a variant ID from {unique_variant_ids}: "))
        instance = next(v[1] for v in variants if v[0] == variant_id)
    
    if check_existing_card(card_id, variant_id, instance):
        play_audio('old_match.mp3')
        speak(f"{card_name}")
    else:
        play_audio('new_match.mp3')
        speak(f"{card_name}")
    #conn.close()



    
    # Step 8: Insert into collection_inventory
    current_date = datetime.now()
    log_message(f"Inserting into 'collection_inventory'. Card Name:{card_name}, Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Scan Date: {current_date}")
    cursor.execute("INSERT INTO collection_inventory (card_id, variant_id, instance, scan_date) VALUES (?, ?, ?, ?)", 
                    (card_id, variant_id, instance, current_date))
    conn.commit()

    log_message(f"Insertion successful. Card Name:{card_name}, Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Date: {current_date}")

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