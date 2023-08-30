
def fuzzy_match_set(gcv_text, set_abbreviation):
    from fuzzywuzzy import fuzz
    score = fuzz.partial_ratio(gcv_text.lower(), set_abbreviation.lower())
    threshold = 80
    return score >= threshold


import sqlite3
import re
import cv2
import json
from google.cloud import vision
import logging
#from google.cloud.vision import types

from fuzzywuzzy import fuzz




variant_id_to_name = {
    1: 'Oversized',
    2: 'Foil',
    3: 'Extended Art',
    4: 'Alternate Art',
    5: 'Standard',
    6: 'Loot',
    7: 'Extended Art Foil',
    8: 'Alternate Art Foil',
    9: 'Extended Alternate Art',
    10: 'Oversized Extended Art'
}


def _createlog():
    log = logging.getLogger()  # 'root' Logger
    console = logging.StreamHandler()
    format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
    console.setFormatter(logging.Formatter(format_str))
    log.addHandler(console)  # prints to console.
    log.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging
    return log



# Create a logger instance
logger = _createlog()

def fuzzy_match_set(gcv_text, set_abbreviation):
    # Calculate similarity score between GCV text and set abbreviation
    score = fuzz.partial_ratio(gcv_text.lower(), set_abbreviation.lower())
    
    # Define a threshold for matching (e.g., 80%)
    threshold = 80
    
    # Return True if similarity score exceeds threshold, otherwise return False
    return score >= threshold

def prompt_user_for_set():
    """Prompts the user to manually select a set from the available sets in the database."""
    
    cursor.execute("SELECT set_name FROM sets")
    sets = [row[0] for row in cursor.fetchall()]
    
    logger.info("Unable to automatically detect the set. Please select a set from the list below:")
    for index, set_name in enumerate(sets, 1):
        logger.info(f"{index}. {set_name}")
    
    chosen_set_index = None
    while chosen_set_index not in range(1, len(sets) + 1):
        try:
            chosen_set_index = int(input("Enter the number corresponding to the set: "))
            if chosen_set_index not in range(1, len(sets) + 1):
                logger.warning("Invalid choice. Please try again.")
        except ValueError:
            logger.warning("Please enter a valid number.")
    
    return sets[chosen_set_index - 1]

def updated_prompt_user_for_set(card_name):
    # Fetch only the sets where the card name is found
    query = '''
    SELECT DISTINCT sets.set_name
    FROM wow_cards
    JOIN sets ON wow_cards.set_id = sets.set_id
    WHERE wow_cards.card_name = ?
    '''
    cursor.execute(query, (card_name,))
    sets = [row[0] for row in cursor.fetchall()]
    
    if not sets:
        return None  # Return None if no sets found for the card name
    
    # Display the sets for the user to choose from
    print("Unable to automatically detect the set. Please select a set from the list below:")
    for index, set_name in enumerate(sets, 1):
        print(f"{index}. {set_name}")
    
    # Prompt the user to choose a set
    chosen_set_index = None
    while chosen_set_index not in range(1, len(sets) + 1):
        try:
            chosen_set_index = int(input("Enter the number corresponding to the set: "))
            if chosen_set_index not in range(1, len(sets) + 1):
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    return sets[chosen_set_index - 1]

def capture_card_image_with_logging(save_path):
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capture Card Image")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Capture Card Image", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:  # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:  # SPACE pressed
            img_name = save_path
            cv2.imwrite(img_name, frame)
            print(f"{img_name} written!")
            break

    cam.release()
    cv2.destroyAllWindows()

# Function to extract text from image
def extract_text_from_image_updated(filename):
    client = vision.ImageAnnotatorClient()
    with open(filename, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    card_name = ""
    for text in texts[1:]:
        if not text.description[0].isdigit() and "\\n" not in text.description:
            card_name += text.description + " "
        else:
            break
    card_name = card_name.strip()
    set_pattern = re.compile(r'(\w+) \d{1,3}/\d{1,3}')
    set_candidates = [set_pattern.match(text.description) for text in texts[-5:]]
    set_name = next((match.group(1) for match in set_candidates if match), None)
    return card_name, set_name

def extract_text_from_image_to_gcv_with_logging_v4(filename):
    client = vision.ImageAnnotatorClient()
    with open(filename, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    full_text = response.text_annotations[0].description
    logger.debug(f"Full text from GCV: {full_text}")
    
    # Extracting card name, ignoring lines that are only numbers or empty at the start
    lines = [line for line in full_text.split("\n") if line.strip()]
    card_name_line = lines[1] if lines[0].replace(" ", "").isdigit() else lines[0]
    card_name = card_name_line.strip()
    
    logger.debug(f"Extracted card name: {card_name}")
    
    # Adjusted regex pattern for set extraction
    set_pattern = re.compile(r'([A-Z\s]+)\s?\d{1,3}/\d{1,3}')
    set_match = set_pattern.search(full_text)
    set_name = set_match.group(1).strip() if set_match else None
    if set_name:
        logger.debug(f"Extracted set name: {set_name}")
    else:
        logger.debug("Set name not found in the full text.")
    
    return card_name, set_name, response

# Function to search for card in database
def search_sets_for_card_name(card_name):
    query = '''
    SELECT wow_cards.card_id, wow_cards.card_name, sets.set_abbreviation
    FROM wow_cards
    JOIN sets ON wow_cards.set_id = sets.set_id
    WHERE wow_cards.card_name LIKE ?
    '''
    cursor.execute(query, ('%' + card_name + '%',))
    matching_sets = cursor.fetchall()
    return matching_sets

# Function to find set in description
def find_set_in_description(description, matching_sets):
    for card in matching_sets:
        if card[2].lower() in description.lower():
            return card
    return None

def update_card_log(card_id, variant_id, instance):
    logger.debug(f"Logging card with Card ID: {card_id}, Variant ID: {variant_id}, Instance: {instance}")

def handle_card_variants_and_log_with_prompt_updated_v2(card_id):
    # Connect to the database
    conn = sqlite3.connect('wow_cards.db')
    cursor = conn.cursor()

    # Fetch all possible variants for the given card
    cursor.execute("SELECT variant_id, instance FROM possible_card_variants WHERE card_id=?", (card_id,))
    variants = cursor.fetchall()

    if not variants:
        # If there are no specific variants for the card, default to standard
        variant_id = 5
        instance = None
    elif len(variants) == 1:
        # If there's only one variant for the card, use that
        variant_id, instance = variants[0]
    else:
        # If there are multiple variants, prompt the user to choose
        print("Multiple variants detected. Please select a variant:")
        for index, (variant, instance) in enumerate(variants, 1):
            variant_name = variant_id_to_name[variant]
            print(f"{index}. {variant_name} (Variant ID: {variant}, Instance: {instance})")
        selection = int(input())
        variant_id, instance = variants[selection - 1]

    # Update the card log with the chosen variant
    update_card_log(card_id, variant_id, instance)

    # Close the database connection
    conn.close()


# Function to handle card variants and logging
def handle_card_variants_and_log_with_prompt_updated(card_id):
    cursor.execute("SELECT variant_id FROM card_variants WHERE card_id=?", (card_id,))
    variants = [v[0] for v in cursor.fetchall()]

    # Remove the 'standard' variant (id: 5) from the list if there are other variants
    if len(variants) > 1 and 5 in variants:
        variants.remove(5)

    if len(variants) == 1:
        # If only one variant, log and update the card log
        variant_id = variants[0]
        logger.debug(f"Only one variant found. Variant ID: {variant_id}")
        update_card_log(card_id, variant_id)
    else:
        # If multiple variants, prompt the user to select one
        logger.info("Multiple variants detected. Please select a variant:")
        variant_choices = {}
        for index, variant_id in enumerate(variants, 1):
            variant_name = variant_id_to_name[variant_id]
            variant_choices[str(index)] = variant_id
            logger.info(f"{index}. {variant_name} (Variant ID: {variant_id})")

        chosen_variant = None
        while chosen_variant not in variant_choices:
            try:
                chosen_variant = input("Enter the number corresponding to your choice: ")
                if chosen_variant not in variant_choices:
                    logger.warning("Invalid choice. Please try again.")
            except Exception as e:
                logger.error(f"Error while collecting input: {e}")

        variant_id = variant_choices[chosen_variant]
        logger.debug(f"Chosen variant ID: {variant_id}")
        update_card_log(card_id, variant_id)
# Example usage




# Connect to the database
conn = sqlite3.connect('wow_cards.db')  # Replace 'path_to_db' with the path to your database
cursor = conn.cursor()
image_path = "captured_card.jpg"  # Modify path if needed
capture_card_image_with_logging(image_path)
# ... (rest of the code)
# Extract card name, set, and GCV response directly from the captured image
card_name, set_name, gcv_response = extract_text_from_image_to_gcv_with_logging_v4(image_path)
logger.debug(f"Card Name: {card_name}, Set Name: {set_name}")

# If set_name is not detected, prompt user for set selection
if not set_name:
    set_name = updated_prompt_user_for_set(card_name)
    logger.debug(f"User-selected Set Name: {set_name}")

# Search for the card in the database
matching_sets = search_sets_for_card_name(card_name)

# Find the set in the GCV response description
matching_card = find_set_in_description(gcv_response.text_annotations[0].description, matching_sets)

# Handle card variants and log the details
if matching_card:
    handle_card_variants_and_log_with_prompt_updated_v2(matching_card[0])
else:
    logger.warning("No matching set found in the GCV response.")
