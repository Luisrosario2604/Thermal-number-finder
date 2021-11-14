#!/usr/bin/python3
# Importing python3 from local, just use "python3 <binary>" if is not the same location

# /
# ** Natalia / Vicent / Luis, 2021
# ** Dectection digit position
# ** File description:
# ** Detecting thermal sections
# ** https://github.com/Luisrosario2604
# ** https://github.com/vgilabert94
# */

# Imports
import flirimageextractor
from matplotlib import cm
import numpy as np
import cv2
import pickle


# Function declarations
def open_file(filename):

    flir = flirimageextractor.FlirImageExtractor(palettes=[cm.jet, cm.bwr, cm.gist_ncar])
    flir.process_image(filename)

    flir_thermal = flir.extract_thermal_image()
    flir_thermal_norm = (flir_thermal - np.amin(flir_thermal)) / (np.amax(flir_thermal) - np.amin(flir_thermal))

    img_rgb = flir.extract_embedded_image()
    img_term = np.uint8(cm.inferno(flir_thermal_norm) * 255)

    return flir_thermal_norm, img_rgb, img_term


def onChange(x, flir_thermal_norm, img_rgb):

    valor = cv2.getTrackbarPos("Thermal", "WinThermal")
    mask = np.uint8(np.logical_not((flir_thermal_norm * 255) > valor)) * 255
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    img_gray_mask = cv2.bitwise_and(img_gray, mask)
    cv2.imshow("WinThermal", img_gray_mask)


def detect_center_of_biggest_countour(gray):
    edged = cv2.Canny(gray, 30, 200)

    contours, hierarchy = cv2.findContours(edged,
                                           cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        center_rectangle = [x + (w / 2), y + (h / 2)]

    return center_rectangle


def main():

    result = []
    for digit in range(9):
        text = "./CODIGOS_ETIQUETADOS/DIGITOS_00" + str(digit + 1) + ".jpg"
        flir_thermal_norm, img_rgb, img_term = open_file(text)
        valor = 210

        thermal_mask = np.uint8(np.logical_not((flir_thermal_norm * 255) > valor)) * 255

        shape = detect_center_of_biggest_countour(thermal_mask)
        result.append([digit+1, shape])

        print(str([digit+1, shape]))

        valor += 0.05
    save_file = open("digit_position.pkl", "wb")
    pickle.dump(result, save_file)
    save_file.close()


# Main body
if __name__ == '__main__':
    main()
