import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

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


def display (firstEye, secondEye, firstSO2Matrix, secondSO2Matrix):
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].imshow(firstEye)
    axs[0, 0].set_title('first eye')
    axs[0, 0].axis('off')
    axs[0, 1].imshow(secondEye)
    axs[0, 1].set_title('second eye')
    axs[0, 1].axis('off')

    minValue,maxValue=colorMapRange(firstSO2Matrix,secondSO2Matrix)

    axs[1, 0].imshow(firstSO2Matrix,cmap=plt.cm.coolwarm, vmin =minValue, vmax = maxValue)
    axs[1, 0].set_title('saturated oxygen (1st eye)')
    axs[1, 0].axis('off')
    cmp = axs[1, 1].imshow(secondSO2Matrix,cmap=plt.cm.coolwarm, vmin =minValue, vmax = maxValue)
    axs[1, 1].set_title('saturated oxygen (2nd eye)')
    axs[1, 1].axis('off')
    fig.colorbar(cmp , ax=axs[1, :], location='bottom',shrink=0.6)
    plt.show()
    return None

def colorMapRange (firstImage,secondImage):
    minValue=np.min(np.array([np.min(firstImage),np.min(secondImage)]))
    maxValue = np.max(np.array([np.max(firstImage), np.max(secondImage)]))
    return minValue,maxValue

def matrixSO2(labels,saturationValues,leftEye=False):
    yLabel = np.array(['A', 'B', 'C', 'D', 'E', 'F', 'J', 'K', 'L', 'M'])
    xLabel = np.array(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    concentrationMatrix = np.zeros([10, 10])

    for i in range(saturationValues.shape[0]):
        splitLabel = np.array(list(labels[i]))

        concentrationMatrix[ int(np.where(np.array(splitLabel[0]) == xLabel)[0]),
            int(np.where(np.array(splitLabel[1]) == yLabel)[0])] =saturationValues[i]
    
    return concentrationMatrix


def testPlot():
    eye1=np.random.rand(1000,1000)
    eye2 = np.random.rand(1000, 1000)
    SO1 = np.random.rand(10, 10)
    SO2 = np.random.rand(10, 10)
    display(eye1,eye2,SO1,SO2)
    return None



################  OLD FUNCTIONS (DONT REMOVE THEM SVP)  ######################
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
