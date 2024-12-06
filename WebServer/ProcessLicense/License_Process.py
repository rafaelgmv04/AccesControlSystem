import os
import cv2
import pytesseract
import numpy as np
import re

# Path to the Haar Cascade Classifier
harcascade = "ProcessLicense/model/haarcascade_russian_plate_number.xml"

"""
this function receives an image and returns the license plate decoded from the image.

condition: the image must be exist
            the image must be cropped to the license plate
            the image must be decoding correctly

It returns the license plate decoded from the image 
"""
def getLicenseProcess(image):
    if image is None:
        print("Error loading image!")
        return ""
    else:

        plateCrop = cropPlate(image)
        if plateCrop is None:
            print("Error cropting the plate!")
            return ""
        else:
            plateText = decodePlateLicense(plateCrop)
            if plateText is None:
                print("Error decoding plate!")
                return ""
            else:
                return plateText

"""
this function receives an image and returns the license plate cropped from the image.

condition: area of the license plate must be greater than 500 pixels
           the license plate must be in the center of the image
           need decode using nparray to convert the image to a numpy array and then use cv2.imdecode to convert the image to a cv2 image
It returns the license plate cropped from the image        
"""

def cropPlate(plate):
    if plate is None:
        print("Error loading image!")
        return None
    else:
        min_area = 500
        try:
            npArray = np.frombuffer(plate, np.uint8)
            # Carregar a imagem da placa
            plate = cv2.imdecode(npArray, cv2.IMREAD_COLOR)
        except cv2.error as e:
            print(f"Error loading image!: {e}")
            return None
        try:
            plate_cascade = cv2.CascadeClassifier(harcascade)
        except:
            print("Error loading Haar Cascade Classifier!")
            return None
        try:
            plate_gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
        except cv2.error as e:
            print(f"Error to convert image to gray: {e}")
            return None
        try:
            plates = plate_cascade.detectMultiScale(plate_gray, 1.1, 4)
        except:
            print("Error detecting plates!")
            return None
        for (x, y, w, h) in plates:

            area = w * h
            if area >= min_area:
                cv2.rectangle(plate, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(plate, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

                plate_roi = plate[y:y + h, x:x + w]
                print("Detected plate!")
                return plate_roi
            else:
                print("Non detected plate!")
                return None

"""
this function receives a license plate and decode it using pytesseract library.

condition: the license plate must be a clear image, without noise or blur
           the license plate must be in the center of the image
           the license plate must be in the correct orientation
           the license plate must be in the correct size

It returns the license plate decoded as a string        
"""
def decodePlateLicense(license_plate):
    if license_plate is None:
        print("Error loading image!")
    else:
        resize_license_plate = cv2.resize(license_plate, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        grayscale_resize_license_plate = cv2.cvtColor(resize_license_plate, cv2.COLOR_BGR2GRAY)

        gaussian_blur_license_plate = cv2.GaussianBlur(grayscale_resize_license_plate, (5, 5), 0)

        _, binary_license_plate = cv2.threshold(gaussian_blur_license_plate, 150, 255, cv2.THRESH_BINARY)

        predicted_result = pytesseract.image_to_string(gaussian_blur_license_plate, lang='eng', config='--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        filter_predicted_result = "".join(predicted_result.split()).replace(":", "").replace("-", "").replace(".", "")

        return filter_predicted_result



def extrair_substring(input_string):
    match = re.search(r'\d{2}', input_string)
    if match:
        start = match.start()
        end = match.end()
        substring = input_string[max(0, start-2):min(len(input_string), end+2)]
        return substring
    else:
        return "No one number found in the string!"

