import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import cv2

### what variables i can have as input:
# 1. ref image
# 2. absolute X,Y rosa regarding the location of ONH center
# 3. size of ONH (width, length) and its center
# 4. what is the size of the grid?

### what functions do i need?
# 1. the gray to rgb for plotting
# 2. adding grid to the images
# 3. adding rosa circles to the image
# 4. giving a label to the rosa circles so they can be averaged to plot a map
# 5. relating StO2 values to the rosa locations


def display(firstEyeImage, secondEyeImage, firstSO2Matrix, secondSO2Matrix, xCoordinatesOS, yCoordinatesOS, xCoordinatesOD, yCoordinatesOD, saturationValuesOS, saturationValuesOD):
    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    axs[0, 0].imshow(firstEyeImage)
    axs[0, 0].scatter(xCoordinatesOS, yCoordinatesOS, c=saturationValuesOS, cmap=plt.cm.coolwarm)
    axs[0, 0].set_title('First eye')
    axs[0, 0].axis('off')
    axs[0, 1].imshow(secondEyeImage)
    axs[0, 1].scatter(xCoordinatesOD, yCoordinatesOD, c=saturationValuesOD, cmap=plt.cm.coolwarm)
    axs[0, 1].set_title('Second eye')
    axs[0, 1].axis('off')

    minValue, maxValue = colorMapRange(firstSO2Matrix, secondSO2Matrix)

    axs[1, 0].imshow(firstSO2Matrix, cmap=plt.cm.coolwarm, vmin=minValue, vmax=maxValue)
    axs[1, 0].set_title('Oxygen saturation (1st eye)')
    axs[1, 0].axis('off')
    cmp = axs[1, 1].imshow(secondSO2Matrix, cmap=plt.cm.coolwarm, vmin=minValue, vmax=maxValue)
    axs[1, 1].set_title('Oxygen saturation (2nd eye)')
    axs[1, 1].axis('off')
    fig.colorbar(cmp, ax=axs[1,:], location='bottom', shrink=0.6)
    plt.show()

def colorMapRange(firstImage, secondImage):
    minValue = np.min(np.array([np.min(firstImage), np.min(secondImage)]))
    maxValue = np.max(np.array([np.max(firstImage), np.max(secondImage)]))
    return minValue, maxValue

def getOxygenSatMatrix(labels, saturationValues, gridsize=(10,10)):
    assert len(labels) == len(saturationValues), "The number of labels must be the same as the number of oxygen saturation values."
    assert gridsize[0] == gridsize[1], "The gridsize has to be the same on both axis."
    assert gridsize[0] % 2 == 0, "The gridsize has to be an even number."
    xLabel = np.array([i for i in range(gridsize[0])])
    yLabel = np.array([i for i in range(gridsize[1])])
    # yLabel = np.array(['A', 'B', 'C', 'D', 'E', 'F', 'J', 'K', 'L', 'M'])
    # xLabel = np.array(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    concentrationMatrix = np.zeros(gridsize)
    saturationLocation = {}

    for i in range(len(saturationValues)):
        if labels[i] == None or saturationValues[i] == None:
            continue
        yIndex = np.where(np.array(labels[i][1]) == yLabel)[0]
        xIndex = np.where(np.array(labels[i][0]) == xLabel)[0]
        index = (int(yIndex), int(xIndex))
        if index in saturationLocation.keys():
            saturationLocation[index].append(saturationValues[i])
        else:
            saturationLocation[index] = list([saturationValues[i]])
        currentValue = concentrationMatrix[yIndex, xIndex][0]

    for index, sat in saturationLocation.items():
        concentrationMatrix[index] = np.mean(sat)

    return concentrationMatrix

def cleanResultValuesAndLocation(shiftParameters, lowSliceX, lowSliceY, saturationO2, gridParameters):
    xCenterGrid = gridParameters[0]# int
    yCenterGrid = gridParameters[1]# int
    length = gridParameters[2]# int
    shiftParameters = np.array(shiftParameters)
    indexes = np.where(shiftParameters != None)
    shiftParameters = shiftParameters[indexes]
    saturationO2 = saturationO2[indexes]
    normalizedSaturation = (saturationO2-np.min(saturationO2))/(np.max(saturationO2)-np.min(saturationO2))

    xCoordinates = []
    yCoordinates = []

    for j, coords in enumerate(list(shiftParameters)):
        x = int(coords[0]) + lowSliceX + xCenterGrid
        y = int(coords[1]) + lowSliceY + yCenterGrid
        xCoordinates.append(x)
        yCoordinates.append(y)

    return xCoordinates, yCoordinates, saturationO2, normalizedSaturation

def testPlot():
    eye1 = np.random.rand(1000, 1000)
    eye2 = np.random.rand(1000, 1000)
    SO1 = np.random.rand(10, 10)
    SO2 = np.random.rand(10, 10)
    display(eye1, eye2, SO1, SO2)



################  OLD FUNCTIONS (DONT REMOVE THEM SVP)  ######################
def getRosaLabels(gridParameters, rosaLocationOnRefImage, gridsize=(10,10)):
    assert gridsize[0] == gridsize[1], "The gridsize has to be the same on both axis."
    assert gridsize[0] % 2 == 0, "The gridsize has to be an even number."
    xCenterGrid = gridParameters[0]
    yCenterGrid = gridParameters[1]
    length = gridParameters[2]
    # rosaLocationOnRefImage = np.array(rosaLocationOnRefImage)[np.where(rosaLocationOnRefImage != None)]
    xLabel = np.array([i for i in range(gridsize[0])])
    yLabel = np.array([i for i in range(gridsize[1])])
    # xLabel = np.array(['1','2','3','4','5','6','7','8','9','10'])
    # yLabel = np.array(['A','B','C','D','E','F','J','K','L','M'])
    xRosa = []
    yRosa = []
    for i in rosaLocationOnRefImage:
        try:
            xRosa.append(i[0])
            yRosa.append(i[1])
        except TypeError: # Means the value is None
            xRosa.append(None)
            yRosa.append(None)

    xHalfGrid = int(gridsize[0]/2)
    xGrid = np.array(range(-xHalfGrid*length, xHalfGrid*length))
    xlabel = np.array( ["" for x in range(xGrid.shape[0])])
    for x in range(xLabel.shape[0]):
        xlabel[x*length:(x+1)*length] = xLabel[x]

    yHalfGrid = int(gridsize[1]/2)
    yGrid = np.array(range(-yHalfGrid*length, yHalfGrid*length))
    ylabel = np.array( ["" for x in range(yGrid.shape[0])])
    for y in range(yLabel.shape[0]):
        ylabel[y*length:(y+1)*length] = yLabel[y]

    outputLabels = []

    # The following line takes for granted the grid is a square!
    for j in range(len(xRosa)):
        if xRosa[j] == None or yRosa[j] == None:
            outputLabels.append(None)
        else:
            xTemporaryLabel = xlabel[ np.where(xGrid == xRosa[j] - xCenterGrid)[0] ]
            xTemporaryLabel = int(xTemporaryLabel[0])
            yTemporaryLabel = ylabel[ np.where(yGrid == yRosa[j] - yCenterGrid)[0] ]
            yTemporaryLabel = int(yTemporaryLabel[0])
            temporaryLabel = (xTemporaryLabel, yTemporaryLabel)
            outputLabels.append(temporaryLabel)

    return outputLabels

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

# def findNearest(array, value):
#     idx = (np.abs(array - value)).argmin()
#     return idx

def plotResult(image, shiftParameters, gridParameters, saturationsO2, rosaRadius=4, thickness=8, leftEye=False):
    print("Preparing plot of the result")
    if len(image.squeeze().shape) == 3:
        refImage = image[0,:,:]
    else:
        refImage = image
    imageRGB = makeImageRGB(refImage)
    rescaledImage, LowSliceX, LowSliceY = rescaleImage(imageRGB, gridParameters)
    rescaledImageWithCircles = rescaledImage
    # rescaledImageWithCircles = drawRosaCircles(rescaledImage, shiftParameters,
    #                             LowSliceX, LowSliceY, saturationsO2, gridParameters, rosaRadius=rosaRadius,
    #                             thickness=thickness)
    resultImageWithGrid = drawGrid(rescaledImageWithCircles, gridParameters)
    if (leftEye == False):
        return resultImageWithGrid
        # plt.imsave('Result.jpg', resultImageWithGrid)
    if (leftEye == True):
        # Result image has to be mirrored
        return resultImageWithGrid[:,::-1]
        # plt.imsave('Result.jpg', mirrorImage(resultImageWithGrid))

def makeImageRGB(grayImage):
    imageRGB = np.dstack((grayImage, grayImage, grayImage))
    return imageRGB

def drawRosaCircles(rescaledImage, shiftParameters, lowSliceX, lowSliceY, saturationO2, gridParameters, rosaRadius=4, thickness=8):
    xCenterGrid = gridParameters[0]# int
    yCenterGrid = gridParameters[1]# int
    length = gridParameters[2]# int
    shiftParameters = np.array(shiftParameters)
    indexes = np.where(shiftParameters != None)
    shiftParameters = shiftParameters[indexes]
    saturationO2 = saturationO2[indexes]
    normalizedSaturation = (saturationO2-np.min(saturationO2))/(np.max(saturationO2)-np.min(saturationO2))
    for j, coords in enumerate(list(shiftParameters)):
        color = (normalizedSaturation[j] , 0 , 1-normalizedSaturation[j])
        x = int(coords[0]) + lowSliceX + xCenterGrid
        y = int(coords[1]) + lowSliceY + yCenterGrid
        centerCoordinates = (x, y)
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

def drawGrid(imageRGB, gridParameters, gridsize=(10,10)):
    assert gridsize[0] == gridsize[1], "The gridsize has to be the same on both axis."
    # assert gridsize[0] % 2 == 0, "The gridsize has to be an even number."
    assert gridsize[0] % 10 == 0, "The gridsize has to be a multiple of 10."
    length = gridParameters[2]
    stepsize = gridsize[0]
    length = length//(stepsize//10)
    dx, dy = length, length
    # Custom (rgb) grid color:
    gridColor = 1
    # Modify the image to include the grid
    imageRGB[:,::dx,:] = gridColor
    imageRGB[::dy,:,:] = gridColor
    return imageRGB
