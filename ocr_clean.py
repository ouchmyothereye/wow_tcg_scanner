# imports:
import cv2
import numpy as np
# OCR imports:
from PIL import Image
import pyocr
import pyocr.builders

# image path
path = "/Users/badcrumble/Documents/GitHub/wow_tcg_scanner"
fileName = "captured_img.jpg"

# Reading an image in default mode:
inputImage = cv2.imread(path + fileName)

# Get local maximum:
kernelSize = 5
maxKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernelSize, kernelSize))
localMax = cv2.morphologyEx(inputImage, cv2.MORPH_CLOSE, maxKernel, None, None, 1, cv2.BORDER_REFLECT101)

# Perform gain division
gainDivision = np.where(localMax == 0, 0, (inputImage/localMax))

# Clip the values to [0,255]
gainDivision = np.clip((255 * gainDivision), 0, 255)

# Convert the mat type from float to uint8:
gainDivision = gainDivision.astype("uint8")

# Convert RGB to grayscale:
grayscaleImage = cv2.cvtColor(gainDivision, cv2.COLOR_BGR2GRAY)

# Get binary image via Otsu:
_, binaryImage = cv2.threshold(grayscaleImage, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Set kernel (structuring element) size:
kernelSize = 3
# Set morph operation iterations:
opIterations = 1

# Get the structuring element:
morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernelSize, kernelSize))

# Perform closing:
binaryImage = cv2.morphologyEx( binaryImage, cv2.MORPH_CLOSE, morphKernel, None, None, opIterations, cv2.BORDER_REFLECT101 )

# Flood fill (white + black):
cv2.floodFill(binaryImage, mask=None, seedPoint=(int(0), int(0)), newVal=(255))

# Invert image so target blobs are colored in white:
binaryImage = 255 - binaryImage

# Find the blobs on the binary image:
contours, hierarchy = cv2.findContours(binaryImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Process the contours:
for i, c in enumerate(contours):

    # Get contour hierarchy:
    currentHierarchy = hierarchy[0][i][3]

    # Look only for children contours (the holes):
    if currentHierarchy != -1:

        # Get the contour bounding rectangle:
        boundRect = cv2.boundingRect(c)

        # Get the dimensions of the bounding rect:
        rectX = boundRect[0]
        rectY = boundRect[1]
        rectWidth = boundRect[2]
        rectHeight = boundRect[3]

        # Get the center of the contour the will act as
        # seed point to the Flood-Filling:
        fx = rectX + 0.5 * rectWidth
        fy = rectY + 0.5 * rectHeight

        # Fill the hole:
        cv2.floodFill(binaryImage, mask=None, seedPoint=(int(fx), int(fy)), newVal=(0))

# Write result to disk:
cv2.imwrite("text.png", binaryImage, [cv2.IMWRITE_PNG_COMPRESSION, 0])