# TODO: Implement preprocessing steps for captured images to enhance recognition accuracy.
# Suggestions: Convert to grayscale, apply Gaussian blur, use edge detection, etc.
# Integrate with online card databases to fetch card details if not found in local JSON.
# This can provide a fallback mechanism when local data is incomplete or outdated.


import os
# from google.cloud.vision import types
from google.cloud import vision_v1 as vision

# Initialize Cloud Vision client
client = vision.ImageAnnotatorClient()

def extract_text_from_image(image_path):
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    # Extract the first line for card name and third line from the bottom for set information
    lines = response.text_annotations[0].description.strip().split('\n')
    card_name = lines[0]
    card_set_and_number = lines[-3] if len(lines) >= 3 else ""

    return card_name, card_set_and_number
