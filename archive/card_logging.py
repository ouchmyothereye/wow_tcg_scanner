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
    with open("cards.json", "r") as file:
        data = json.load(file)
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



    with open('card_log.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
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
        updated_rows.append({
            'Session': session,
            'Card Name': card_name,
            'Card Number': card_number,
            'Set/Block/Raid': set_block_raid,
            'Quantity': '1'
        })

    with open('card_log.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Session', 'Card Name', 'Card Number', 'Set/Block/Raid', 'Quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in updated_rows:
            writer.writerow(row)

    return new_entry

def back_out_last_entry():
    with open('card_log.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
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
    with open('card_log.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Session', 'Card Name', 'Card Number', 'Set/Block/Raid', 'Quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
