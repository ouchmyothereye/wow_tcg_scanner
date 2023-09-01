
# Content from audio_feedback.py
""" The audio_feedback.py file focuses on providing audio feedback based on the results of card recognition. Here's a breakdown:

Imports and TODO Comments:

The pygame library is imported to handle audio playback.
There's a TODO comment suggesting enhancements to the audio feedback, such as more specific cues, different sounds for various errors, and voice feedback with card names.
Initialization and Sound Paths:

The pygame mixer, responsible for playing sounds, is initialized.
Paths to different audio feedback files are defined:
NO_MATCH_SOUND: Sound played when no match is found.
OLD_MATCH_SOUND: Sound played when a card is recognized but already exists in the log.
NEW_MATCH_SOUND: Sound played when a new card is recognized and added to the log.
Function: play_sound(sound_path):

Takes a path to an audio file as input.
Loads the audio file using pygame and plays it.
The function waits for the sound to finish before returning. """

# TODO: Enhance audio feedback to provide more specific cues.
# Suggestions: Different sounds for different errors, voice feedback with card name, etc.

import pygame
from gtts import gTTS
import tempfile

# Initialize pygame mixer
pygame.mixer.init()

# Paths to audio files
NO_MATCH_SOUND = "no_match.mp3"
OLD_MATCH_SOUND = "old_match.mp3"
NEW_MATCH_SOUND = "new_match.mp3"

def play_sound(sound_path):
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def speak_text(text):
    """
    Convert text to speech and play it.
    """
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(fp.name + ".mp3")
        play_sound(fp.name + ".mp3")


# Content from camera.py
""" The camera.py file provides functionality related to capturing images using a webcam. Here's a summary:

Import:

The OpenCV library (cv2) is imported.
Function: capture_card_from_webcam():

Initiates a webcam feed using OpenCV.
Displays the live webcam feed in a window titled 'Card Scanner'.
The user is instructed to position the card in view and press the 'c' key to capture the image. Pressing the 'q' key exits the webcam feed.
If the 'c' key (represented by the ASCII code 13) is pressed, the webcam is released, the display window is destroyed, and the current frame (image of the card) is returned.
If the 'q' key is pressed or there's an error in capturing a frame, the webcam feed is terminated, and the display window is destroyed.
This module provides a straightforward way to interact with a webcam and capture images of trading cards. """

import cv2

def capture_card_from_webcam():
    """
    Captures an image of a card from the webcam feed when the 'c' key is pressed.
    """
    cap = cv2.VideoCapture(0)
    print("Opening webcam. Position the card and press 'c' to capture. Press 'q' to exit.")
    
    while True:
        ret, frame = cap.read()
        
        if frame is None or frame.shape[0] == 0 or frame.shape[1] == 0:
            print("Error: Failed to retrieve frame from webcam.")
            break
            
        cv2.imshow('Card Scanner', frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 13:
            cap.release()
            cv2.destroyAllWindows()
            return frame

        if key == ord('q'):
            break

        if key == ord('z'):
            cap.release()
            cv2.destroyAllWindows()
            return 'BACKOUT_LAST_ENTRY'

    cap.release()
    cv2.destroyAllWindows()

# Content from card_logging.py
""" The card_logging.py file deals with the logging and retrieval of card data. Here's a breakdown:

Imports and TODO Comments:

Essential libraries like os, csv, and json are imported.
There are TODO comments suggesting the integration of a database system for scalability.
Function: get_script_directory():

Returns the directory in which the script is located.
Function: get_card_session():

Manages sessions for card logging.
If a session file doesn't exist, it creates one and initializes the session to 1.
If a session file exists, it reads the last session number, increments it, and returns the new session number.
Function: get_card_data_from_json(card_name, card_set_and_number=None):

Retrieves card data from the cards.json file using the card's name.
If a single card matches the name, it returns that card.
If multiple cards match the name and set/number information is provided, it refines the search and returns the matching card.
Function: update_card_log(card_name, card_number, set_block_raid, session):

Updates the card log (card_log.csv) with the given card details.
Checks if the card already exists in the log:
If it does, the quantity is incremented.
If it doesn't, a new entry for the card is added.
Returns True if a new entry is added, and False otherwise.
From the provided content, the module primarily focuses on managing sessions, retrieving card data from a JSON file, and logging card details in a CSV file.
 """
# TODO: Integrate with a database system for scalability.
# Suggestions: Use SQLite for a lightweight database or consider more robust systems like PostgreSQL for larger collections.

import os
import csv
import json

def get_script_directory():
    return os.path.dirname(os.path.realpath(__file__))

def get_card_session():
    session_file_path = os.path.join(get_script_directory(), 'session.csv')
    if not os.path.exists(session_file_path):
        with open(session_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Session'])
            writer.writerow([1])
            return 1
    else:
        with open(session_file_path, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            current_session = int(rows[-1][0])
        with open(session_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Session'])
            for i in range(current_session):
                writer.writerow([i + 1])
            writer.writerow([current_session + 1])
            return current_session + 1

def get_card_data_from_json(card_name, card_set_and_number=None):
    """Retrieve card data from the cards.json file using the card's name."""
    conn = sqlite3.connect("/mnt/data/wow_cards.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM card_versions")
    all_cards = cursor.fetchall()
    data = dict(all_cards)
    matching_cards = [card for card in data if card['name'].lower() == card_name.lower()]

        # If only one card matches the name, return it
    if len(matching_cards) == 1:
            return matching_cards[0]
        # If multiple cards match the name and set/number info is provided, refine the search
    elif len(matching_cards) > 1 and card_set_and_number:
            for card in matching_cards:
                if card.get('set') and card_set_and_number in card['set']:
                    return card
    return None
     

def update_card_log(card_name, card_number, set_block_raid, session):
    card_exists = False
    new_entry = False
    updated_rows = []
    card_identifier = f"{card_name}|{set_block_raid}"

    print(f"Attempting to update log for {card_name} from {set_block_raid}.")  # Debugging statement



    cursor.execute("SELECT * FROM collection_inventory")
    card_log = cursor.fetchall()
            
    for row in reader:
            print(f"Comparing log entry '{row['Card Name']}' to extracted '{card_name}'")
           # if row['Card Name'] == card_name and row['Set/Block/Raid'] == set_block_raid:
            if row['Card Name'].strip().lower() == card_name.strip().lower() and row['Set/Block/Raid'].strip().lower() == set_block_raid.strip().lower():

        #for row in reader:
         #   if card_name == row["Card Name"] and set_block_raid == row["Set/Block/Raid"]:
        # ... (rest of the code for updating the existing entry)

                print(f"Card {card_name} exists in the log. Updating quantity.")  # Debugging statement
                card_exists = True
                row['Quantity'] = str(int(row['Quantity']) + 1)
            updated_rows.append(row)

    if not card_exists:
        print(f"Card {card_name} is new. Adding to the log.")  # Debugging statement
        new_entry = True
    card_id = "placeholder"
    variant_id = "placeholder"
    instance = "placeholder"
    updated_rows.append({
            'Session': session,
            'Card Name': card_name,
            'Card Number': card_number,
            'Set/Block/Raid': set_block_raid,
            'Quantity': '1'
        })

    import datetime
    scan_date = datetime.datetime.now()
    cursor.execute("INSERT INTO collection_inventory (card_id, variant_id, instance, scan_date) VALUES (?, ?, ?, ?)", (card_id, variant_id, instance, scan_date))
    conn.commit()
    fieldnames = ['Session', 'Card Name', 'Card Number', 'Set/Block/Raid', 'Quantity']
        
    writer.writeheader()
    for row in updated_rows:
        writer.writerow(row)

    return new_entry

def back_out_last_entry():
    cursor.execute("SELECT * FROM collection_inventory")
    card_log = cursor.fetchall()
        
    rows = list(reader)

    # If there are no entries, return
    if not rows:
        return

    last_entry = rows[-1]

    # If the quantity of the last entry is more than 1, just decrement the quantity
    if int(last_entry['Quantity']) > 1:
        last_entry['Quantity'] = str(int(last_entry['Quantity']) - 1)
    # If the quantity is 1, remove the entire entry
    else:
        rows.pop()

    # Write the modified data back to the CSV
    cursor.execute("INSERT INTO collection_inventory (card_id, variant_id, instance, scan_date) VALUES (?, ?, ?, ?)", (card_id, variant_id, instance, scan_date))
    conn.commit()
    fieldnames = ['Session', 'Card Name', 'Card Number', 'Set/Block/Raid', 'Quantity']
        
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

# Content from vision.py
""" The vision.py file focuses on extracting text from the images of trading cards using Google Cloud Vision. Here's a brief summary:

Imports and Initialization:

Essential libraries such as os, cv2, and google.cloud are imported.
The Google Cloud Vision client is initialized.
Function: extract_text_from_image(image_path):

This function takes the path of an image as an input and returns the card's name and its set and number information.
The image is read using OpenCV.
The top part of the image (330x65 pixels from the top) is cropped.
The bottom part of the image (360x45 pixels from the bottom) is cropped.
The two cropped areas are combined vertically into a single image.
This combined image is saved temporarily as "combined_cropped.jpg".
Google Cloud Vision is used to detect text from the combined image.
The extracted text is split into lines.
The card's name is assumed to be in the first block, and any blocks starting with a number are ignored.
The set information of the card is assumed to be in the second block.
The function returns the card name, the card set and number, and the extracted lines of text. """


# TODO: Implement preprocessing steps for captured images to enhance recognition accuracy.
# Suggestions: Convert to grayscale, apply Gaussian blur, use edge detection, etc.
# Integrate with online card databases to fetch card details if not found in local JSON.
# This can provide a fallback mechanism when local data is incomplete or outdated.


import os
import cv2
# from google.cloud.vision import types
from google.cloud import vision_v1 as vision

# Initialize Cloud Vision client
client = vision.ImageAnnotatorClient()

def extract_text_from_image(image_path):
        # Read the image
    image = cv2.imread(image_path)
    
    # Crop the top part (330x65 starting from the top)
    top_crop = image[:65, :]
    
    # Crop the bottom part (360x45 starting from the bottom)
    height, _, _ = image.shape
    bottom_crop = image[height-45:, :]
    
    # Combine the two cropped areas into a single image
    combined_image = cv2.vconcat([top_crop, bottom_crop])
    combined_image_path = "combined_cropped.jpg"
    cv2.imwrite(combined_image_path, combined_image)

    with open(combined_image_path, 'rb') as image_file:
        content = image_file.read()
    combined_vision_image = vision.Image(content=content)
    response = client.text_detection(image=combined_vision_image)
    lines = response.text_annotations[0].description.strip().split('\n')
        # Filter out single-letter blocks from GCV response
    filtered_lines = [line for line in lines if len(line.strip()) > 1]
    
    # Extract card name from the first remaining block
    card_name = filtered_lines[0]

    # We'll assume the card name is in the first block, and ignore blocks starting with a number
    # card_name = lines[1] if lines[0][0].isdigit() else lines[0]
    
    # Assuming the set information is in the second block
    card_set_and_number = lines[1] if card_name == lines[0] else lines[2]
    
    return card_name, card_set_and_number, lines

# Content from main.py
""" The main.py file seems to be the primary script that integrates all the functionalities of the card scanning system. Here's an overview:

Imports and TODO Comments:

The file starts with a few TODO comments suggesting improvements.
Essential libraries and functions from other modules (camera.py, card_logging.py, vision.py, and audio_feedback.py) are imported.
Function: get_best_match_from_json(extracted_name, card_data):

This function takes the extracted card name and a list of card data (from a JSON file).
It then attempts to find the best match from the list using fuzzy string matching.
If no satisfactory match is found using the threshold, it retries without the threshold.
It returns the card data for the best match.
Function: get_best_match_from_json_v2(extracted_name, card_data):

An improved version of the previous function.
It sets a threshold for fuzzy matching and searches for a match within the threshold.
Extracted names and card names are converted to lowercase and whitespace is stripped before comparison.
Function: main():

The primary execution function of the script.
Initializes a session for card logging and retrieves the existing card data from a JSON file.
Captures an image of a card from a webcam.
Extracts text from the captured image.
Tries to match the extracted text with card data from the JSON file.
Updates the card log, displays card details, and plays appropriate audio feedback based on the match.
Handles exceptions and provides audio feedback for errors.
Main Execution:

If the script is run as the main program, the main() function is executed. """

# TODO: Implement batch processing to allow multiple cards to be scanned in quick succession.
# Consider having a buffer time between scans or a UI element indicating readiness for the next scan.
# Develop a user-friendly interface for the card scanning system.
# Consider using libraries like PyQt or Tkinter for the UI.
# Consider further modularization if the script grows in complexity.
# Breaking functionalities into separate modules aids maintenance and readability.



import os
import json
import cv2
import traceback
from camera import capture_card_from_webcam
from card_logging import get_script_directory, get_card_session, update_card_log
from vision import extract_text_from_image
from audio_feedback import play_sound, speak_text, NO_MATCH_SOUND, OLD_MATCH_SOUND, NEW_MATCH_SOUND
from card_logging import get_card_session, get_card_data_from_json, update_card_log, back_out_last_entry
from camera import capture_card_from_webcam
from fuzzywuzzy import fuzz

def get_best_match_from_json(extracted_name, card_data):
    best_match = None
    highest_score = 0
    
    for card in card_data:
        current_score = fuzz.ratio(extracted_name, card["name"])
        if current_score > highest_score:
            highest_score = current_score
            best_match = card

    
    if not best_match:  # If no match found with threshold, retry without threshold
        for card in card_data:
            card_name = card["name"].strip().lower()
            current_score = fuzz.ratio(extracted_name, card_name)
            if current_score > highest_score:
                highest_score = current_score
                best_match = card

    return best_match


def get_best_match_from_json_v2(extracted_name, card_data):
    best_match = None
    highest_score = 0
    threshold = 85  # Setting a threshold for fuzzy matching
    
    # Convert the extracted name to lowercase and strip whitespace
    extracted_name = extracted_name.strip().lower()
    
    for card in card_data:
        card_name = card["name"].strip().lower()
        current_score = fuzz.ratio(extracted_name, card_name)
        print(f"Comparing '{extracted_name}' to '{card_name}'. Score: {current_score}")

        if current_score > highest_score and current_score >= threshold:
            highest_score = current_score
            best_match = card

    
    if not best_match:  # If no match found with threshold, retry without threshold
        for card in card_data:
            card_name = card["name"].strip().lower()
            current_score = fuzz.ratio(extracted_name, card_name)
            print(f"Comparing '{extracted_name}' to '{card_name}' without threshold. Score: {current_score}")
            
            if current_score > highest_score:
                highest_score = current_score
                best_match = card

    return best_match

# Load card data from JSON
with open(os.path.join(get_script_directory(), 'cards.json'), 'r') as file:
    CARDS_DATA = dict(all_cards)

##def get_best_match_from_json_v2(card_name):
##    for card in CARDS_DATA:
  ##      if card['name'] == card_name:
   ##         return card
 ##   return None

conn = sqlite3.connect("/mnt/data/wow_cards.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM card_versions")
all_cards = cursor.fetchall()
cards_data = dict(all_cards)


def main():
    try:
      #  print("Opening webcam. Position the card and wait for auto-capture. Press 'q' to exit.")
        session = get_card_session()

        while True:
            # Capture the card using the new auto-capture method
            card_image = capture_card_from_webcam()

            if isinstance(card_image, str) and card_image == 'BACKOUT_LAST_ENTRY':
                back_out_last_entry()
                speak_text("Reverted last entry.")
                continue  # Or continue with whatever logic you prefer

            if card_image is None:  # Exit if 'q' was pressed or if there was an issue
                break

            # Save the captured card image to a file
            captured_image_path = "captured_card.jpg"
            cv2.imwrite(captured_image_path, card_image)

            try:
                card_name, card_set_and_number, _ = extract_text_from_image(captured_image_path)
                # Filter out single-letter blocks from GCV response
           #     filtered_blocks = [block for block in lines if len(block['description'].strip()) > 1]

                # Extract card name from the first remaining block
           #     card_name = filtered_blocks[0]['description'].strip()

                print(f"Extracted Card Name: {card_name}")
                card_data = get_best_match_from_json_v2(card_name, cards_data)
                if not card_data:
                    print(f"No match found in JSON data for card name: {card_name}")

                if card_data:
                    card_info = card_data.get('set') or card_data.get('block') or card_data.get('raid') or "Unknown"
                    display_line = f"Card Name: {card_name} | Card Number: {card_data['num']} | Set/Block/Raid: {card_info}"
                    new_entry = update_card_log(card_data['name'], card_data['num'], card_data['set'], session)

                    
                    if new_entry:
                        print(f"Logging Card: {card_name} from {card_info}")
                        print({display_line}) 
                        play_sound(NEW_MATCH_SOUND)
                        speak_text(card_name)

                    else:
                        print(f"Logging Card: {card_name} from {card_info}")
                        play_sound(OLD_MATCH_SOUND)
                        print(display_line)
                        speak_text(card_name)

            except IndexError:
                print("Error: Unable to extract card information.")
                play_sound(NO_MATCH_SOUND)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()  # This will print the detailed traceback

if __name__ == "__main__":
    main()
