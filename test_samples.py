"""
* Made to test the different results from applying preprocessing
* before using Tesseract text detection.
* This script returns the following images from samples:
    *
"""

import os
import cv2
import numpy as np
from PIL import ImageGrab, Image
import pytesseract as tf


# Set Tesseract location if you don't have tesseract executable in your PATH (WINDOWS)
# Defaults to: 'C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe'
tf.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

# PATHs to handle images
PATH = "..\samples"
OUT_PATH = "..\samples_out"

"""
Ubisoft username rules:
    - Enter 3 to 15 characters
    - Start with a letter.
    - Use only letters, numerals, and the following punctuation: underscore (_), dash (-), and period (.).

--psm 4 = Assume a single column of text of variable sizes
"""
TENSOR_CONFIG = (
    "--psm 4 -c tessedit_char_whitelist=.-_0123456789abcdefghijklmnopqrstuvwxyz"
)


def textTest():
    global PATH, OUT_PATH, TENSOR_CONFIG

    # Use samples to test different scenarios
    # Iterate through the names of contents of the folder
    for image_path in os.listdir(OUT_PATH):
        if image_path.endswith(".xml") or image_path.endswith(".txt"):
            print("Skipped file:", image_path)
            continue

        image_path = os.path.join(OUT_PATH, image_path)
        img = cv2.imread(image_path)

        d = tf.image_to_data(img, output_type=tf.Output.DICT)
        # print("\nKeys:\n", list(d.keys()))

        n_boxes = len(d["text"])
        for i in range(n_boxes):
            try:
                # * Check if the first character is the banned symbole (#) or unknown (?)
                if d["text"][i] == "??" or d["text"][i] == "#" or d["text"][i] == "":
                    continue

                # * Check if the first character is a letter (rule)
                if not d["text"][i][0].isalpha():
                    continue

                # * We need to convert the confidence values from a float string to an integer
                if int(float(d["conf"][i])) > 60:
                    (x, y, w, h) = (
                        d["left"][i],
                        d["top"][i],
                        d["width"][i],
                        d["height"][i],
                    )
                    cv2.putText(
                        img,
                        d["text"][i],
                        (x - 10 if x > 20 else x + 60, y - 10 if y > 20 else y + 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )
                    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            except Exception as error:
                print(f"Can not convert {d['conf'][i]}", error)

        imS = cv2.resize(img, (960, 540))  # Resize image
        cv2.imshow("TEXT TEST", imS)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def generateSamples():
    global PATH, OUT_PATH, TENSOR_CONFIG

    # Use samples to test different scenarios
    # Iterate through the names of contents of the folder
    for image_path in os.listdir(PATH):

        print("=====================")
        if image_path.endswith(".xml"):
            print("Skipped file:", image_path)
            continue

        print("Image:", image_path)

        # create the full input path and read the file
        input_path = os.path.join(PATH, image_path)
        image = cv2.imread(input_path)

        # * Convert to grayscale and applies thresholding
        screen = image
        screen_G = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        screen_T = cv2.threshold(screen_G, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[
            1
        ]

        # * Save screenshot
        # _0: original image
        # _1: grayscale image
        # _2: grayscale + thresholding image
        cv2.imwrite(f'{OUT_PATH}\{image_path.replace("_1", "_0")}', screen)
        cv2.imwrite(f"{OUT_PATH}\{image_path}", screen_G)
        cv2.imwrite(f'{OUT_PATH}\{image_path.replace("_1", "_2")}', screen_T)

        # Print text from image
        # print(tf.image_to_string(screen))

        # Save different results to text file
        with open(f'{OUT_PATH}\{image_path.replace(".jpg", ".txt")}', "w") as f:
            print("Saving text results to file")
            f.write("==================================")
            f.write("\nORIGINAL IMAGE:\n")
            f.writelines(tf.image_to_string(screen, config=TENSOR_CONFIG))

            f.write("\n==================================")
            f.write("\nGRAYSCALE IMAGE:\n")
            f.writelines(tf.image_to_string(screen_G, config=TENSOR_CONFIG))

            f.write("\n==================================")
            f.write("\nGRAYSCALE + THRESHOLDING IMAGE:\n")
            f.writelines(tf.image_to_string(screen_T, config=TENSOR_CONFIG))


textTest()
