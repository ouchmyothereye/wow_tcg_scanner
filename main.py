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
from audio_feedback import play_sound, NO_MATCH_SOUND, OLD_MATCH_SOUND, NEW_MATCH_SOUND
from card_logging import get_card_session, get_card_data_from_json, update_card_log
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
        if current_score > highest_score and current_score >= threshold:
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

# Load card data from JSON
with open(os.path.join(get_script_directory(), 'cards.json'), 'r') as file:
    CARDS_DATA = json.load(file)

##def get_best_match_from_json_v2(card_name):
##    for card in CARDS_DATA:
  ##      if card['name'] == card_name:
   ##         return card
 ##   return None

with open("cards.json", "r") as file:
    cards_data = json.load(file)


def main():
    try:
      #  print("Opening webcam. Position the card and wait for auto-capture. Press 'q' to exit.")
        session = get_card_session()

        while True:
            # Capture the card using the new auto-capture method
            card_image = capture_card_from_webcam()

            if card_image is None:  # Exit if 'q' was pressed or if there was an issue
                break

            # Save the captured card image to a file
            captured_image_path = "captured_card.jpg"
            cv2.imwrite(captured_image_path, card_image)

            try:
                card_name, card_set_and_number = extract_text_from_image(captured_image_path)
                print(f"Extracted Card Name: {card_name}")
                card_data = get_best_match_from_json_v2(card_name, cards_data)
                if not card_data:
                    print(f"No match found in JSON data for card name: {card_name}")

                if card_data:
                    card_info = card_data.get('set') or card_data.get('block') or card_data.get('raid') or "Unknown"
                    display_line = f"Card Name: {card_name} | Card Number: {card_data['num']} | Set/Block/Raid: {card_info}"
                    new_entry = update_card_log(card_data['name'], card_data['num'], card_data['set'], session)

                    
                    if new_entry:
                        print(f"\033[92m{display_line}\033[0m")  # Print in green
                        play_sound(NEW_MATCH_SOUND)

                    else:
                        print(display_line)
                        play_sound(OLD_MATCH_SOUND)


            except IndexError:
                print("Error: Unable to extract card information.")
                play_sound(NO_MATCH_SOUND)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()  # This will print the detailed traceback

if __name__ == "__main__":
    main()
