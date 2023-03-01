import os
import time
from pynput.keyboard import Key, Listener
from win32gui import GetWindowText, GetForegroundWindow


# Image manipulation
import cv2
import numpy as np
from PIL import ImageGrab, Image
import pytesseract as tf


# Set Tesseract location if you don't have tesseract executable in your PATH (WINDOWS)
# Defaults to: 'C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe'
tf.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

# PATHs to handle images
path = "..\samples"
outPath = "..\samples_out"


i = 0
last_key_press = None
last_screenshot_time = None
key_press_repeat = 0


def on_press(key):
    global last_key_press
    global key_press_repeat
    global last_screenshot_time

    print("Key pressed: ", key)
    print("Last key pressed: ", last_key_press)
    print("Press repeat: ", key_press_repeat)
    last_key_press = key

    if key != Key.tab:
        key_press_repeat = 0
        return

    key_press_repeat += 1

    # * Key pressed should be at least 3 seconds (time may differ with input lag)
    if key_press_repeat > 30 and last_key_press == Key.tab:
        print("Got screenshot!")
        key_press_repeat = 0

        # * Ignore if a screenshot was taken less than 30 seconds ago
        now = time.time()
        if last_screenshot_time and (now - last_screenshot_time) < 30:
            print(
                f"Screenshot ignored!\nLast screenshot was {last_screenshot_time} seconds ago"
            )
            return

        last_screenshot_time = now
        getImage()


def on_release(key):
    # print('{0} release'.format(key), key == Key.tab)
    if key == Key.esc:
        # Stop listener
        return False


def test():
    # Use samples to test different scenarios
    # Iterate through the names of contents of the folder
    for image_path in os.listdir(path):

        print("=====================")
        print("Image:", image_path)

        # create the full input path and read the file
        input_path = os.path.join(path, image_path)
        image_to_rotate = cv2.imread(input_path)

        # rotate the image
        # rotated = ndimage.rotate(image_to_rotate, 45)

        # create full output path, 'example.jpg'
        # becomes 'rotate_example.jpg', save the file to disk
        # fullpath = os.path.join(outPath, 'Sample_'+image_path)
        # misc.imsave(fullpath, rotated)

        # Print text from image
        print(tf.image_to_string(image_to_rotate))


def getImage():
    print("Generating image...")

    global i
    i += 1

    # * Get screenshot
    # ? OR np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080))) -> x, y, w, h
    screen = np.array(ImageGrab.grab())

    # * Convert to grayscale and applies thresholding
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    screen = cv2.threshold(screen, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # * Save screenshot
    cv2.imwrite(f"test{i}.jpg", screen)

    # * Show image
    # cv2.imshow('Python Window', screen)
    # cv2.waitKey(1)
    # cv2.destroyAllWindows()


def isGameRunning():
    import psutil

    # Print all pids
    for proc in psutil.process_iter(["pid", "name"]):
        print(proc.info)

    return "RainbowSix.exe" in (p.name() for p in psutil.process_iter())


def isCurrentWindowGame():
    return GetWindowText(GetForegroundWindow())  # ! == "Rainbow Six"


def main():
    print("Running....")

    if not isGameRunning():
        # * Suppress automatically exiting
        print("Game is not running!\nExiting automatically...")
        input("\n[ PRESS ENTER TO EXIT ]")
        exit()

    # * Keypress Listener
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
