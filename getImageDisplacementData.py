from processImages import *
from zilia import *
from analyzeRosaImages import *
from cv2 import cvtColor, COLOR_RGB2GRAY
import time
import csv
import os
from skimage.color import rgb2gray

def computeRosaPositionForAllImages(imageDict):
    rosaAbsCoords = {}
    for path, image in imageDict.items():
        blob = findLaserSpot(image)
        if blob is None:
            rosaAbsCoords[path] = ("NA", "NA")
        else:
            rosaX = int(blob['center']['rx'])
            rosaY = int(blob['center']['ry'])
            rosaAbsCoords[path] = rosaX, rosaY
    return rosaAbsCoords

def saveRosaData(rosaAbsCoords: dict, fileName="displacementData"):
    if os.path.exists(fileName+".csv"):
        # the file already exists
        fileMode = 'a'
    else:
        # the file must first be created
        fileMode = 'w'
    with open(fileName+'.csv', fileMode, newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for path, coords in rosaAbsCoords.items():
            for path, valueY in rosaAbsXDict.items():
            writer.writerow([path, 'rosaAbsX', coords[0]])
            writer.writerow([path, 'rosaAbsY', coords[1]])

def findLaserSpot(inImage):
    redChannel = getGrayMapFromRedChannel(inImage)
    maxRedChannel = np.max(redChannel)
    startTime = time.time()
    found, _, circleHeight, circleWidth, radius = findLaserSpotRecursive(redChannel, maxRedChannel, startTime)
    if not found:
        print("Laser not found")
        return None
    print("Laser found.")
    circleHeight, circleWidth, radius = fineTuneRosaDetection(redChannel, circleHeight, circleWidth, radius)
    blobDict = formatBlob(inImage, [circleHeight, circleWidth, radius, found])
    return blobDict

def getGrayMapFromRedChannel(inImage):
    image = inImage.astype(np.uint8)
    blue = image[:,:,2]
    red = image[:,:,0]
    redChannel = red >= blue

    grayLevelImg = cvtColor(image, COLOR_RGB2GRAY)
    outImage = redChannel*grayLevelImg
    outImage = outImage.astype(np.uint8)
    return outImage
