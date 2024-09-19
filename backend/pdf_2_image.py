"""
This module provides functionality to convert PDF files into images.
It uses the `pypdfium2` library to render each page of the PDF as an image.
The converted images are saved in the specified output folder.
"""

import os
import base64
import pypdfium2 as pdfium


class PDFConvert:
    """
    A class to handle the conversion of PDF pages to images.

    Methods:
    --------
    convert_pdf_to_images(file_path, scale, output_folder):
        Converts a PDF file into images and saves them in the specified folder.
    """

    def convert_pdf_to_images(self, file_path, scale=300/72, output_folder='.'):
        """
        Converts each page of a PDF file into images and saves them as JPEG files.

        Parameters:
        ----------
        file_path : str
            The path to the PDF file that needs to be converted.
        scale : float, optional
            The scale factor for rendering the images (default is 300/72).
        output_folder : str, optional
            The folder where the images will be saved (default is the current folder).

        Returns:
        -------
        image_paths : list
            A list of file paths to the saved images.

        """
        
        pdf_file = pdfium.PdfDocument(file_path)  # Load the PDF file
        page_indices = [i for i in range(len(pdf_file))]  # Get the indices of all pages
        
        file_path = os.path.basename(file_path)

        # Render the PDF pages to images
        renderer = pdf_file.render(
            pdfium.PdfBitmap.to_pil,
            page_indices=page_indices,
            scale=scale,
        )

        # Ensure output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)  # Create the folder if it doesn't exist

        image_paths = []  # List to store paths to saved images

        # Loop through each page and save the rendered image
        for i, image in zip(page_indices, renderer):
            image_file_path = os.path.join(
                output_folder,
                f'{file_path[:-4]}_page_{i+1}.jpg'  # Save each page with a unique name
            )
            image.save(image_file_path, format='JPEG', optimize=True)  # Save as JPEG
            image_paths.append(image_file_path)  # Add the image path to the list

        return image_paths  # Return the list of image paths


        
