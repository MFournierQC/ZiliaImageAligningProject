from processImages import *
from spectrumAnalysis import *
from displayResult import *
from processImagesFromDatabase import *
from zilia import *
import matplotlib.pyplot as plt

eye='os'

db = ZiliaDB()
retinaImages = db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh', eye=eye)
rosaImages = db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh', content='rosa', eye=eye)

rosaAbsoluteXY=getRosaProperties(rosaImages)
# useful info:  int(['center']['x']) , int(['center']['y']) , ['rradius'] , and ['found']

print(rosaAbsoluteXY[10]['found'])

shiftValueFromReferenceImage , imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)

sr = applyShiftOnRosaCenter(rosaAbsoluteXY,shiftValueFromReferenceImage)
print(sr)

# shift = calculateShiftInOneAcquisition (retinaImages)
# # Calculate shifts regarding the first good image in an acquisition
# print(shift)
#
#

########
# what else to consider?
# remove dark images? (it was there before but where is it now??)


## OLD FUNCTIONS
# collectionDir = r"/Users/elahe/Documents/GitHub/Human acquisition/20210715-165559-og-scan-veineartere-rlp50"
# grayImage = loadImages(collectionDir, leftEye=False, newImages=True)
## change function name
# dataDictionary = seperateImages(grayImage, collectionDir)
# dataDictionary = removeBadImages(dataDictionary)
# image = dataDictionary["image"]
# laser = dataDictionary["laserImage"]
# xLaser = dataDictionary["xCenter"]
# yLaser = dataDictionary["yCenter"]
# rLaser = dataDictionary["radius"]
# imageNumber = dataDictionary["imageNumber"]
# indexShift = findImageShift(image)
# shiftParameters = applyShift(xLaser, yLaser, indexShift)
# gridParameters = defineGridParams(image)
# Label, dataDictionary, shiftParameters = getRosaLabels(gridParameters, shiftParameters, dataDictionary)
# concentration, saturationFlag = mainAnalysis()
# a= plotResult(image, shiftParameters, gridParameters,concentration)
# # so2 analysis
# SO2Dictionary=saveData(saturationFlag, concentration , imageNumber , Label)
# meanC,lab=meanSO2(SO2Dictionary["oxygenSat"],SO2Dictionary["rosaLabel"])
# plotSO2_right= matrixSO2(lab,meanC)
# #######################
# display(a,b,plotSO2_right,plotSO2_left)
