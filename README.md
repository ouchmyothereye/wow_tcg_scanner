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
    - Note that use of the Google Cloud Vision API for text detection is free, up to point. Please refer to the [pricing policy](https://cloud.google.com/vision/pricing) for any limits.

## Usage

1. Run the script as you would a regular Python script: `python scan.py`.
2. Press the **Enter key** on the numpad to capture an image of the card.
3. Use the presented buttons or keypad to make selections for the set and variant as needed.
4. To quit the utility, press `q`.

The script will automatically update the `collection_inventory` table in the `wow_cards.db` SQLite database file with the recognized card details.

## Monitoring

For real-time monitoring of the card recognition and cataloging process, it's recommended to use a utility like [BareTail](https://www.baremetalsoft.com/baretail/). With BareTail, you can monitor the `program.log` file in real-time to ensure cards are being correctly recognized and cataloged.

## Database Structure: `wow_cards.db`

The SQLite database, `wow_cards.db`, contains information regarding the World of Warcraft Trading Card Game (WoW TCG) cards, their variants, and your collection inventory. A variety of sources were used to create the database, including tcgplayer, [wowcards.info](http://www.wowcards.info/), and the [WoW TCG Collection Tracker Google Sheet by Plague_dog32](https://docs.google.com/spreadsheets/d/1JwrDMrWvFY0Egl0_6wz1SvF4KqVPdOywaBCdRNoq-II/edit#gid=1157922476).

### Tables and Descriptions:

1. **artists**: Lists the artists who have created artwork for the cards.
   - `artist_id`: Unique identifier for each artist.
   - `name`: Name of the artist.

2. **rarities**: Describes the various rarity classifications of the cards.
   - `rarity_id`: Unique identifier for each rarity type.
   - `name`: Rarity name (e.g., Rare, Epic).

3. **release_years**: Holds the years when the cards were released.
   - `year_id`: Unique identifier for each release year.
   - `year`: Actual year of release.

4. **card_variants**: Describes the various card variations, such as foil or special editions.
   - `variant_id`: Unique identifier for each variant type.
   - `description`: Description of the card variant.

5. **blocks**: Contains distinct blocks or groups to which card sets belong.
   - `block_id`: Unique identifier for each block.
   - `block_name`: Name of the block.

6. **sets**: Represents the sets in which the cards were released.
   - `set_id`: Unique identifier for each set.
   - `set_name`: Name of the card set.
   - `set_abbreviation`: Abbreviated form of the set name.
   - `block_id`: Refers to the block to which the set belongs.

7. **wow_cards**: The main table containing all the "base" printings of the cards.
   - `card_id`: Unique identifier for each card.
   - `card_name`: Name of the card.
   - `card_number`: Number assigned to the card.
   - `artist_id`: Refers to the artist of the card.
   - `set_id`: Refers to the set in which the card was released.
   - `rarity_id`: Refers to the rarity of the card.
   - `year_id`: Refers to the year the card was released.

8. **possible_card_variants**: Contains the different variants a card might have, like foil printings.
   - `card_id`: Refers to the base printing of the card.
   - `variant_id`: Refers to the type of variant.
   - `instance`: Denotes the specific instance of a variant. This distinguighes cards that may have mulitple version of a variant (for example, if a card has two different alternate art versions, version #1 would be considered instance 1 and version #2 would be considered instance 2.

9. **collection_inventory**: Represents the user's collection, capturing details of the cards scanned.
   - `card_id`: Refers to the card in question.
   - `variant_id`: Refers to the variant type of the card.
   - `instance`: Denotes the specific instance of a variant.
   - `scan_date`: The date when the card was scanned and added to the inventory.
   - `ignore`: A flag to determine if the card should be ignored or considered in the inventory.

### Notes:

- The `wow_cards` table represents all the basic printings of the cards, with each card assigned a unique `card_id`.
- If a card has a variant, such as a foil printing, it will be listed in the `possible_card_variants` table. The `card_variants` table provides descriptions of these variations.


## Additional Information

Ensure you have a stable internet connection, as the utility relies on Google Cloud Vision's cloud services for image recognition.
