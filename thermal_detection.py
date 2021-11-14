#!/usr/bin/python3
# Importing python3 from local, just use "python3 <binary>" if is not the same location

# /
# ** Natalia / Vicent / Luis, 2021
# ** Termal detection
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
from operator import itemgetter
import pickle
from math import sqrt


# Global values
is_showing_result = True


# Function declarations
def get_arguments():
    ap = argparse.ArgumentParser()

    ap.add_argument("-f", "--file", required=True, help="path of the data file")
    return vars(ap.parse_args())


def get_distance(x1, y1, x2, y2):
    return sqrt(((x1 - x2)**2) + ((y1 - y2)**2))


def print_result(final_result):
    a = 1

    print()
    print("Final result :")
    print()

    result_txt = ""
    for i in final_result:
        print("\t" + str(a) + ")" + " Number " + str(i[0]) + " with a score " + str(i[1]))
        result_txt += str(i[0]) + "_"
        a += 1

    print()
    print("CSV result : " + str(result_txt[:-1]))


def digit_deduction(digits):
    final_digits = []
    for digit in range(1, 10):
        score = digits.count(digit)
        if score >= 200:
            final_digits.append([digit, score])
    return sorted(final_digits, key=itemgetter(1))


def open_file(filename):

    flir = flirimageextractor.FlirImageExtractor(palettes=[cm.jet, cm.bwr, cm.gist_ncar])
    flir.process_image(filename)

    flir_thermal = flir.extract_thermal_image()
    flir_thermal_norm = (flir_thermal - np.amin(flir_thermal)) / (np.amax(flir_thermal) - np.amin(flir_thermal))

    img_rgb = flir.extract_embedded_image()
    img_term = np.uint8(cm.inferno(flir_thermal_norm) * 255)

    return flir_thermal_norm, img_rgb, img_term


def detect_shape(gray, frame):
    edged = cv2.Canny(gray, 30, 200)
    min_area = 2400
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    rectangles_detection_pos = []

    if 0 < len(contours) < 5:
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)

            if w * h < min_area:
                rectangles_detection_pos.append([x + (w / 2), y + (h / 2)])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)

    if is_showing_result:
        cv2.imshow("Detection", frame)
    return rectangles_detection_pos


def detect_number_touched(rectangles_detection_pos, digit_center):
    digits = []
    for detected_pos in rectangles_detection_pos:
        dist = 20
        i = False
        for c in digit_center:
            dist_tmp = get_distance(detected_pos[0], detected_pos[1], c[1][0], c[1][1])
            if dist_tmp < dist:
                dist = dist_tmp
                digit = int(c[0])
                i = True
        if i:
            digits.append(digit)
    return digits


def main():
    args = get_arguments()

    save_file = open("digit_position.pkl", "rb")
    digit_center = pickle.load(save_file)
    save_file.close()

    flir_thermal_norm, img_rgb, img_term = open_file(args["file"])

    valor = 150
    digits = []
    while valor <= 260:
        thermal_mask = np.uint8(np.logical_not((flir_thermal_norm * 255) > valor)) * 255
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        img_gray_mask = cv2.bitwise_and(img_gray, thermal_mask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        rectangles_detection_pos = detect_shape(thermal_mask, img_gray_mask)
        digits.extend(detect_number_touched(rectangles_detection_pos, digit_center))

        valor += 0.05
    final_result = digit_deduction(digits)
    cv2.destroyAllWindows()

    print_result(final_result)


# Main body
if __name__ == '__main__':
    main()
