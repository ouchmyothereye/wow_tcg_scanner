
# System imports
import io
import sys
import time
import logging

# 3rd-party imports
import cv2
from google.cloud import vision

# Local source imports
import settings

# Set up environment variables for Google
# Note: You will need to modify this with the path to your Google Cloud credentials

#############################
# START FUNCTIONS
#############################

def create_log():
    log = logging.getLogger()  # 'root' Logger
    console = logging.StreamHandler()
    format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
    console.setFormatter(logging.Formatter(format_str))
    log.addHandler(console)  # prints to console.
    log.setLevel(logging.WARNING)
    return log

def capture_card_image_with_webcam(path):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        cv2.imshow('Press "c" to capture the card image', frame)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            cv2.imwrite(path, frame)
            break
    cap.release()
    cv2.destroyAllWindows()

def detect_text(path):
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts[0].description

#############################
# END FUNCTIONS
#############################

# START MAIN
if __name__ == '__main__':
    log = create_log()
    log.info(sys.version)
    main_prop = settings.main()
    main_prop["RUNS"] = 0
    try:
        while main_prop["START"] != 0 and main_prop["RUNS"] < 3:
            log.warning("Run number: " + str(main_prop["RUNS"]))
            main_prop["RUNS"] += 1
            file_path = main_prop["PATH"] + "image" + str(main_prop["RUNS"]) + ".jpg"
            capture_card_image_with_webcam(file_path)
            time.sleep(5)
            card_text = detect_text(file_path)
            log.warning(card_text)
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        pass
