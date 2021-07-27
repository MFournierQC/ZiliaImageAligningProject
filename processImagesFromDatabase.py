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




def removeBadImages(dataDictionary) -> dict:
    """
    Purpose: remove images with low contrast or blurry
    1- use laplacian filter to remove blury images
    2- use average intensity in retinal images for thresholding
    input: series of retina images, series of rosa images, x,y, radius of the rosa center,
           image number in the original folder
    output: reduced data
    """
    image = dataDictionary["image"]

    index = np.array([])
    ii = np.array([])
    for i in range(image.shape[0]):
        temp = image[i,:,:]
        temp = 256*((temp - np.min(temp))/(np.max(temp) - np.min(temp)))
        resultLaplacian = cv2.Laplacian(temp, cv2.CV_64F)
        score = resultLaplacian.var()
        scoreArray = np.hstack((ii, score))

    Threshold = np.mean(scoreArray) + np.std(scoreArray)
    indexToRemove = np.where(scoreArray < Threshold)
    if len(indexToRemove[0]) != 0:
        # Some images are too blurry, let's remove them
        cleanDataDictionary = removeImagesFromIndex(dataDictionary, indexToRemove)
        print("Removed some images because they were too blurry.")
    else:
        cleanDataDictionary = dataDictionary

    return cleanDataDictionary

def findImageShift(Image: np.ndarray, Margin=250, N=100) -> np.ndarray:
    """
    Calculated the shift in x and y direction in two consecutive images
    Input: 3D numpy array (series of retina images)
    The shift in the first image is considered to be zero
    Output: 2D numpy array with the shifts in each image regarding the first image
    """
    temp = Image[:, Margin:Image.shape[1] - Margin, Margin:Image.shape[2] - Margin]
    skeletonImage = np.zeros(Image.shape)
    a = np.zeros(Image.shape)
    indexShift = np.array([0, 0])
    totalShift = np.array([[0, 0]])
    for j in range(temp.shape[0]):
        for i in range(temp.shape[1]):
            y = np.convolve(temp[j,i,:], np.ones(N)/N, mode='valid')
            peaks, _ = find_peaks(-y, prominence=0.001, distance=250)
            skeletonImage[j,i+Margin,peaks+Margin] = 1
        for i in range(temp.shape[2]):
            y = np.convolve(temp[j,:,i], np.ones(N)/N, mode='valid')
            peaks, _ = find_peaks(-y, prominence=0.001, distance=250)
            skeletonImage[j, peaks+Margin, i+Margin] = 1
        a[j,:,:] = ndimage.binary_closing(skeletonImage[j,:,:], structure=np.ones((20,20))).astype(np.int)
        if (j > 0):
            out1 = crossImage(a[j-1,:,:], a[j,:,:])
            maxFlatIndex = np.argmax(out1, axis=None)
            maxIndex = np.unravel_index(maxFlatIndex, out1.shape)
            halfImageSize = np.array([a.shape[1]/2, a.shape[2]/2])
            indexShift = np.vstack((indexShift, np.array(maxIndex) - halfImageSize))
            totalShift = np.vstack((totalShift, np.sum(indexShift, axis=0)))
    return totalShift

def applyShift(xLaser: np.ndarray, yLaser:np.ndarray, shift:np.ndarray) -> tuple:
    """
    Apply the shift value on the x and y of the rosa
    """
    totalShift = (xLaser - shift[:,1]), (yLaser - shift[:,0])
    return totalShift

def crossImage(im1, im2) -> np.ndarray:
    """
    Calculate the cross correlation between two images
    Get rid of the averages, otherwise the results are not good
    Input: two 2D numpy arrays
    Output: cross correlation
    """
    im1 -= np.mean(im1)
    im2 -= np.mean(im2)
    cross = scipy.signal.fftconvolve(im1, im2[::-1,::-1], mode='same')
    return cross

def getRosaLabels(gridParameters, shiftParameters, dataDictionary) -> list:
    xCenterGrid = gridParameters[0]
    yCenterGrid = gridParameters[1]
    length = gridParameters[2]
    xRosa = shiftParameters[1]
    yRosa = shiftParameters[0]
    xLabel = np.array(['1','2','3','4','5','6','7','8','9','10'])
    yLabel = np.array(['A','B','C','D','E','F','J','K','L','M'])

    xGrid = np.array(range(-5*length, 5*length))
    xlabel = np.array( ["" for x in range(xGrid.shape[0])])
    for x in range(xLabel.shape[0]):
        xlabel[x*length:(x+1)*length] = xLabel[x]
    yGrid = np.array(range(-5*length, 5*length))
    ylabel = np.array( ["" for x in range(yGrid.shape[0])])
    for y in range(yLabel.shape[0]):
        ylabel[y*length:(y+1)*length] = yLabel[y]

    outputLabels = []
    imageIndexesToRemove = []

    for j in range(xRosa.shape[0]):
        xTemporaryLabel = xlabel[ np.where(xGrid == xRosa[j] - xCenterGrid)[0] ]
        if len(xTemporaryLabel) == 0:
            # no match was found, the rosa is out of the grid boudaries
            imageIndexesToRemove.append(j)
            continue
        else:
            xTemporaryLabel = str(xTemporaryLabel[0])
        yTemporaryLabel = ylabel[ np.where(yGrid == yRosa[j] - yCenterGrid)[0] ]
        if len(yTemporaryLabel) == 0:
            # no match was found, the rosa is out of the grid boudaries
            imageIndexesToRemove.append(j)
            continue
        else:
            yTemporaryLabel = str(yTemporaryLabel[0])
        temporaryLabel = str(xTemporaryLabel + yTemporaryLabel)
        outputLabels.append(temporaryLabel)

    # Remove images out of boundaries
    if imageIndexesToRemove != []:
        print("Removing images because the ROSA is out of the grid.")
        shiftParameters = cleanShiftParameters(shiftParameters, indexesToRemove)
        imageDataDictionary = removeImagesFromIndex(dataDictionary, imageIndexesToRemove)
    else:
        imageDataDictionary = dataDictionary

    return outputLabels, imageDataDictionary, shiftParameters

def removeImagesFromIndex(dataDictionary, indexes):
    image = dataDictionary["image"]
    laserImage = dataDictionary["laserImage"]
    xCenter = dataDictionary["xCenter"]
    yCenter = dataDictionary["yCenter"]
    radius = dataDictionary["radius"]
    imageNumber = dataDictionary["imageNumber"]

    image = np.delete(image, indexes, axis=0)
    laserImage = np.delete(laserImage, indexes, axis=0)
    xCenter = np.delete(xCenter, indexes, axis=0)
    yCenter = np.delete(yCenter, indexes, axis=0)
    radius = np.delete(radius, indexes, axis=0)
    imageNumber = np.delete(imageNumber, indexes, axis=0)

    imageDataDictionary = {
        "image": image,
        "laserImage": laserImage,
        "xCenter": xCenter,
        "yCenter": yCenter,
        "radius": radius,
        "imageNumber": imageNumber
    }

    return imageDataDictionary

def cleanShiftParameters(shiftParameters, indexesToRemove):
    xShift = shiftParameters[1]
    xShift = np.delete(xShift, indexesToRemove)
    yShift = shiftParameters[0]
    yShift = np.delete(yShift, indexesToRemove)
    return xShift, yShift

def oldDefineGrid(images):
    temp = np.zeros(images.shape)
    temp[np.where(images >= np.mean(images)*1.9)] = 1
    kernel = np.ones((5,5), np.uint8)
    openingTemp = cv2.morphologyEx(temp[0,:,:], cv2.MORPH_OPEN, kernel)
    nonZero = np.nonzero(openingTemp)
    onhHeight = np.max(nonZero[0]) - np.min(nonZero[0])
    onhWidth = np.max(nonZero[1]) - np.min(nonZero[1])
    yCenterGrid = int(((np.max(nonZero[0]) + np.min(nonZero[0]))/2) - (onhHeight-onhWidth))
    xCenterGrid = int((np.max(nonZero[1]) + np.min(nonZero[1]))/2)
    length = int((np.min([onhHeight, onhWidth]))/2)
    return xCenterGrid, yCenterGrid, length




def defineGrid(grayImages):
    imgGray = grayImages[0,:,:]
    meanVal = np.mean(imgGray)
    imgGray = (imgGray - np.min(imgGray)) / (np.max(imgGray) - np.min(imgGray))
    W = np.mean(imgGray, axis=0)
    W = (W - np.min(W)) / (np.max(W) - np.min(W))
    W = np.round(W, 2)
    onhWidth = np.max(np.where(W > 0.50)) - np.min(np.where(W > 0.50))
    onhCenterXCoords = int ( np.min(np.where(W > 0.50)) + onhWidth/2 )

    H = np.mean(imgGray, axis=1)
    H = (H - np.min(H)) / (np.max(H) - np.min(H))
    H = np.round(H, 2)
    onhHeight = np.max(np.where(H > np.min([meanVal * 4, 0.50]))) - np.min(np.where(H > meanVal * 2))
    onhCenterYCoords = int( (np.min(np.where(H > meanVal * 2)) + onhHeight/2)-(onhHeight-onhWidth)/2 )
    length = int((np.min([onhHeight, onhWidth])) / 2)
    return onhCenterXCoords, onhCenterYCoords, length






def defineGridParams(images, xThreshConst=.7, yThreshConst=.7):
    if len(images.shape) == 2:
        # for testing purposes
        plotImage = images
    else:
        plotImage = images[0,:,:]
    sumX = []
    sumY = []
    yIndexes = range(plotImage.shape[0])
    xIndexes = range(plotImage.shape[1])
    for i in yIndexes:
        sumY.append(sum(plotImage[i,:]))
    for j in xIndexes:
        sumX.append(sum(plotImage[:,j]))

    xWidth, xCenterGrid = findONHParamsFromAxisSums(sumX, xIndexes, xThreshConst)
    yWidth, yCenterGrid = findONHParamsFromAxisSums(sumY, yIndexes, yThreshConst)

    gridLength = max(xWidth, yWidth)
    return xCenterGrid, yCenterGrid, gridLength

def findONHParamsFromAxisSums(sumAx, axIndexes, axThreshConst):
    sumAx = np.array(sumAx)
    sumAxNorm = (sumAx - min(sumAx))/(max(sumAx) - min(sumAx))
    # plt.plot(axIndexes, sumAxNorm)
    # plt.plot([0, 900], [axThreshConst, axThreshConst])
    # plt.show()
    maxAxIndex = np.argmax(sumAxNorm)
    leftAxPointIdx = findNearest(sumAxNorm[:maxAxIndex], axThreshConst)
    rightAxPointIdx = findNearest(sumAxNorm[maxAxIndex:], axThreshConst) + maxAxIndex
    axWidth = int(abs(rightAxPointIdx - leftAxPointIdx))
    axCenterGrid = int((rightAxPointIdx + leftAxPointIdx)/2)
    return axWidth, axCenterGrid

def findNearest(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx






def plotResult(image, shiftParameters, gridParameters,saturationsO2, rosaRadius=4, thickness=8,leftEye = False):
    print("Preparing plot of the result")
    refImage = image[0,:,:]
    imageRGB = makeImageRGB(refImage)
    rescaledImage, LowSliceX, LowSliceY = rescaleImage(imageRGB, gridParameters)
    rescaledImageWithCircles = drawRosaCircles(rescaledImage, shiftParameters,
                                LowSliceX, LowSliceY,saturationsO2, rosaRadius=rosaRadius,
                                thickness=thickness)
    resultImageWithGrid = drawGrid(rescaledImageWithCircles, gridParameters)
    if (leftEye == False):
        plt.imsave('Result.jpg', resultImageWithGrid)
    if (leftEye == True):
        plt.imsave('Result.jpg', mirrorImage(resultImageWithGrid))
    return resultImageWithGrid

def makeImageRGB(grayImage):
    imageRGB = np.dstack((grayImage, grayImage, grayImage))
    return imageRGB

def drawRosaCircles(rescaledImage, shiftParameters, LowSliceX, LowSliceY,saturationO2, rosaRadius=4, thickness=8):
    xRosa = shiftParameters[0]
    yRosa = shiftParameters[1]
    normalizedSatiration=(saturationO2-np.min(saturationO2))/(np.max(saturationO2)-np.min(saturationO2))
    for j in range(xRosa.shape[0]):
        color=(normalizedSatiration[j] , 0 , 1-normalizedSatiration[j])
        centerCoordinates = (int(xRosa[j]) + LowSliceX, int(yRosa[j]) + LowSliceY)
        image = cv2.circle(rescaledImage, centerCoordinates, rosaRadius, color, thickness)
    return rescaledImage

def rescaleImage(imageRGB, gridParameters):
    xCenterGrid = gridParameters[0]# int
    yCenterGrid = gridParameters[1]# int
    length = gridParameters[2]# int
    left = np.max([xCenterGrid - (length*5), 0])
    up = np.max([yCenterGrid - (length*5), 0])
    right = np.min([(5*length), (imageRGB.shape[0] - xCenterGrid)]) + xCenterGrid
    down  = np.min([(5*length), (imageRGB.shape[1] - yCenterGrid)]) + yCenterGrid

    temp = imageRGB[up:down, left:right,:]
    xNewCenter = xCenterGrid - left
    yNewCenter = yCenterGrid - up
    gridImage = np.zeros([length*10, length*10, 3])
    # Set slicing limits:
    LOW_SLICE_Y = ((5*length) - yNewCenter)
    HIGH_SLICE_Y = ((5*length) + (temp.shape[0] - yNewCenter))
    LOW_SLICE_X = ((5*length) - xNewCenter)
    HIGH_SLICE_X = ((5*length) + (temp.shape[1] - xNewCenter))
    # Slicing:
    gridImage[LOW_SLICE_Y:HIGH_SLICE_Y, LOW_SLICE_X:HIGH_SLICE_X, :] = temp
    return gridImage, LOW_SLICE_X, LOW_SLICE_Y

def drawGrid(imageRGB, gridParameters):
    length = gridParameters[2]
    dx, dy = length, length
    # Custom (rgb) grid color:
    gridColor = 1
    # Modify the image to include the grid
    imageRGB[:,::dx,:] = gridColor
    imageRGB[::dy,:,:] = gridColor
    return imageRGB
