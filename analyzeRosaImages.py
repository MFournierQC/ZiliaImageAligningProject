import logging
import time
from cv2 import (
    findContours,
    contourArea,
    threshold,
    THRESH_BINARY,
    RETR_TREE,
    CHAIN_APPROX_SIMPLE,
    minEnclosingCircle, 
    minAreaRect,
    THRESH_TOZERO,
#    circle,
    COLOR_BGR2GRAY,
    cvtColor,
#    morphologyEx,
    MORPH_CLOSE
    )
import cv2
from fractions import Fraction
from decimal import Decimal
import numpy as np
from math import pi
from typing import TYPE_CHECKING

LOGGER = logging.getLogger(__name__)

#ECCENTRICITY_CRITERIA = 0.7
# IS_CONTOUR_EMPTY_CRITERIA = 0.4
# R_25_um = 10/2048
# R_75_um = 30/2048
# R_TH_100um = 44/2048
# R_TH_200um = 80/2048
# R_300_um = 100/2048
# R_TH = R_TH_200um
# ALGO_TIMEOUT_IN_SECONDS = 0.5


class ConnectedComponents:
    def __init__(self, binaryImage):
        self.binaryImage = binaryImage
        self.centroidList = []
        self.radiusList = []
        self.areaList = []
        self.majorAxisList = []
        self.minorAxisList = []
        self.contour = []

    def getPropertiesConnectedComponent(self, minLength=4, minArea=15):
        contours = self.getContoursConnectedComponent(self.binaryImage)
        self.filterConnectedComponents(contours, minLength, minArea)

    def getContoursConnectedComponent(self, binaryImage):
        try:
            _, unfilteredContours, _ = findContours(
                binaryImage, RETR_TREE, CHAIN_APPROX_SIMPLE)
        except:
            unfilteredContours, _ = findContours(
                binaryImage, RETR_TREE, CHAIN_APPROX_SIMPLE)
        return unfilteredContours

    def filterConnectedComponents(self, contours, minLength, minArea):
        for cntr in contours:
            if len(cntr) > minLength:
                area = contourArea(cntr)
                if int(area) > minArea:
                    center, radius = minEnclosingCircle(cntr)
                    (_,_), (majorAxis, minorAxis), _ = minAreaRect(cntr)
                    self.centroidList.append(center)
                    self.radiusList.append(radius)
                    area = pi * radius * radius
                    self.areaList.append(area)
                    self.majorAxisList.append(minorAxis / 2)
                    self.minorAxisList.append(majorAxis / 2)
                    self.contour.append(cntr)


def extractGrayMapFromRedChannel(image):
    blue = image[:,:,0]
    red = image[:,:,2]
    redChannel = red >= blue

    grayLevelImg = cvtColor(image, COLOR_BGR2GRAY)
    out_image = redChannel*grayLevelImg

    formattedImage = out_image.astype(np.uint8)
    return formattedImage


def analyzeBinaryImageForRosa(binaryImage, eccentricityCriteria=0.7, R_75_um=30/2048, R_300_um=100/2048):
    in_img_size = binaryImage.shape

    cc = ConnectedComponents(binaryImage)
    cc.getPropertiesConnectedComponent()
    if len(cc.areaList) >= 15:
        return False, 0, 0, 0

    t = time.time()
    list_idx = np.flip(np.argsort(cc.areaList), 0)

    if len(cc.areaList) > 0:
        areaNumber = len(cc.areaList)
        if areaNumber > 1:
            LOGGER.debug("Multiple areas:" + str(areaNumber))
        for idx in list_idx:
            circleCentroid = cc.centroidList[idx]
            circleRadius = cc.radiusList[idx]
            if int(circleRadius) > int(R_75_um * in_img_size[0]) and int(circleRadius) <= int(R_300_um * in_img_size[0]):
                minorAxis = np.min([cc.minorAxisList[idx], cc.majorAxisList[idx]])
                majorAxis = np.max([cc.minorAxisList[idx], cc.majorAxisList[idx]])
                is_a_circle = minorAxis/majorAxis > eccentricityCriteria
                if is_a_circle:
                    return True, float(circleCentroid[1]), float(circleCentroid[0]), float(circleRadius)
    return False, 0, 0, 0


def formatBlob(inImage, laser_spot_parameter):
    """
    Format parameters of the blop and turn them into an organized dictionary.
    Input: inImage(image as a numpy array).
           laser_spot_parameter(an iterable object containing [circle height,
                            circle width, circle radius, True/False value
                            that tells if the spot was found or not]).
    Output: blob(a dictionary that contains all parameters of the blob:
                {"center":{
                        "x": horizontal position of the center of the blob.
                        "y": vertical position of the center of the blob.
                        "rx": horizontal radius of the blob.
                        "ry": vertical radius of the blob.
                        }
                "radius": radius of the smallest circle that surrounds the
                          blob.
                "rradius": rounded radius (is an integer)
                "found": True/False, tells if a spot was found or not.
                }
                )
    """
    # captor_ratio = 1.18
    circleHeight, circleWidth, radius, found = laser_spot_parameter
    h, w = inImage.shape[0], inImage.shape[1]

    rectangle_height = min(h,w)
    rectangle_width = max(h,w)

    r, c = circleWidth, circleHeight

    radius = int(radius)
    blob = {
        'center': {
            "x": r / rectangle_width,
            "y": c / rectangle_height,
            "rx": r,
            "ry": c},
        'radius': float(Fraction(Fraction(Decimal(radius)), h)),
        'rradius': radius,
        'found': found}
    return blob


def fineTuneRosaDetection(redChannel, circleHeight, circleWidth, radius):
    """
    Fine tune the detection of the Rosa in an image.
    Input: redChannel(red channel of the image).
           circleHeight(the height of the circle).
           circleWidth(the width of the circle).
           radius(the radius of the circle).
    Output: 
    """
    h, w = np.shape(redChannel)
    circleHeight, circleWidth = int(circleHeight), int(circleWidth)

    circleHeightOrig, circleWidthOrig = int(circleHeight), int(circleWidth)
    original_radius = int(radius)

    h_crop = h/8
    w_crop = w/8
    h_min = np.amax([int(circleHeight-h_crop), 0])
    h_max = np.amin([int(circleHeight+h_crop), h])
    
    w_min = np.amax([int(circleWidth-w_crop), 0])
    w_max = np.amin([int(circleWidth+w_crop), h])

    crop_img = redChannel[h_min:h_max, w_min:w_max]

    new_img = np.zeros((h,w))
    new_img[h_min:h_max, w_min:w_max] = crop_img
    perc = int(np.max([np.percentile(crop_img, 95) - 1, 0]))

    in_img_size = redChannel.shape
    if int(perc) == 0:
        return circleHeight, circleWidth, original_radius

    else:
        _, binaryImage = threshold(new_img, int(perc), 255, THRESH_BINARY)

        binaryImage = binaryImage.astype(np.uint8)
        found, circleHeight, circleWidth, radius = analyzeBinaryImageForRosa(binaryImage)
        if found:
            return circleHeight, circleWidth, radius
        else:
            return circleHeightOrig, circleWidthOrig, original_radius
    return circleHeightOrig, circleWidthOrig, original_radius


def findLaserSpotMainCall(inImage: np.ndarray):
    """
    Try to find the laser spot in the image.
    Calls a recursive algorithm to do so.
    Input: image as a 3D numpy array.
    Output: blob(output of the formatBlop function, which is a dictionary
                containing parameters of the blob).
            recTime(number of times the recusive algorithm was called).
            found(True or False, says if laser spot was found or not).
    """

    formattedImage = inImage.astype(np.uint8)

    time_start = time.time()
    redChannel = extractGrayMapFromRedChannel(formattedImage)
    maxValueRedChannel = np.max(redChannel)
 
    found, recTime, circleHeight, circleWidth, radius = findLaserSpotRecursive(
        redChannel, maxValueRedChannel, time_start)

    if found:
        circleHeight, circleWidth, fine_tuned_radius = fineTuneRosaDetection(redChannel, circleHeight, circleWidth, radius)
        radius = fine_tuned_radius

    blob = formatBlob(inImage, [circleHeight, circleWidth, radius, found])
    time_elapsed = (time.time() - time_start)

    laser_found = "Laser found" if found else "Laser NOT found"

    LOGGER.warning(
            f"{laser_found}. Took {str(time_elapsed)}. Recursive count {str(recTime)}")

    return blob, recTime, found


def findLaserSpotRecursive(redChannel, maxValue, startTime, recTime=0, thr=0.95, algoTimeoutInSeconds=0.1):
    """
    Use a recursive algorithm to try to find the laser spot in the image.
    Input: redChannel(red channel of the image),
           thr(the set threshold),
           maxValue(maximum light intensity of red channel),
           startTime,
           recTime(number of times the recursive algorithm got executed so
              far).
    Output: Found(True or False, says if laser spot was found or not),
            recTime(number of times the recursive algorithm was ececuted),
            circleHeight(0 if "found" is False, circle height if found is True),
            circleWidth(0 if "found" is False, circle width if found is True),
            radius(0 if found is False, circle radius if found is True).
    """
    recTime = recTime + 1

    binaryImage = binarizeLaserImage(redChannel, thr, maxValue)

    current_time = time.time() - startTime
    if current_time > algoTimeoutInSeconds:
        LOGGER.warning(
            f"Laser spot not found - too long: Took {str(current_time)} for {recTime} iteration."
            )
        return False, recTime, 0, 0, 0

    if thr < 0.4:
        LOGGER.debug(f"Laser spot not found after {recTime} iteration in {str(current_time)}")
        return False, recTime, 0, 0, 0
    found, circleHeight, circleWidth, circleRadius = analyzeBinaryImageForRosa(binaryImage)
    if found:
        return True, recTime, circleHeight, circleWidth, circleRadius

    else:
        th = thr - 0.1
        return findLaserSpotRecursive(redChannel, maxValue, startTime, recTime=recTime, thr=th)


def binarizeLaserImage(inputImage, thresh, maxValue, halfRange=3):
    """
    Turn an image into a binary image.
    Inputs : inputImage(3D numpy array of the red channel of the image).
             thresh(the threshold that is used as a reference to know which
                   pixels shall be turned to 0 while turning the image into
                   a binary image).
             maxValue(maximum light intensity value of the input image)
    Output : binaryImage(numpy array of the image turned into a binary image).
    """
    grayImage = inputImage
    maximum = maxValue

    _, binaryImage = threshold(
        grayImage, int(maximum * thresh) - halfRange, 255, THRESH_TOZERO)
    _, binaryImage = threshold(
        binaryImage, int(maximum * thresh) + halfRange, 255, THRESH_BINARY)

    return binaryImage


# if __name__ == "__main__":
def analyzeRosa(imagePath):
    """
    Import an image as a numpy array and give parameters of the blob.
    Input: imagePath(file path of the image you want to import. Must not
                include accents [è, é, etc.], or else it will not work).
    Output: blob(a dictionary containting parameters from the blob in the
                picure, which is the output of the formatBlob function).
    """

    image = cv2.imread(imagePath)

    blob, _, _ = findLaserSpotMainCall(image)

    return blob
