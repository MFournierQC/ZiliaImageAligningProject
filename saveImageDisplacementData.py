from processImages import *
from zilia import *
import csv
from os import path

def computeDisplacementForAllImages(dirPath, removeBadIm=True):
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
    if path.exists(fileName+".csv"):
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
            # writer.writerow([eyeImagePaths[i], 'onhXShift', int(onhXShifts[i])])
            # writer.writerow([eyeImagePaths[i], 'onhYShift', int(onhYShifts[i])])

def getPathsFromImageNumbers(dirPath, imageNumbers):
    paths = []
    for i in imageNumbers:
        if len(str(i)) == 1:
            path = dirPath+"/00"+str(i)+"-eye.jpg"
            paths.append(path.replace("\\", "/"))
        if len(str(i)) == 2:
            path = dirPath+"/0"+str(i)+"-eye.jpg"
            paths.append(path.replace("\\", "/"))
        if len(str(i)) == 3:
            path = dirPath+"/"+str(i)+"-eye.jpg"
            paths.append(path.replace("\\", "/"))
    return paths
