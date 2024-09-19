"""
This module provides a utility class `Color` to isolate a specific report region 
from an image and determine if the image is of low or high contrast.
"""

import cv2
import numpy as np
from skimage.exposure import is_low_contrast


class Color:
    """
    A class to isolate a report area from an image and check the contrast level.

    Methods:
    --------
    isolate_report(image_path):
        Isolates the largest contour (assumed to be the report) and checks
        whether the cropped image is low or high contrast.
    """

    def isolate_report(self, image_path):
        """
        Isolates the largest contour in the image, crops the image to this region,
        and checks if the cropped image is low or high contrast.

        Parameters:
        ----------
        image_path : str
            The path to the image that needs to be processed.

        Returns:
        -------
        mean_intensity : int
            The mean intensity value of the cropped region.
        diff : int
            Returns 35 if the image is low contrast, 0 if it is high contrast.
        """
        
        # Load the image
        img = cv2.imread(image_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply a binary threshold to segment the report area
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Assume the largest contour corresponds to the report area
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the bounding rectangle for the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Crop the image to this bounding rectangle
        cropped = gray[y:y+h, x:x+w]
        
        # Check if the cropped image is low contrast using `skimage.exposure.is_low_contrast`
        out = is_low_contrast(cropped, fraction_threshold=0.6)
        
        # If the image is low contrast, set `diff` to 35, otherwise set it to 0
        if out:
            diff = 35
        else:
            diff = 0

        # Convert the cropped image to a NumPy array and calculate its mean intensity
        image_array = np.array(cropped)

        return int(np.mean(image_array)), diff
