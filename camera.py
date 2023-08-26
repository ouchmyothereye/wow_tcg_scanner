# TODO: Implement real-time feedback on card placement in the camera's view.
# Use contour detection to highlight card edges and guide the user to adjust the card's position for optimal scanning.

import cv2

def capture_card_from_webcam():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cv2.imshow('Card Scanner', frame)

        key = cv2.waitKey(1)
        if key == ord('c'):  # If 'c' is pressed, capture the image
            cv2.imwrite('captured_card.jpg', frame)
            cv2.destroyAllWindows()
            cap.release()
            return 'captured_card.jpg'
        elif key == ord('q'):  # If 'q' is pressed, exit
            cv2.destroyAllWindows()
            cap.release()
            return None
