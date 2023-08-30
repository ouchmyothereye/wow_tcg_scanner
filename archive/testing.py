import cv2
import pytesseract
from PIL import Image

def preprocess_image_for_ocr(img_path):
    # Read the image
    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    
    # Binarization using Otsu's method
    _, binary_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Noise reduction (you can use a bilateral filter, median filter, etc.)
    denoised_image = cv2.medianBlur(binary_image, 3)
    
    # Save or return the preprocessed image
    processed_img_path = "processed_" + img_path
    cv2.imwrite(processed_img_path, denoised_image)
    return processed_img_path

def crop_regions(img_path):
    # Load the image
    image = cv2.imread(img_path)

    # Define the coordinates for the regions to be cropped
    x1, y1, w1, h1 = 657, 17, 800, 250
    x2, y2, w2, h2 = 589, 955, 337, 91

    # Crop the regions
    cropped_region1 = image[y1:y1+h1, x1:x1+w1]
    cropped_region2 = image[y2:y2+h2, x2:x2+w2]

    # Save the cropped regions or return them
    cv2.imwrite("cropped_region1.jpg", cropped_region1)
    cv2.imwrite("cropped_region2.jpg", cropped_region2)
    
    return cropped_region1, cropped_region2

def extract_text_from_image(img_path):
    preprocessed_path = preprocess_image_for_ocr(img_path)
    image = Image.open(preprocessed_path)
    text = pytesseract.image_to_string(image)
    return text.strip()

# Example usage:
img_path = "captured_card.jpg"
text_on_card = extract_text_from_image(img_path)
print(text_on_card)
