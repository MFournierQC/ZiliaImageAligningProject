from processImages import *
from spectrumAnalysis import *
from displayResult import *
from zilia import *


# New data:

# collectionDir="/Users/elahe/Documents/Bresil 1511184-20210525T145240Z-001/Bresil 1511184/20210316-100153-bresil-od-onh-rlp6"


# ziliaDb = 'zilia.db'
db = ZiliaDB()
retinaImages = db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh', eye='od')
rosaImages = db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh', content='rosa', eye='od')
print(len(retinaImages))
print(len(retinaImages))

# collectionDir = r"/Users/elahe/Documents/GitHub/Human acquisition/20210715-165559-og-scan-veineartere-rlp50"
#
# grayImage = loadImages(collectionDir, leftEye=False, newImages=True)
#
# ## change function name
# dataDictionary = seperateImages(grayImage, collectionDir)
# dataDictionary = removeBadImages(dataDictionary)
#
# image = dataDictionary["image"]
# laser = dataDictionary["laserImage"]
# xLaser = dataDictionary["xCenter"]
# yLaser = dataDictionary["yCenter"]
# rLaser = dataDictionary["radius"]
# imageNumber = dataDictionary["imageNumber"]
#
# print('image number' , imageNumber)
#
# indexShift = findImageShift(image)
# shiftParameters = applyShift(xLaser, yLaser, indexShift)
# gridParameters = defineGridParams(image)
#
# Label, dataDictionary, shiftParameters = getRosaLabels(gridParameters, shiftParameters, dataDictionary)
# print(Label)
#
# concentration, saturationFlag = mainAnalysis()
# print('max : ' , np.max(concentration) , 'min : ' , np.min(concentration))
#
# a= plotResult(image, shiftParameters, gridParameters,concentration)
#
# # so2 analysis
#
# SO2Dictionary=saveData(saturationFlag, concentration , imageNumber , Label)
#
# # label=np.array(['A1','B2','C3','B2','B2','A1'])
# # concentrationValues=np.array([1,2,3,4,5,1])
#
#
# meanC,lab=meanSO2(SO2Dictionary["oxygenSat"],SO2Dictionary["rosaLabel"])
#
# plotSO2_right= matrixSO2(lab,meanC)

# #######################
#
# collectionDir="/Users/elahe/Documents/Bresil 1511184-20210525T145240Z-001/Bresil 1511184/20210316-101640-bresil-os-onh-rlp6"
#
# leftEye = True
# newImages = True
#
# grayImage = loadImages(collectionDir, leftEye=leftEye, newImages=newImages)
# # dataDictionary = seperateImages(grayImage, collectionDir)
# dataDictionary = seperateImages(grayImage, collectionDir)
# dataDictionary = removeBadImages(dataDictionary)
#
# image = dataDictionary["image"]
# laser = dataDictionary["laserImage"]
# xLaser = dataDictionary["xCenter"]
# yLaser = dataDictionary["yCenter"]
# rLaser = dataDictionary["radius"]
# imageNumber = dataDictionary["imageNumber"]
#
# print('image number' , imageNumber)
#
# indexShift = findImageShift(image)
# shiftParameters = applyShift(xLaser, yLaser, indexShift)
# gridParameters = defineGridParams(image)
#
# Label, dataDictionary, shiftParameters = getRosaLabels(gridParameters, shiftParameters, dataDictionary)
# print(Label)
#
# concentration, saturationFlag = mainAnalysis()
#
# b= plotResult(image, shiftParameters, gridParameters,concentration,leftEye=True)
#
#
# # so2 analysis
#
#
# SO2Dictionary=saveData(saturationFlag, concentration , imageNumber , Label)
#
# meanC,lab=meanSO2(SO2Dictionary["oxygenSat"],SO2Dictionary["rosaLabel"])
# plotSO2_left= matrixSO2(lab,meanC,leftEye=True)
#
#
#
# display(a,b,plotSO2_right,plotSO2_left)
#
# # if file, all rosas place, find store uniqly!!!
# #insert into calculations (pah=th,key,value):
# #values ('/')
# """
# # onhCenterX
# # onhCenterY
# # onhHeight
# # onhWidth
# rosaCenterX
# rosaCentery
# rosaRadius
# displacementX
# displacementY
# reference
# gridX
# gridY
# isDark
#
# """

