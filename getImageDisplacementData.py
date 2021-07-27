from processImages import *
from zilia import *
from analyzeRetinaImages import *
from cv2 import cvtColor, COLOR_RGB2GRAY
import csv
import os
from skimage.color import rgb2gray

def computeRosaDisplacementForAllImages(imageDict):
    rosaAbsX = {}
    rosaAbsY = {}
    for path, image in imageDict.items():
        blob = findLaserSpot(image)
        if blob is None:
            rosaAbsX[path] = "NA"
            rosaAbsY[path] = "NA"
        else:
            rosaX = int(blob['center']['x']*image.shape[1])
            rosaY = int(blob['center']['y']*image.shape[0])
            rosaAbsX[path] = rosaX
            rosaAbsY[path] = rosaY
    return rosaAbsX, rosaAbsY

def findLaserSpot(inImage: np.ndarray):
    redChannel = getGrayMapFromRedChannel(inImage)
    maxRedChannel = np.max(redChannel)
    found, _, circleHeight, circleWidth, radius = findLaserSpotRecursive(redChannel, maxRedChannel, time_start)
    if not found:
        print("Laser not found")
        return None
    print("Laser found.")
    circleHeight, circleWidth, radius = fineTuneRosaDetection(redChannel, circleHeight, circleWidth, radius)
    blob = formatBlob(inImage, [circleHeight, circleWidth, radius, found])
    return blob

def getGrayMapFromRedChannel(inImage):
    image = inImage.astype(np.uint8)
    blue = image[:,:,2]
    red = image[:,:,0]
    redChannel = red >= blue

    grayLevelImg = cvtColor(image, COLOR_RGB2GRAY)
    outImage = redChannel*grayLevelImg
    outImage = outImage.astype(np.uint8)
    return outImage

def saveImageData(data, fileName="displacementData"):
    rawRosaXs, rawRosaYs, onhXShifts, onhYShifts, eyeImagePaths = data
    if os.path.exists(fileName+".csv"):
        # the file already exists
        fileMode = 'a'
    else:
        # the file must first be created
        fileMode = 'w'
    with open(fileName+'.csv', fileMode, newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(len(eyeImagePaths)):
            writer.writerow([eyeImagePaths[i], 'rosaAbsX', int(rawRosaXs[i])])
            writer.writerow([eyeImagePaths[i], 'rosaAbsY', int(rawRosaYs[i])])
            # writer.writerow([eyeImagePaths[i], 'onhAbsX', int(onhXShifts[i])])
            # writer.writerow([eyeImagePaths[i], 'onhAbsY', int(onhYShifts[i])])
