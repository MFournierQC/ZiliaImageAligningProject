from analyzeRosaImages import analyzeRosa

from skimage.io import imread_collection
from skimage.color import rgb2gray
import numpy as np
import cv2
import matplotlib.pyplot as plt
#from scipy.ndimage import gaussian_filter
#import scipy.fftpack as fp
from matplotlib import pyplot
from scipy.signal import find_peaks
from scipy import ndimage
import scipy.signal
from tkinter.filedialog import askdirectory
import fnmatch
import os


def mirrorImage(image) -> np.ndarray:
    mirroredImage = image[:,::-1,:]
    return mirroredImage

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
    for kk in range(image.shape[0]):
        d1 = image[kk,:,:]
        d1 = 256*((d1 - np.min(d1))/(np.max(d1) - np.min(d1)))
        resLap = cv2.Laplacian(d1, cv2.CV_64F)
        score = resLap.var()
        ii = np.hstack((ii, score))
    Threshold = np.mean(ii)
    index = np.where(ii < Threshold)

    if len(index[0]) == 0:
        # Some images are too blurry, let's remove them
        print("Removing images because they are too blurry.")
        cleanDataDictionary = removeImagesFromIndex(dataDictionary, index)
    else:
        cleanDataDictionary = dataDictionary

    return cleanDataDictionary

def seperateImages(grayImageCollection, collectionDir: str, extension="jpg") -> dict:
    """
    Purpose: seperate retina images from rosa images
    Load retina image - then load the corresponding rosa image 
    Check to find the rosa, if found, append the image and other info a the numpy array
    Input: grayscale images (output of loadImages function), directory for the images folder
    Output: dictionary including: retina images, rosa images,
            x,y, and radius of rosa center, numbers of the images in the directory
    """
    # 1st image has to be the retina, 2nd has to be the rosa.
    Thresh = np.mean(grayImageCollection)
    numberOfRosaImages = 0
    image = np.empty((1, grayImageCollection.shape[1], grayImageCollection.shape[2]), float)
    laserImage = np.empty((1, grayImageCollection.shape[1], grayImageCollection.shape[2]), float)
    temp = np.empty((1, grayImageCollection.shape[1], grayImageCollection.shape[2]), float)
    xCenter = np.array([])
    yCenter = np.array([])
    radius = np.array([])
    imageNumber = np.array([])

    for i in range(1, grayImageCollection.shape[0]):
        firstPicMeanValue = np.mean(grayImageCollection[i-1,:,:])
        secondPicMeanValue = np.mean(grayImageCollection[i,:,:])
        if (firstPicMeanValue > Thresh and secondPicMeanValue < Thresh):
            # The first picture is a retina image and the next one, a ROSA image.
            if (i < 10):
                loadLaserImage = collectionDir+'/00'+str(i)+"."+extension
            if (i >= 10 and i < 100):
                loadLaserImage = collectionDir+'/0'+str(i)+"."+extension
            if (i >= 100):
                loadLaserImage = collectionDir+"/"+str(i)+"."+extension
            blob = analyzeRosa(loadLaserImage)
            if (blob['found'] == True):
                temp[0,:,:] = grayImageCollection[i-1,:,:] # retina
                image = np.vstack((image, temp)) # retina
                temp[0,:,:] = grayImageCollection[i,:,:] # rosa
                laserImage = np.vstack((laserImage, temp)) # rosa
                numberOfRosaImages += 1
                # the following arrays are 1D
                xCenter = np.hstack((xCenter,int(blob['center']['x']*image.shape[2]))) # for the center of the rosa
                yCenter = np.hstack((yCenter,int(blob['center']['y']*image.shape[1]))) # for the center of the rosa
                radius = np.hstack((radius,int(blob['radius']*image.shape[1]))) # for the center of the rosa
                imageNumber = np.hstack((imageNumber, int(i-1))) # it's a 1D array
    if numberOfRosaImages == 0:
        raise ImportError("No laser spot was found. Try with different data.")
    image = np.delete(image, 0, axis=0) # remove the first initialized empty matrix
    laserImage = np.delete(laserImage, 0, axis=0) # remove the first initialized empty matrix
    imageDataDictionary = {
        "image": image,
        "laserImage": laserImage,
        "xCenter": xCenter,
        "yCenter": yCenter,
        "radius": radius,
        "imageNumber": imageNumber
    }
    return imageDataDictionary

def listFileNames(directory: str, extension="jpg") -> list:
    foundFiles = []
    for file in os.listdir(directory):
        if fnmatch.fnmatch(file, f'*.{extension}'):
            foundFiles.append(file)
    return foundFiles

def getFiles(directory: str, extension="jpg", newImages=True) -> list:
    sortedListOfFiles = np.sort(listFileNames(directory, extension))
    filteredFiles = []
    for fileIndex in range(len(sortedListOfFiles)):
        if (fileIndex + 3) % 3 == 0:
            if newImages:
                # to exclude files with retina and rosa circle at the same time
                continue
            else:
                # no file has to be removed
                filteredFiles.append(directory+"/"+sortedListOfFiles[fileIndex])
        else:
            filteredFiles.append(directory+"/"+sortedListOfFiles[fileIndex])
    return filteredFiles

def loadImages(collectionDir: str, leftEye=False, extension="jpg", newImages=True) -> np.ndarray:
    """
    This function gets the directory of a series of images
    Blue channel of the image = 0
    Output is a series of grayscale images
    """
    files = getFiles(collectionDir, extension=extension, newImages=newImages)
    imageCollection = imread_collection(files)# imports as RGB image
    if leftEye:
        temporaryCollection = []
        for image in imageCollection:
            temporaryCollection.append(mirrorImage(image))
        imageCollection = np.array(temporaryCollection)
    grayImage = np.zeros((len(imageCollection), imageCollection[0].shape[0], imageCollection[0].shape[1]))
    for i in range(len(imageCollection)):
        imageCollection[i][:,:,2] = 0
        grayImage[i,:,:] = rgb2gray(imageCollection[i])
    return grayImage

def seperateNewImages(grayImageCollection, collectionDir: str, extension="jpg") -> dict:
    """
    Purpose: seperate new retina images from new rosa images
    Load retina image - then load the corresponding rosa image 
    Check to find the rosa, if found, append the image and other info a the numpy array
    Input: grayscale images (output of loadImages function), directory for the images folder
    Output: dictionary including: retina images, rosa images,
            x,y, and radius of rosa center, numbers of the images in the directory
    """
    # 1st image has to be the retina, 2nd has to be the rosa.
    numberOfRosaImages = 0
    image = np.empty((1, grayImageCollection.shape[1], grayImageCollection.shape[2]), float)
    laserImage = np.empty((1, grayImageCollection.shape[1], grayImageCollection.shape[2]), float)
    temp = np.empty((1, grayImageCollection.shape[1], grayImageCollection.shape[2]), float)
    xCenter = np.array([])
    yCenter = np.array([])
    radius = np.array([])
    imageNumber = np.array([])

    sortedFileNames = np.sort(listFileNames(collectionDir, extension))
    files = getFiles(collectionDir, extension, newImages=True)
    # first pic = eye, 2nd pic = rosa
    for i in range(1, grayImageCollection.shape[0]):
        if "eye" in files[i-1]:
            loadLaserImage = files[i]
            blob = analyzeRosa(loadLaserImage)
            if (blob['found'] == True):
                numberOfRosaImages += 1
                currentImageNumber = int(sortedFileNames[i][:3].lstrip("0"))
                temp[0,:,:] = grayImageCollection[i-1,:,:] # retina
                image = np.vstack((image, temp)) # retina
                temp[0,:,:] = grayImageCollection[i,:,:] # rosa
                laserImage = np.vstack((laserImage, temp)) # rosa
                # the following arrays are 1D
                xCenter = np.hstack((xCenter, int(blob['center']['x']*image.shape[2]))) # for the center of the rosa
                yCenter = np.hstack((yCenter, int(blob['center']['y']*image.shape[1]))) # for the center of the rosa
                radius = np.hstack((radius, int(blob['radius']*image.shape[1]))) # for the center of the rosa
                imageNumber = np.hstack((imageNumber, currentImageNumber)) # it's a 1D array
    if numberOfRosaImages == 0:
        raise ImportError("No laser spot was found. Try with different data.")
    image = np.delete(image, 0, axis=0) # remove the first initialized empty matrix
    laserImage = np.delete(laserImage, 0, axis=0) # remove the first initialized empty matrix
    imageDataDictionary = {
        "image": image,
        "laserImage": laserImage,
        "xCenter": xCenter,
        "yCenter": yCenter,
        "radius": radius,
        "imageNumber": imageNumber
    }
    return imageDataDictionary

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
            ind = np.unravel_index(np.argmax(out1, axis=None), out1.shape)
            indexShift = np.vstack((indexShift, np.array(ind) - np.array([a.shape[1]/2, a.shape[2]/2])))
            totalShift = np.vstack((totalShift, np.sum(indexShift, axis=0)))
    return totalShift

def newFindImageShift():
    """
    Find the image shift with the new ellipse finding algorithm parameters.
    """
    pass

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

def placeRosa(gridParameters, shiftParameters, dataDictionary) -> list:
    xCenterGrid = gridParameters[0]
    yCenterGrid = gridParameters[1]
    length = gridParameters[2]
    xRosa = shiftParameters[0]
    yRosa = shiftParameters[1]
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
        imageDataDictionary = removeImagesFromIndex(dataDictionary, imageIndexesToRemove)
    else:
        imageDataDictionary = dataDictionary

    return outputLabels, imageDataDictionary, imageIndexesToRemove

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
    xShift = shiftParameters[0]
    xShift = np.delete(xShift, indexesToRemove)
    yShift = shiftParameters[1]
    yShift = np.delete(yShift, indexesToRemove)
    return xShift, yShift

def defineGrid(Image) -> tuple:
    # onh = optic nerve head
    temp = np.zeros(Image.shape)
    temp[np.where(Image >= np.mean(Image)*1.9)] = 1
    kernel = np.ones((5,5), np.uint8)
    openingTemp = cv2.morphologyEx(temp[0,:,:], cv2.MORPH_OPEN, kernel) # to reduce noise
    nonZero = np.nonzero(openingTemp)
    onhHeight = np.max(nonZero[0]) - np.min(nonZero[0])
    onhWidth = np.max(nonZero[1]) - np.min(nonZero[1])
    onhCenterVerticalCoords = int(((np.max(nonZero[0]) + np.min(nonZero[0]))/2) - (onhHeight-onhWidth))
    onhCenterHorizontalCoords = int((np.max(nonZero[1]) + np.min(nonZero[1]))/2)
    length = int((np.min([onhHeight, onhWidth]))/2)
    return onhCenterHorizontalCoords, onhCenterVerticalCoords, length
    # return xCenterGrid, yCenterGrid, length

def oldPlotResult(Image, shiftParameters, gridParameters, rosaRadius=30):
    xCenterGrid = gridParameters[0]
    yCenterGrid = gridParameters[1]
    length = gridParameters[2]
    xRosa = shiftParameters[0]
    yRosa = shiftParameters[1]

    color = (0, 255, 0)
    thickness = 5

    for j in range(xRosa.shape[0]):
        centerCoordinates = (int(xRosa[j]), int(yRosa[j]))
        image = cv2.circle(Image[0,:,:], centerCoordinates, rosaRadius, color, thickness)
    #plt.imsave("preimage2D.jpg", image) # same for old and new

    left = np.max([xCenterGrid - (length*5), 0])
    up = np.max([yCenterGrid - (length*5), 0])
    right = np.min([(5*length), (Image.shape[1] - xCenterGrid)]) + xCenterGrid
    down = right = np.min([(5*length), (Image.shape[2] - yCenterGrid)]) + yCenterGrid
    temp = Image[0,up:down, left:right]
    xNewCenter = xCenterGrid - left
    yNewCenter = yCenterGrid - up
    gridImage = np.zeros([length*10, length*10])
    # Set slicing limits:
    LOW_SLICE_Y = ((5*length) - yNewCenter)
    HIGH_SLICE_Y = ((5*length) + (temp.shape[0] - yNewCenter))
    LOW_SLICE_X = ((5*length) - xNewCenter)
    HIGH_SLICE_X = ((5*length) + (temp.shape[1] - xNewCenter))
    # Slicing:
    gridImage[LOW_SLICE_Y:HIGH_SLICE_Y, LOW_SLICE_X:HIGH_SLICE_X] = temp

    plt.figure()
    img = gridImage.copy()
    dx, dy = length, length
    # Custom (rgb) grid color:
    gridColor = 0
    # Modify the image to include the grid
    img[:,::dy] = gridColor
    img[::dx,:] = gridColor
    plt.imsave('Result_old.jpg', img)

def plotResult(image, shiftParameters, gridParameters,saturationsO2, rosaRadius=30, thickness=5,leftEye = False):
    refImage = image[0,:,:]
    imageRGB = makeImageRGB(refImage)
    rescaledImage, LowSliceX, LowSliceY = rescaleImage(imageRGB, gridParameters)
    rescaledImageWithCircles = drawRosaCircles(rescaledImage, shiftParameters,
                                LowSliceX, LowSliceY,saturaionsO2, rosaRadius=rosaRadius,
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

def drawRosaCircles(rescaledImage, shiftParameters, LowSliceX, LowSliceY,saturationO2, rosaRadius=30, thickness=10):
    xRosa = shiftParameters[0]
    yRosa = shiftParameters[1]
    for j in range(xRosa.shape[0]):
        color=(saturationO2[j]/100 , 0 , 1-(saturationO2[j]/100))
        centerCoordinates = (int(xRosa[j]) + LowSliceX, int(yRosa[j]) + LowSliceY)
        cv2.circle(rescaledImage, centerCoordinates, rosaRadius, color, thickness)
    return rescaledImage

def rescaleImage(imageRGB, gridParameters):
    xCenterGrid = gridParameters[0]# int
    yCenterGrid = gridParameters[1]# int
    length = gridParameters[2]# int
    left = np.max([xCenterGrid - (length*5), 0])
    up = np.max([yCenterGrid - (length*5), 0])
    right = np.min([(5*length), (imageRGB.shape[0] - xCenterGrid)]) + xCenterGrid
    down = right = np.min([(5*length), (imageRGB.shape[1] - yCenterGrid)]) + yCenterGrid

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
