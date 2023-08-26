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

        if key == ord('c'):
            cap.release()
            cv2.destroyAllWindows()
            return frame

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
