from processImages import *
from zilia import *
from analyzeRetinaImages import *
from cv2 import cvtColor, COLOR_RGB2GRAY
import csv
import os
from skimage.color import rgb2gray

def computeDisplacementForAllImages(imageDict):
    rosaAbsX = {}
    rosaAbsY = {}
    for path, image in imageDict.items():
        image = 



def findLaserSpot(inImage: np.ndarray):
    redChannel = getGrayMapFromRedChannel(inImage)
    maxValueRedChannel = np.max(redChannel)
    found, _, circleHeight, circleWidth, radius = findLaserSpotRecursive(
        redChannel, maxValueRedChannel, time_start)
    if found:
        circleHeight, circleWidth, fine_tuned_radius = fineTuneRosaDetection(redChannel, circleHeight, circleWidth, radius)
        radius = fine_tuned_radius
    else:
        return None, False
    blob = formatBlob(inImage, [circleHeight, circleWidth, radius, found])
    laserFound = "Laser found" if found else "Laser NOT found"
    print(laserFound)
    return blob, found

def getGrayMapFromRedChannel(inImage):
    image = inImage.astype(np.uint8)
    blue = image[:,:,2]
    red = image[:,:,0]
    redChannel = red >= blue

    grayLevelImg = cvtColor(image, COLOR_RGB2GRAY)
    outImage = redChannel*grayLevelImg
    outImage = outImage.astype(np.uint8)
    return outImage


def oldComputeDisplacementForAllImages(dirPath, removeBadIm=True):
    """
    The goal is to save a csv file with the following columns:
    filePath, properties, values
    The properties will be computed for each file, and will be the following:
    rawRosaX, rawRosaY, onhXShift, onhYShift
    """
    grayImages = loadImages(dirPath)
    dataDictionary = seperateImages(grayImages, dirPath)
    if removeBadIm:
        dataDictionary = removeBadImages(dataDictionary)
    rawRosaXs = dataDictionary["xCenter"]
    rawRosaYs = dataDictionary["yCenter"]
    grayImages = dataDictionary["image"]
    imageNumbers = dataDictionary["imageNumber"]
    shiftParams = findImageShift(grayImages)
    onhXShifts, onhYShifts = shiftParams[:,1], shiftParams[:,0]
    eyeImagePaths = getPathsFromImageNumbers(dirPath, imageNumbers)
    return rawRosaXs, rawRosaYs, onhXShifts, onhYShifts, eyeImagePaths

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

def getPathsFromImageNumbers(dirPath, imageNumbers):
    paths = []
    for i in imageNumbers:
        if len(str(i)) == 1:
            path = dirPath+"/00"+str(i)+"-eye.jpg"
            paths.append(os.path.replace("\\", "/"))
        if len(str(i)) == 2:
            path = dirPath+"/0"+str(i)+"-eye.jpg"
            paths.append(os.path.replace("\\", "/"))
        if len(str(i)) == 3:
            path = dirPath+"/"+str(i)+"-eye.jpg"
            paths.append(os.path.replace("\\", "/"))
    return paths
