# TODO: Integrate with a database system for scalability.
# Suggestions: Use SQLite for a lightweight database or consider more robust systems like PostgreSQL for larger collections.

import os
import csv

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

def update_card_log(card_name, card_number, card_info, session):
    log_file_path = os.path.join(get_script_directory(), 'card_log.csv')
    new_entry = False

    # Check if log file exists
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Session', 'Card Name', 'Card Number', 'Set/Block/Raid', 'Quantity'])
    
    # Check if the card already exists in the log
    entries = []
    with open(log_file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[1] == card_name and row[2] == card_number:
                row[4] = str(int(row[4]) + 1)  # Update quantity
                new_entry = False
            entries.append(row)
    
    if new_entry:
        entries.append([session, card_name, card_number, card_info, '1'])

    # Write updated data to the log
    with open(log_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(entries)

    return new_entry
