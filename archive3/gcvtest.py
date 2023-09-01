import os
from google.cloud import vision
import re

vision_client = vision.ImageAnnotatorClient()

# Load the locally saved image
image_path = r'C:\Users\hallc\Documents\worldbuilding\wow_tcg_scanner\captured_image.jpg'
with open(image_path, 'rb') as image_file:
    image_content = image_file.read()

image = vision.Image(content=image_content)

response = vision_client.text_detection(image=image)

card_text = response.text_annotations[0].description if response.text_annotations else "No text detected."

import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('wow_cards.db')
cursor = connection.cursor()

# Query the table based on the lines in the 'card_text' variable
lines_to_query = [line.strip() for line in card_text.split('\n')][:3]

for line in lines_to_query:
    query = "SELECT * FROM card_versions WHERE card_name = ?"
    cursor.execute(query, (line,))
    result = cursor.fetchall()

    # If matching records are found, print them and exit the loop
    if result:
        for row in result:
            print(row)  # Print the entire row
            matching_column_6 = row[5]  # Assuming column 6 is at index 5
            print("Matching Column 6 Entry:", matching_column_6)
        break

# If no matching records are found for any line, print a message
if not result:
    print("No matching records found.")

# Close the database connection
connection.close()
