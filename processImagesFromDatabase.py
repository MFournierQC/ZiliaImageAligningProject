from analyzeRosaImages import analyzeRosa

from skimage.io import imread_collection
from skimage.color import rgb2gray
from skimage.feature import canny
from skimage.transform import resize, hough_ellipse
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib import pyplot
from scipy.signal import find_peaks
from scipy import ndimage
import scipy.signal
from tkinter.filedialog import askdirectory
import fnmatch
import os

def getRosaProperties (rosaImages):
    """get a list of rosa images, returns the properties in a dictionary, if no rosa found, it will raise an error"""
    rosaProperties=[]
    numberOfRosaFound=0
    for image in range(len(rosaImages)):
        rosaInfo = analyzeRosa(rosaImages[image])
        rosaProperties.append(rosaInfo)
        if rosaInfo['found']:
            numberOfRosaFound +=1
    if numberOfRosaFound == 0:
        raise ImportError("No laser spot was found. Try with different data.")
    return rosaProperties

# def findDarkImages (retinaImages):
#     max = np.max(retinaImages)
#     min = np.min(retinaImages)
#     for image in range(len(retinaImages)):
#         print('number : ', image)
#         print('mean   :  ', np.mean(retinaImages[image]))
#     return max


def findBlurryImages (retinaImages):
    """see if the image is blurry based on the average laplacian std
    returns a label that is true if the image is blurry and false if it is not!"""
    blurryImages = []
    laplacianVarianceValues = np.array([])
    for image in range(len(retinaImages)):
        normalizedRetinaImage = 256 * ((retinaImages[image] - np.min(retinaImages[image])) /
                                       (np.max(retinaImages[image]) - np.min(retinaImages[image])))
        laplacianOfImage = cv2.Laplacian(normalizedRetinaImage, cv2.CV_64F)
        laplacianVariance = laplacianOfImage.var()
        laplacianVarianceValues = np.hstack((laplacianVarianceValues, laplacianVariance))
    laplacianThreshold = np.mean(laplacianVarianceValues) # - np.std(laplacianVarianceValues)
    for i in range(laplacianVarianceValues.shape[0]):
        if laplacianVarianceValues[i] < laplacianThreshold :
            blurryImages.append('True')
        else :
            blurryImages.append('False')
    return blurryImages

def cropImageMargins(image , margin=250 ):
    return image [margin:image.shape[0] - margin, margin:image.shape[1] - margin]

def spotDarkVessels(image , n = 100 ):
    croppedSkeleton=np.zeros(image.shape)
    for i in range(image.shape[0]):
        columns = np.convolve(image[i,:], np.ones(n)/n, mode='valid')
        peaks, _ = find_peaks(-columns, prominence=0.001, distance=250)
        croppedSkeleton[i , peaks] = 1
    for i in range(image.shape[1]):
        rows = np.convolve(image[:,i], np.ones(n)/n, mode='valid')
        peaks, _ = find_peaks(-rows, prominence=0.001, distance=250)
        croppedSkeleton[peaks , i ] = 1
    return croppedSkeleton

def calculateSkeletonImage (image , margin = 250 , n=100 ):
    skeletonImage = np.zeros(image.shape)
    croppedImage = cropImageMargins(image , margin = margin)
    skeletonImage[margin:image.shape[0]-margin , margin:image.shape[1]-margin] = spotDarkVessels(croppedImage , n = n)
    return ndimage.binary_closing(skeletonImage[:,:], structure=np.ones((20,20))).astype(np.float)

def findGoodImagesIndex (blurryFlag):
    return np.where(np.array(blurryFlag) != 'True')[0]

def calculateValidShiftsInOneAcquisition(images: np.ndarray, margin=250, n=100 , maxValidShift = 200):
    """Calculated the shift in x and y direction in two consecutive images
        Input: list of 2D numpy arrays (series of retina images)
        The shift in the first image is considered to be zero
        Output: 2D numpy array with the shifts in each image regarding the first image
        """
    blurryImagesLabel = findBlurryImages(images)
    goodImagesNumber = findGoodImagesIndex(blurryImagesLabel)

    imageIsValid = [None] * len(blurryImagesLabel)
    imageIsValid [goodImagesNumber[0]] = True
    shiftValueFromReferenceImage = [None] * len(blurryImagesLabel)
    shiftValueFromReferenceImage[goodImagesNumber[0]] = np.array([0, 0])
    tempShiftVariable=np.array([0,0])

    if (len(goodImagesNumber) > 1):
        for firstImage in range(len(goodImagesNumber) - 1):
            shiftValue = np.array([1000,1000])
            firstSkeletonImage = calculateSkeletonImage(images[goodImagesNumber[firstImage+1]],margin=margin , n=n)
            for secondImage in range(firstImage+1):
                if (shiftValue[0]>maxValidShift or shiftValue[1]>maxValidShift):
                    if imageIsValid[goodImagesNumber[firstImage - secondImage]]:
                        secondSkeletonImage = calculateSkeletonImage(images[goodImagesNumber[firstImage - secondImage]]
                                                                     , margin=margin , n=n)
                        crossCorrelationResult = crossImage(firstSkeletonImage, secondSkeletonImage)
                        maxValueIndexFlat = np.argmax(crossCorrelationResult, axis=None)
                        maxValueIndex2D = np.unravel_index(maxValueIndexFlat, crossCorrelationResult.shape)
                        halfImageSize = np.array([firstSkeletonImage.shape[0] / 2, firstSkeletonImage.shape[1] / 2])
                        shiftValue = np.array(maxValueIndex2D) - halfImageSize
    
            if(shiftValue[0] < maxValidShift and shiftValue[1] < maxValidShift):
                imageIsValid[goodImagesNumber[firstImage+1]] = True
                tempShiftVariable += shiftValue.astype(np.int)
                shiftValueFromReferenceImage[goodImagesNumber[firstImage + 1]] = tempShiftVariable

    return shiftValueFromReferenceImage , imageIsValid


def applyShiftOnRosaCenter ( rosaInfoAbsolute , shiftValuesFromReferenceImage):
    """
    Apply the shift value on the x and y of the rosa
    """
    rosaOnRefImage = [None] * len(shiftValuesFromReferenceImage)
    for i in range(len(shiftValuesFromReferenceImage)):
        if rosaInfoAbsolute[i]['found']:
            if shiftValuesFromReferenceImage[i] is not None :
                rosaOnRefImage [i] = [int(rosaInfoAbsolute[i]['center']['x']-shiftValuesFromReferenceImage[i][1]) ,
                                  int(rosaInfoAbsolute[i]['center']['y']-shiftValuesFromReferenceImage[i][0])]
    return  rosaOnRefImage

def crossImage(firstImage, secondImage) -> np.ndarray:
    """
    Calculate the cross correlation between two images
    Get rid of the averages, otherwise the results are not good
    Input: two 2D numpy arrays
    Output: cross correlation
    """
    firstImage -= np.mean(firstImage)
    secondImage -= np.mean(secondImage)
    crossCorrelationValues = scipy.signal.fftconvolve(firstImage, secondImage[::-1,::-1], mode='same')
    return crossCorrelationValues


def findRefImage (isValidFlag, images ):
    validImagesIndex = np.where(np.array(isValidFlag) == True)[0]
    return images[validImagesIndex[0]]

def normalize (data , max = None , min = None):
    if max is None and min is None:
        return (data - np.min(data)) / (np.max(data) - np.min(data))
    else:
        return (data - min) / (max - min)
    
def findOHNParamsInRefImage (refImage):
    meanValueOfRefImage = np.mean(refImage)
    normalizeImage = normalize(refImage)
    meanRowsValues = np.mean(normalizeImage , axis=0)
    normalizeRows = normalize(meanRowsValues)
    normalizeRows = np.round(normalizeRows, 2)
    onhWidth = np.max(np.where(normalizeRows > 0.50)) - np.min(np.where(normalizeRows > 0.50))
    onhCenterXCoords = int(np.min(np.where(normalizeRows > 0.50)) + onhWidth / 2)

    meanColumnsvalues = np.mean(normalizeImage, axis=1)
    normalizeColumns = normalize(meanColumnsvalues)
    normalizeColumns = np.round(normalizeColumns, 2)
    onhHeight = np.max(np.where(normalizeColumns > np.min([meanValueOfRefImage * 4, 0.50]))
                       ) - np.min(np.where(normalizeColumns > meanValueOfRefImage * 2))
    onhCenterYCoords = int((np.min(np.where(normalizeColumns > meanValueOfRefImage * 2)) + onhHeight / 2))
    length = int((np.min([onhHeight, onhWidth])) / 2)
    return  onhCenterXCoords,onhCenterYCoords,length

def calculateRosaDistanceFromOnhInRefImage (onhXCenter, onhYCenter , rosaLocationOnRefImage):
    rosaDistanceFromOnh = [None] * len(rosaLocationOnRefImage)
    for rosa in range(len(rosaLocationOnRefImage)):
        if rosaLocationOnRefImage[rosa] is not None:
            rosaDistanceFromOnh[rosa] = [rosaLocationOnRefImage[rosa][0] - onhXCenter ,
                                         rosaLocationOnRefImage[rosa][1] - onhYCenter]
            # this part might have some problem with axis!
    return rosaDistanceFromOnh

