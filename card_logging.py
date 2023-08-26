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
            if row['Card Name'] == card_name and row['Set/Block/Raid'] == set_block_raid:
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
