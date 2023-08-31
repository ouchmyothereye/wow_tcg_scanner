""" The vision.py file focuses on extracting text from the images of trading cards using Google Cloud Vision. Here's a brief summary:

Imports and Initialization:

Essential libraries such as os, cv2, and google.cloud are imported.
The Google Cloud Vision client is initialized.
Function: extract_text_from_image(image_path):

This function takes the path of an image as an input and returns the card's name and its set and number information.
The image is read using OpenCV.
The top part of the image (330x65 pixels from the top) is cropped.
The bottom part of the image (360x45 pixels from the bottom) is cropped.
The two cropped areas are combined vertically into a single image.
This combined image is saved temporarily as "combined_cropped.jpg".
Google Cloud Vision is used to detect text from the combined image.
The extracted text is split into lines.
The card's name is assumed to be in the first block, and any blocks starting with a number are ignored.
The set information of the card is assumed to be in the second block.
The function returns the card name, the card set and number, and the extracted lines of text. """


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
        # Filter out single-letter blocks from GCV response
    filtered_lines = [line for line in lines if len(line.strip()) > 1]
    
    # Extract card name from the first remaining block
    card_name = filtered_lines[0]

    # We'll assume the card name is in the first block, and ignore blocks starting with a number
    # card_name = lines[1] if lines[0][0].isdigit() else lines[0]
    
    # Assuming the set information is in the second block
    card_set_and_number = lines[1] if card_name == lines[0] else lines[2]
    
    return card_name, card_set_and_number, lines
