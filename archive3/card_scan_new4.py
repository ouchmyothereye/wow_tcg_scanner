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

# Set up logging
logging.basicConfig(filename='program.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

# Load Google Cloud Vision credentials from environment variables
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_google_cloud_credentials.json"
client = vision.ImageAnnotatorClient()


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

def get_set_abbreviation(texts, set_abbreviations):
    cleaned_texts = clean_text(texts)

    # Exact matching
    for abbreviation in set_abbreviations:
        logging.info(f"Checking for abbreviation: {abbreviation}")
        if abbreviation.lower() in cleaned_texts:
            return abbreviation

    # Fuzzy matching if exact matching fails
    best_match_score = 0
    best_match_abbreviation = None
    for abbreviation in set_abbreviations:
        score = fuzz.token_set_ratio(cleaned_texts, abbreviation.lower())
        if score > best_match_score:
            best_match_score = score
            best_match_abbreviation = abbreviation

    # If the best fuzzy match score is above a threshold (e.g., 80), return it
    if best_match_score > 80:
        return best_match_abbreviation

    # If no match found, prompt the user to select the correct abbreviation
    logging.warning("No abbreviation matched with the extracted text.")
    print(f"Possible set abbreviations: {', '.join(set_abbreviations)}")
    while True:
        selected_abbreviation = input("Please select the correct set abbreviation from the list above: ").strip()
        if selected_abbreviation in set_abbreviations:
            return selected_abbreviation
        else:
            print("Invalid selection. Please choose a valid abbreviation from the list.")

def query_database(texts):
    logging.info("Connecting to the 'wow_cards' SQLite database.")
    conn = sqlite3.connect('wow_cards.db')
    cursor = conn.cursor()

    # Step 4: Query wow_cards for card_name
    lines_from_text = texts[0].split('\n')

    matched_abbreviation = None

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
                matched_abbreviation = get_set_abbreviation(extracted_texts, set_abbreviations)
                if matched_abbreviation:
                    logging.info(f"Matched set abbreviation: {matched_abbreviation}")
                    # Extract set_id based on matched abbreviation
                    logging.info(f"Querying 'sets' for set abbreviation: {matched_abbreviation}")
                    cursor.execute("SELECT set_id FROM sets WHERE set_abbreviation=?", (matched_abbreviation,))
                    set_id = cursor.fetchone()[0]
                    logging.info(f"Set ID found: {set_id}")
                    break

    if not matched_abbreviation:
        if not set_id:
            logging.error("No card name found in the extracted lines of the text.")
            return
    else:
        # Step 5: Extract set_id based on the closest match
        matched_abbreviation = get_set_abbreviation(extracted_texts, set_abbreviations)
        if matched_abbreviation:
            logging.info(f"Matched set abbreviation: {matched_abbreviation}")
        else:
            matched_abbreviation = input(f"Valid set abbreviations are: {', '.join(set_abbreviations)}\n"
                                         "Please enter a valid set abbreviation from the list above: ")
            # Extract set_id based on matched abbreviation
            logging.info(f"Querying 'sets' for set abbreviation: {matched_abbreviation}")
            cursor.execute("SELECT set_id FROM sets WHERE set_abbreviation=?", (matched_abbreviation,))
            set_id = cursor.fetchone()
            if set_id:
                set_id = set_id[0]
                logging.info(f"Set ID found: {set_id}")
            else:
                logging.error(f"No set ID found for abbreviation: {matched_abbreviation}")
                return

    # ... Continue with the rest of the function (Steps 6-8 as shared)

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

    # Step 8: Insert into collection_inventory
    current_date = datetime.now()
    logging.info(f"Inserting into 'collection_inventory'. Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Scan Date: {current_date}")
    cursor.execute("INSERT INTO collection_inventory (card_id, variant_id, instance, scan_date) VALUES (?, ?, ?, ?)", 
                    (card_id, variant_id, instance, current_date))
    conn.commit()

    logging.info(f"Insertion successful. Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Date: {current_date}")

    conn.close()

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