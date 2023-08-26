# TODO: Implement preprocessing steps for captured images to enhance recognition accuracy.
# Suggestions: Convert to grayscale, apply Gaussian blur, use edge detection, etc.
# Integrate with online card databases to fetch card details if not found in local JSON.
# This can provide a fallback mechanism when local data is incomplete or outdated.


import os
import cv2
# from google.cloud.vision import types
from google.cloud import vision_v1 as vision

# Initialize Cloud Vision client
client = vision.ImageAnnotatorClient()

def extract_text_from_image(image_path):
        # Read the image
    image = cv2.imread(image_path)
    
    # Crop the top part (330x65 starting from the top)
    top_crop = image[:65, :]
    
    # Crop the bottom part (360x45 starting from the bottom)
    height, _, _ = image.shape
    bottom_crop = image[height-45:, :]
    
    # Combine the two cropped areas into a single image
    combined_image = cv2.vconcat([top_crop, bottom_crop])
    combined_image_path = "combined_cropped.jpg"
    cv2.imwrite(combined_image_path, combined_image)

    with open(combined_image_path, 'rb') as image_file:
        content = image_file.read()
    combined_vision_image = vision.Image(content=content)
    response = client.text_detection(image=combined_vision_image)
    lines = response.text_annotations[0].description.strip().split('\n')
    
    # We'll assume the card name is in the first block, and ignore blocks starting with a number
    card_name = lines[1] if lines[0][0].isdigit() else lines[0]
    
    # Assuming the set information is in the second block
    card_set_and_number = lines[1] if card_name == lines[0] else lines[2]
    
    return card_name, card_set_and_number
