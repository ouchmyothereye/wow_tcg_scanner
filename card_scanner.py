import sqlite3
from difflib import get_close_matches
import cv2
from google.cloud import vision
from google.cloud.vision_v1 import Image
import re

# Connect to the database
conn = sqlite3.connect('./wow_cards.db')
cursor = conn.cursor()

def capture_image(filename='captured_card.jpg'):
    cap = cv2.VideoCapture(0)
    
    print("Press 'c' to capture the card image.")
    while True:
        ret, frame = cap.read()
        cv2.imshow('Capture Card', frame)

        if cv2.waitKey(1) & 0xFF == ord('c'):
            cv2.imwrite(filename, frame)
            break

    cap.release()
    cv2.destroyAllWindows()
    return filename

# def extract_text_from_image(filename):
    client = vision.ImageAnnotatorClient()

    with open(filename, 'rb') as image_file:
        content = image_file.read()

    image = Image(content=content)
    response = client.text_detection(image=image)
    
    # Print the complete response for troubleshooting
    print("Response from Google Cloud Vision:")
    print(response)
    
    texts = response.text_annotations

    # Extracting card name from the first 4 blocks
    card_name_candidates = [text.description for text in texts[1:5] if not text.description[0].isdigit()]
    card_name = card_name_candidates[0] if card_name_candidates else None

    # Extracting set from the last blocks using regex
    set_pattern = re.compile(r'(\w+) \d{1,3}/\d{1,3}')
    set_candidates = [set_pattern.match(text.description) for text in texts[-5:]]
    set_name = next((match.group(1) for match in set_candidates if match), None)

    return card_name, set_name

def extract_text_from_image_updated(filename):
    client = vision.ImageAnnotatorClient()

    with open(filename, 'rb') as image_file:
        content = image_file.read()

    image = Image(content=content)
    response = client.text_detection(image=image)
    
    # Print the complete response for troubleshooting
 #   print("Response from Google Cloud Vision:")
  #  print(response)
    
    texts = response.text_annotations

    # Extracting card name from the first few blocks, concatenating them if they don't start with a number
    card_name_candidates = [text.description for text in texts[1:5] if not text.description[0].isdigit()]
    card_name = ' '.join(card_name_candidates).strip()

    # Extracting set from the last blocks using regex
    set_pattern = re.compile(r'(\w+) \d{1,3}/\d{1,3}')
    set_candidates = [set_pattern.match(text.description) for text in texts[-5:]]
    set_name = next((match.group(1) for match in set_candidates if match), None)

    return card_name, set_name

def match_card_details(card_name, card_set):
    """Match the provided card name and set against the card_versions view."""
    # Try to find an exact match
    exact_match = cursor.execute(
        "SELECT * FROM card_versions WHERE card_name = ? AND set_name = ?;",
        (card_name, card_set)
    ).fetchone()
    
    if exact_match:
        return {"type": "exact", "data": exact_match}
    
    # If exact match is not found, attempt to find the closest match based on card name
    all_card_names = cursor.execute("SELECT card_name FROM card_versions;").fetchall()
    all_card_names = [name[0] for name in all_card_names]
    
    closest_match_name = get_close_matches(card_name, all_card_names, n=1)
    
    if closest_match_name:
        closest_match = cursor.execute(
            "SELECT * FROM card_versions WHERE card_name = ?;",
            (closest_match_name[0],)
        ).fetchall()
        return {"type": "close", "data": closest_match}
    
    # If no match is found
    return {"type": "none", "data": None}

def match_card_details_with_user_input(card_name, card_set):
    """Match the provided card name and set against the card_versions view with user input for set matching."""
    
    # Try to find an exact match first for the card name
    exact_match_card_name = cursor.execute(
        "SELECT * FROM card_versions WHERE card_name = ?;",
        (card_name,)
    ).fetchall()
    
    if exact_match_card_name:
        # Try to find a match for the set name based on a partial match (first or last word of full set name)
        potential_matches = [entry for entry in exact_match_card_name if card_set in entry[3].split()]
        
        if potential_matches:
            if len(potential_matches) == 1:
                return {"type": "exact", "data": potential_matches[0]}
            else:
                # If multiple potential matches found, prompt user for selection
                print("Multiple set matches found for the card. Please select one:")
                for idx, match in enumerate(potential_matches):
                    print(f"{idx + 1}. {match[3]}")  # Print set name options
                user_selection = int(input("Enter the number of your choice: "))
                return {"type": "exact", "data": potential_matches[user_selection - 1]}
        else:
            # If no potential matches found based on partial match, prompt user for selection from all exact matches for card name
            print("No set matches found based on partial match. Please select from the following possibilities:")
            for idx, match in enumerate(exact_match_card_name):
                print(f"{idx + 1}. {match[3]}")  # Print set name options
            user_selection = int(input("Enter the number of your choice: "))
            return {"type": "exact", "data": exact_match_card_name[user_selection - 1]}
    
    # If no exact match found for card name, attempt closest match based on card name
    all_card_names = cursor.execute("SELECT card_name FROM card_versions;").fetchall()
    all_card_names = [name[0] for name in all_card_names]
    
    closest_match_name = get_close_matches(card_name, all_card_names, n=1)
    
    if closest_match_name:
        closest_match = cursor.execute(
            "SELECT * FROM card_versions WHERE card_name = ?;",
            (closest_match_name[0],)
        ).fetchall()
        return {"type": "close", "data": closest_match}
    
    # If no match is found
    return {"type": "none", "data": None}

def match_card_details_debug(card_name, card_set):
    """Match the provided card name and set against the card_versions view with debugging information."""
    
    # Try to find an exact match
    exact_match = cursor.execute(
        "SELECT * FROM card_versions WHERE card_name = ? AND set_name = ?;",
        (card_name, card_set)
    ).fetchone()
    
    if exact_match:
        print(f"Exact match found for card name: {card_name} and set: {card_set}")
        return {"type": "exact", "data": exact_match}
    
    # If exact match is not found, attempt to find the closest match based on card name
    all_card_names = cursor.execute("SELECT card_name FROM card_versions;").fetchall()
    all_card_names = [name[0] for name in all_card_names]
    
    closest_match_name = get_close_matches(card_name, all_card_names, n=3)  # Get top 3 matches
    
    if closest_match_name:
        print(f"Closest matches for card name '{card_name}' are: {', '.join(closest_match_name)}")
        
        closest_match = cursor.execute(
            "SELECT * FROM card_versions WHERE card_name = ?;",
            (closest_match_name[0],)
        ).fetchall()
        
        return {"type": "close", "data": closest_match}
    
    # If no match is found
   # print(f"No match found for card name: {card_name}")
   # return {"type": "none", "data": None}

def match_card_details_user_confirm(card_name, card_set):
    """Match the provided card name and set against the card_versions view with user confirmation for close matches."""
    
    # Try to find an exact match first for the card name
    exact_match_card_name = cursor.execute(
        "SELECT * FROM card_versions WHERE card_name = ?;",
        (card_name,)
    ).fetchall()
    
    if exact_match_card_name:
        # Handle set matching as previously described
        potential_matches = [entry for entry in exact_match_card_name if card_set in entry[3].split()]
        
        if potential_matches:
            if len(potential_matches) == 1:
                return {"type": "exact", "data": potential_matches[0]}
            else:
                print("Multiple set matches found for the card. Please select one:")
                for idx, match in enumerate(potential_matches):
                    print(f"{idx + 1}. {match[3]}")  # Print set name options
                user_selection = int(input("Enter the number of your choice: "))
                return {"type": "exact", "data": potential_matches[user_selection - 1]}
    
    # If no exact match found for card name, attempt closest match based on card name
    all_card_names = cursor.execute("SELECT card_name FROM card_versions;").fetchall()
    all_card_names = [name[0] for name in all_card_names]
    
    closest_match_names = get_close_matches(card_name, all_card_names, n=3)  # Get top 3 matches
    
    if closest_match_names:
        # Prompt the user to confirm the closest match or select from other close matches
        print(f"Closest matches for card name '{card_name}' are:")
        for idx, match_name in enumerate(closest_match_names):
            print(f"{idx + 1}. {match_name}")
        user_selection = int(input("Enter the number of your choice or 0 if none of these are correct: "))
        
        if user_selection > 0:
            chosen_match_name = closest_match_names[user_selection - 1]
            closest_match = cursor.execute(
                "SELECT * FROM card_versions WHERE card_name = ?;",
                (chosen_match_name,)
            ).fetchall()
            return {"type": "close", "data": closest_match}
    
    # If no match is found
    return {"type": "none", "data": None}

def match_card_details_with_set_display(card_name, card_set):
    """Match the card name and set with user confirmation for close matches, displaying unique set names."""
    
    # Try to find an exact match first for the card name
    exact_match_card_name = cursor.execute(
        "SELECT * FROM card_versions WHERE card_name = ?;",
        (card_name,)
    ).fetchall()

    if not card_set:
        print("Unable to extract a valid set name from the card. Please check the card and try again.")
        return {"type": "none", "data": None}
    
    if exact_match_card_name:
        # Handle set matching using set_abbreviation
        # Handle set matching using set_abbreviation
        potential_matches = [entry for entry in exact_match_card_name if card_set in (entry[-1] or '')]  # handle potential None values

        
        if not potential_matches:
            potential_matches = [entry for entry in exact_match_card_name if card_set in entry[3].split()]
        
        if potential_matches:
            unique_potential_matches = list({entry[3]: entry for entry in potential_matches}.values())  # Ensure unique set names
            if len(unique_potential_matches) == 1:
                return {"type": "exact", "data": unique_potential_matches[0]}
            else:
                print("Multiple set matches found for the card. Please select one:")
                for idx, match in enumerate(unique_potential_matches):
                    print(f"{idx + 1}. {match[1]} from set {match[3]}")  # Display card name and set name
                user_selection = int(input("Enter the number of your choice: "))
                return {"type": "exact", "data": unique_potential_matches[user_selection - 1]}
    
    # ... (rest of the function remains unchanged)
    
    # If no exact match found for card name, attempt closest match based on card name
    all_card_names = cursor.execute("SELECT card_name FROM card_versions;").fetchall()
    all_card_names = [name[0] for name in all_card_names]
    
    closest_match_names = get_close_matches(card_name, all_card_names, n=3)  # Get top 3 matches
    
    if closest_match_names:
        # Prompt the user to confirm the closest match or select from other close matches
        print(f"Closest matches for card name '{card_name}' are:")
        for idx, match_name in enumerate(closest_match_names):
            match_details = cursor.execute(
                "SELECT card_name, set_name FROM card_versions WHERE card_name = ?;",
                (match_name,)
            ).fetchone()
            print(f"{idx + 1}. {match_details[0]} from set {match_details[1]}")  # Display card name and set name
        user_selection = int(input("Enter the number of your choice or 0 if none of these are correct: "))
        
        if user_selection > 0:
            chosen_match_name = closest_match_names[user_selection - 1]
            closest_match = cursor.execute(
                "SELECT * FROM card_versions WHERE card_name = ?;",
                (chosen_match_name,)
            ).fetchall()
            return {"type": "close", "data": closest_match}
    

    if not set_name:
        print("Unable to determine the set name from the card.")
        set_name = input("Please enter the set abbreviation from the card: ")

    # Using the card name to find potential matches in the database
    potential_matches = cursor.execute(
        "SELECT * FROM card_versions WHERE card_name = ?;",
        (card_name,)
    ).fetchall()

    # If there are potential matches
    if potential_matches:
        # Filter matches based on the user-inputted set abbreviation
        matched_entries = [match for match in potential_matches if match[-1] == set_name]

        if matched_entries:
            # If there's only one match, return it
            if len(matched_entries) == 1:
                return {"type": "exact", "data": matched_entries[0]}
            else:
                # Handle multiple matches
                print("Multiple matches found for the card. Please select one:")
                for idx, match in enumerate(matched_entries):
                    print(f"{idx + 1}. {match[1]} from set {match[3]} (Abbreviation: {match[-1]})")
                user_selection = int(input("Enter the number of your choice: "))
                return {"type": "exact", "data": matched_entries[user_selection - 1]}

        else:
            # If no matches found with the user-inputted abbreviation, display all potential matches
            print("Multiple potential matches found based on card name. Please select the correct set:")
            for idx, match in enumerate(potential_matches):
                print(f"{idx + 1}. {match[1]} from set {match[3]} (Abbreviation: {match[-1]})")
            user_selection = int(input("Enter the number of your choice: "))
            return {"type": "exact", "data": potential_matches[user_selection - 1]}

    else:
        # If still no matches found, return a message indicating so
        print(f"No matches found for card name '{card_name}' with set abbreviation '{set_name}'.")

    
   # else:
        # If no matches found, return a message indicating so
   #     print(f"No matches found for card name '{card_name}' in set '{set_name}'.")

    
    # If no match is found
    return {"type": "none", "data": None}

def handle_variants(matched_card):
    """Handle card variants and prompt user for selection if necessary."""
    # Extract card_id from matched_card
    if isinstance(matched_card, tuple):
        card_id = matched_card[0]
    elif isinstance(matched_card, list):
        card_id = matched_card[0][0]
    else:
        raise ValueError("Invalid format for matched_card.")
    
    # Fetch possible variants for the matched card
    variants = cursor.execute(
        "SELECT variant_id, variant_type FROM card_versions WHERE id = ?;",
        (card_id,)
    ).fetchall()
    
    # If only one variant, return it
    if len(variants) == 1:
        return variants[0][0]
    
    # If multiple variants, prompt user for selection
    print("Multiple variants found for the card. Please select one:")
    for idx, variant in enumerate(variants):
        print(f"{idx + 1}. {variant[1]}")
    
    # Get user selection
    user_selection = int(input("Enter the number of your choice: "))
    
    return variants[user_selection - 1][0]

def log_to_inventory(matched_card, variant_id):
    """Log the matched card (and its variant) to the collection_inventory."""
    
    card_id = matched_card[0]
    card_name = matched_card[1]
    
    # Check if the card (and its variant) is already in the collection_inventory
    existing_entry = cursor.execute(
        "SELECT quantity FROM collection_inventory WHERE card_id = ? AND variant_id = ?;",
        (card_id, variant_id)
    ).fetchone()
    
    # If the card exists in the inventory, update the quantity
    if existing_entry:
        new_quantity = existing_entry[0] + 1
        cursor.execute(
            "UPDATE collection_inventory SET quantity = ? WHERE card_id = ? AND variant_id = ?;",
            (new_quantity, card_id, variant_id)
        )
        conn.commit()
        return f"Updated quantity for card '{card_name}' to {new_quantity}."
    
    # If the card doesn't exist in the inventory, add a new entry
    else:
        instance_value = f"{card_id}_{variant_id}"  # unique instance value based on card_id and variant_id
        cursor.execute(
            "INSERT INTO collection_inventory (card_id, variant_id, instance, quantity) VALUES (?, ?, ?, 1);",
            (card_id, variant_id, instance_value)
        )
        conn.commit()
        return f"Added card '{card_name}' to the inventory."


# Capture card image
image_file = capture_image()

# Extract card details using Google Cloud Vision
detected_text = extract_text_from_image_updated(image_file)
# Split the detected text into card name and set (Adjust this based on your card's format)
card_name, card_set = detected_text

# ...

# Extracting text using Google Cloud Vision
detected_text = extract_text_from_image_updated(image_file)
# Print out the raw text blocks from GCV
print("\nRaw text blocks extracted from the card:")
if detected_text[1]:
    for idx, block in enumerate(detected_text[1]):
        print(f"Block {idx + 1}: {block}")
else:
    print("No additional text blocks were detected beyond the card name.")

detected_text = extract_text_from_image_updated(image_file)

# Extract card name
card_name = detected_text[0]

# Initialize set_name to None
set_name = None

# Check if detected_text[1] exists and is not None
if detected_text[1]:
    set_blocks = detected_text[1][-4:]  # Consider the last 4 blocks for the set name
    set_name_pattern = re.compile(r"[A-Za-z]+\s?\d+/\d+")  # Pattern for "SET_NAME XX/XXX"

    for block in set_blocks:
        if set_name_pattern.search(block):
            set_name = block.split()[0]
            break

# If set name cannot be determined, ask the user
if not set_name:
    print("Unable to determine the set name from the card.")
    set_name = input("Please enter the set abbreviation from the card: ")



# Match the extracted details
matched_card_details = match_card_details_with_set_display(card_name, card_set)
if matched_card_details["type"] != "none":
    chosen_variant = handle_variants(matched_card_details["data"])
    message = log_to_inventory(matched_card_details["data"], chosen_variant)
    print(message)
else:
    print("No matching card found in the database.")
