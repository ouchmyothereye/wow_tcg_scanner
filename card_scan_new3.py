import cv2
import os
import logging
from google.cloud import vision
from google.cloud import vision_v1 as vision
import sqlite3
from datetime import datetime
from difflib import get_close_matches

# Set up logging
logging.basicConfig(filename='program.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

# Load Google Cloud Vision credentials from environment variables
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_google_cloud_credentials.json"
client = vision.ImageAnnotatorClient()

# Connecting to the database
def connect_to_db():
    conn = sqlite3.connect('wow_cards.db')
    return conn

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

def get_set_abbreviation(extracted_texts, set_abbreviations):
    """
    Identify and return the set abbreviation from the extracted texts.
    """
    # Join the texts and convert to lowercase
    cleaned_text = ' '.join(extracted_texts).lower()
    logging.debug(f"Cleaned text for abbreviation matching: {cleaned_text}")
    
    # Iterate over each set abbreviation
    for abbreviation in set_abbreviations:
        logging.debug(f"Checking for abbreviation: {abbreviation.lower()}")
        if abbreviation.lower() in cleaned_text:
            logging.debug(f"Matched: {abbreviation}")
            return abbreviation

    # If no match is found, return None
    logging.warning("No abbreviation matched.")
    return None
# Querying the database
def query_database(extracted_texts):
    # Connecting to the database
    conn = connect_to_db()
    cursor = conn.cursor()

    # Extracting potential card names
    potential_card_names = [
        text.description for text in extracted_texts[0:3]
    ]

    for card_name in potential_card_names:
        # Querying the card_versions table
        cursor.execute(
            "SELECT DISTINCT set_abbreviation FROM card_versions WHERE card_name = ?", (card_name,)
        )
        set_abbreviations = [item[0] for item in cursor.fetchall()]

        if not set_abbreviations:
            continue

        # Attempt to match set abbreviation
        matched_abbreviation = get_set_abbreviation(extracted_texts, set_abbreviations)
        
        if not matched_abbreviation:
            matched_abbreviation = input(f"Valid set abbreviations are: {', '.join(set_abbreviations)}\nPlease enter a valid set abbreviation from the list above: ")

        cursor.execute("SELECT set_id FROM sets WHERE set_abbreviation = ?", (matched_abbreviation,))
        set_id = cursor.fetchone()

        if not set_id:
            continue

        # Querying card_versions for card name and set ID
        cursor.execute("SELECT card_id FROM card_versions WHERE card_name = ? AND set_id = ?", (card_name, set_id[0]))
        card_id = cursor.fetchone()

        if not card_id:
            continue

        cursor.execute("SELECT variant_id FROM possible_card_variants WHERE card_id = ?", (card_id[0],))
        variant_ids = cursor.fetchall()

        if len(variant_ids) == 1:
            variant_id = variant_ids[0][0]
        else:
            variant_id = int(input(f"Please select a variant ID from the list: {', '.join([str(v[0]) for v in variant_ids])}\n"))

        # Inserting into collection_inventory
        cursor.execute(
            "INSERT INTO collection_inventory(card_id, variant_id, instance, scan_date) VALUES (?, ?, ?, ?)",
            (card_id[0], variant_id, 1, datetime.date.today())
        )
        conn.commit()

        # Closing the database connection
        conn.close()
        return

    print("No card found in the database for the provided texts.")
    # Closing the database connection
    conn.close()

# Function to extract the set abbreviation
def get_set_abbreviation(extracted_texts, set_abbreviations):
    for text in extracted_texts:
        if text.description.lower() in [abbr.lower() for abbr in set_abbreviations]:
            return text.description
    return None

if __name__ == "__main__":
    img_path = capture_image()
    extracted_texts = send_to_gcv(img_path)
    query_database(extracted_texts)
