"""
This module provides functionality to process images and extract text using 
EasyOCR and Tesseract OCR. It performs preprocessing like resizing, thresholding,
and denoising to enhance text extraction from images.
"""

import cv2
import pytesseract
import numpy as np
import easyocr
from get_threshold import Color

# Initialize the color thresholding class
col = Color()

# Specify the Tesseract-OCR executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class ImageConvert:
    """
    A class to process images and extract text using OCR.

    Methods:
    --------
    process_image(image_path):
        Preprocesses the image and extracts text using EasyOCR and Tesseract.
    
    extract_text_from_images(image_paths):
        Processes multiple images and extracts text from each.
    """

    def process_image(self, image_path):
        """
        Processes a single image by applying various preprocessing techniques 
        (grayscale conversion, resizing, thresholding) and extracts text 
        using EasyOCR and Tesseract.

        Parameters:
        ----------
        image_path : str
            The path to the image that needs to be processed.

        Returns:
        -------
        str
            Extracted text from the image, combining both EasyOCR and Tesseract results.
        """
        
        # Load the image
        img = cv2.imread(image_path)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resize the image to enhance text readability
        resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        
        # Isolate the background and calculate contrast difference
        bg, diff = col.isolate_report(image_path)
        print(bg)
        
        # If the image has high contrast, save and load the resized image
        if diff == 0:
            cv2.imwrite('DocEx_frontend/backend/temp/processed_image.jpg', resized)
            preprocessed_image = cv2.imread('DocEx_frontend/backend/temp/processed_image.jpg')

        # If the image is low contrast, apply thresholding and denoising
        else:
            bg -= diff

            # Apply thresholding to separate foreground and background
            _, thresh = cv2.threshold(resized, bg, 255, cv2.THRESH_BINARY)

            # Optionally apply denoising to reduce noise
            denoised = cv2.fastNlMeansDenoising(thresh, None, h=30)

            # Apply a sharpening filter to enhance edges
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened = cv2.filter2D(denoised, -1, kernel)

            # Save and load the processed image
            cv2.imwrite('DocEx_frontend/backend/temp/processed_image.jpg', sharpened)
            preprocessed_image = cv2.imread('DocEx_frontend/backend/temp/processed_image.jpg')

        # Instantiate EasyOCR text detector
        reader = easyocr.Reader(['en'], gpu=False)

        # Detect text in the image using EasyOCR
        text_ = reader.readtext(preprocessed_image)

        # Define the threshold for OCR confidence
        threshold = 0.25

        # Store the extracted text from EasyOCR
        all_texts = []
        for t_ in text_:
            bbox, text, score = t_
            if score > threshold:
                all_texts.append(text)

        # Combine the extracted text
        extracted_text = "\n".join(all_texts)

        # Use Tesseract to extract additional text
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(preprocessed_image, config=custom_config)
        
        # Return both EasyOCR and Tesseract results
        return 'Extraction 1\n' + extracted_text + '\nExtraction 2\n' + text

    def extract_text_from_images(self, image_paths):
        """
        Processes multiple images and extracts text from each.

        Parameters:
        ----------
        image_paths : list of str
            List of paths to images that need to be processed.

        Returns:
        -------
        all_texts : list
            List of extracted texts for each image.
        """
        
        all_texts = []

        # Loop through each image path and process
        for image_path in image_paths:
            print(f"Processing: {image_path}")
            text = self.process_image(image_path)
            all_texts.append(text)
            print(f"Extracted Text: {text}\n")
        
        return all_texts

    