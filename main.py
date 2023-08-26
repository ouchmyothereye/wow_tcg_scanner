# TODO: Implement batch processing to allow multiple cards to be scanned in quick succession.
# Consider having a buffer time between scans or a UI element indicating readiness for the next scan.
# Develop a user-friendly interface for the card scanning system.
# Consider using libraries like PyQt or Tkinter for the UI.
# Consider further modularization if the script grows in complexity.
# Breaking functionalities into separate modules aids maintenance and readability.



import os
import json
from camera import capture_card_from_webcam
from logging import get_script_directory, get_card_session, update_card_log
from vision import extract_text_from_image
from audio_feedback import play_sound, NO_MATCH_SOUND, OLD_MATCH_SOUND, NEW_MATCH_SOUND

# Load card data from JSON
with open(os.path.join(get_script_directory(), 'cards.json'), 'r') as file:
    CARDS_DATA = json.load(file)

def get_card_data_from_json(card_name):
    for card in CARDS_DATA:
        if card['name'] == card_name:
            return card
    return None

if __name__ == "__main__":
    print("Opening webcam. Press 'c' to capture the card. Press 'q' to exit.")
    session = get_card_session()

    while True:
        captured_image_path = capture_card_from_webcam()
        if not captured_image_path:
            break
        try:
            card_name, card_set_and_number = extract_text_from_image(captured_image_path)
            card_data = get_card_data_from_json(card_name)
            
            if card_data:
                card_info = card_data.get('set') or card_data.get('block') or card_data.get('raid') or "Unknown"
                display_line = f"Card Name: {card_name} | Card Number: {card_data['num']} | Set/Block/Raid: {card_info}"
                
                # Check if the card already exists in the log and update accordingly
                new_entry = update_card_log(card_data['name'], card_data['num'], card_info, session)
                if new_entry:
                    print("\\033[92m" + display_line + "\\033[0m")  # Print in green
                    play_sound(NEW_MATCH_SOUND)
                else:
                    print(display_line)
                    play_sound(OLD_MATCH_SOUND)
            else:
                print(f"Card {card_name} not found in cards.json!")
                play_sound(NO_MATCH_SOUND)

        except IndexError:
            print("Error: Unable to extract card information.")
