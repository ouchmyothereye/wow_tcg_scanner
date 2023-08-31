import cv2
import os
import logging
from google.cloud import vision
from google.cloud import vision_v1 as vision
import sqlite3
from datetime import datetime
from difflib import get_close_matches

# Set up logging
logging.basicConfig(filename='program.log', level=logging.INFO, format='%(asctime)s - %(message)s')

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
    
def query_database(texts):
    logging.info("Connecting to the 'wow_cards' SQLite database.")
    conn = sqlite3.connect('wow_cards.db')
    cursor = conn.cursor()

    # Step 4: Query card_versions for card_name
    lines_from_text = texts[0].split('\n')

    for potential_card_name in lines_from_text:
        logging.info(f"Querying 'card_versions' for potential card name: {potential_card_name}")
        cursor.execute("SELECT DISTINCT set_abbreviation FROM card_versions WHERE card_name=?", (potential_card_name,))
        result = cursor.fetchall()
        if result:
            card_name = potential_card_name
            set_abbreviations = [row[0] for row in result]
            logging.info(f"Possible set abbreviations for {card_name}: {set_abbreviations}")
            break
    else:
        logging.error("No card name found in the extracted lines of the text.")
        return

    # Step 5: Extract set_id based on the closest match
    matched_abbreviation = None
    lowered_texts = [text.lower() for text in texts]  # Convert all texts to lowercase for case-insensitive matching
    for abbreviation in set_abbreviations:
        for text in texts:
            if abbreviation.lower() in lowered_texts:
                    matched_abbreviation = abbreviation
                    break
        if abbreviation.lower() in lowered_texts:
            matched_abbreviation = abbreviation
            break
        else:
            # Try to find a close match
            close_matches = get_close_matches(abbreviation.lower(), lowered_texts, n=3, cutoff=0.85)
            if close_matches:
                matched_abbreviation = close_matches[0]
                break

    if not matched_abbreviation:
        logging.warning("No set abbreviation found or closely matched in the text.")
        while matched_abbreviation not in set_abbreviations:
            print("Valid set abbreviations are:", ", ".join(set_abbreviations))
            matched_abbreviation = input("Please enter a valid set abbreviation from the list above: ")

    logging.info(f"Matched set abbreviation: {matched_abbreviation}")

    # Step 6: Extract set_id
    logging.info(f"Querying 'sets' for set abbreviation: {matched_abbreviation}")
    cursor.execute("SELECT set_id FROM sets WHERE set_abbreviation=?", (matched_abbreviation,))
    set_id = cursor.fetchone()
    if set_id:
        set_id = set_id[0]
        logging.info(f"Set ID found: {set_id}")
    else:
        logging.error(f"No set ID found for abbreviation: {matched_abbreviation}")
        return

    # ... Continue with the rest of the function


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
    current_date = datetime.now().date()
    logging.info(f"Inserting into 'collection_inventory'. Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Scan Date: {current_date}")
    cursor.execute("INSERT INTO collection_inventory (card_id, variant_id, instance, scan_date) VALUES (?, ?, ?, ?)", 
                    (card_id, variant_id, instance, current_date))
    conn.commit()

    logging.info(f"Insertion successful. Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}, Date: {current_date}")

    conn.close()

if __name__ == "__main__":
    img_path = capture_image()
    extracted_texts = send_to_gcv(img_path)
    query_database(extracted_texts)
