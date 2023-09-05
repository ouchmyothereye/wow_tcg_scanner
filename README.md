# WoW TCG Card Scanning Utility

This utility is designed to recognize and catalog cards from the World of Warcraft Trading Card Game (WoW TCG). It uses Google Cloud Vision for card recognition and updates a SQLite database with the recognized card details.

## Dependencies

To run this utility, you will need the following Python libraries:

- [Google Cloud Vision](https://cloud.google.com/vision/docs/libraries)
- SQLite
- Pygame
- (Any other dependencies listed at the start of `scan.py`)

## Setup

1. **SQLite Database**: Use the provided `wow_cards.db` SQLite database. If you want to start with a fresh collection, you can either:
    - Remake the `collection_inventory` table with the same columns.
    - Set all existing records' "ignore" column to 1 in the `collection_inventory` table.

2. **Google Cloud Vision**: 
    - Create your own Google Cloud Vision service account to use the API. Follow the [official documentation](https://cloud.google.com/vision/docs/setup) to get started.
    - Place the JSON key for the service account in your environment variables. This is essential for the script to access Google Cloud Vision services.

## Usage

1. Run the script as you would a regular Python script: `python scan.py`.
2. Press the **Enter key** on the numpad to capture an image of the card.
3. Use the presented buttons or keypad to make selections for the set and variant as needed.
4. To quit the utility, press `q`.

The script will automatically update the `collection_inventory` table in the `wow_cards.db` SQLite database file with the recognized card details.

## Monitoring

For real-time monitoring of the card recognition and cataloging process, it's recommended to use a utility like [BareTail](https://www.baremetalsoft.com/baretail/). With BareTail, you can monitor the `program.log` file in real-time to ensure cards are being correctly recognized and cataloged.

## Additional Information

Ensure you have a stable internet connection, as the utility relies on Google Cloud Vision's cloud services for image recognition.
