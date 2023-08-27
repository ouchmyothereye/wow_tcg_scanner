""" The camera.py file provides functionality related to capturing images using a webcam. Here's a summary:

Import:

The OpenCV library (cv2) is imported.
Function: capture_card_from_webcam():

Initiates a webcam feed using OpenCV.
Displays the live webcam feed in a window titled 'Card Scanner'.
The user is instructed to position the card in view and press the 'c' key to capture the image. Pressing the 'q' key exits the webcam feed.
If the 'c' key (represented by the ASCII code 13) is pressed, the webcam is released, the display window is destroyed, and the current frame (image of the card) is returned.
If the 'q' key is pressed or there's an error in capturing a frame, the webcam feed is terminated, and the display window is destroyed.
This module provides a straightforward way to interact with a webcam and capture images of trading cards. """

import cv2

def capture_card_from_webcam():
    """
    Captures an image of a card from the webcam feed when the 'c' key is pressed.
    """
    cap = cv2.VideoCapture(0)
    print("Opening webcam. Position the card and press 'c' to capture. Press 'q' to exit.")
    
    while True:
        ret, frame = cap.read()
        
        if frame is None or frame.shape[0] == 0 or frame.shape[1] == 0:
            print("Error: Failed to retrieve frame from webcam.")
            break
            
        cv2.imshow('Card Scanner', frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 13:
            cap.release()
            cv2.destroyAllWindows()
            return frame

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
