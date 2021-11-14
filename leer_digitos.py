#!/usr/bin/python3
# Importing python3 from local, just use "python3 <binary>" if is not the same location

# /
# ** Natalia / Vicent / Luis, 2021
# ** Leer digitos
# ** File description:
# ** Detecting thermal sections
# ** https://github.com/Luisrosario2604
# ** https://github.com/vgilabert94
# */

# Imports
import argparse
import flirimageextractor
from matplotlib import cm
import numpy as np
import cv2
from PIL import Image
import functools


# Function declarations
def get_arguments():
    ap = argparse.ArgumentParser()

    ap.add_argument("-f", "--file", required=True, help="path of the data file")
    return vars(ap.parse_args())


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


def show_image(flir_thermal_norm, img_rgb):
    cv2.imshow("WinThermal", img_rgb)
    cv2.namedWindow("WinThermal")
    cv2.createTrackbar("Thermal", "WinThermal", 255, 255, functools.partial(onChange, flir_thermal_norm=flir_thermal_norm, img_rgb=img_rgb))
    while True:
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()


def main():
    args = get_arguments()

    flir_thermal_norm, img_rgb, img_term = open_file(args["file"])

    Image.fromarray(img_rgb).show()
    Image.fromarray(img_term).show()

    show_image(flir_thermal_norm, img_rgb)


# Main body
if __name__ == '__main__':
    main()
