from processImages import *
from spectrumAnalysis import *
from displayResult import *

# New data:
# collectionDir = r"./tests/TestImages/miniTestSampleNewData"
collectionDir="/Users/elahe/Documents/Bresil 1511184-20210525T145240Z-001/Bresil 1511184/20210316-100153-bresil-od-onh-rlp6"

# Test plot directory
# collectionDir = r"./tests/TestImages/testPlot"

# Backup USB on Mac OS:
# collectionDir = r"/Volumes/DATA BACKUP/Baseline3/Bresil 1511184/20210316-100153-bresil-od-onh-rlp6"

# More new data that looks half decent...:
# collectionDir = r"E:\Baseline3\Kenya\20210316-144549-kenya-os-onh-rlp6-20210525T141349Z-001\20210316-144549-kenya-os-onh-rlp6"

# More new data that looks bad:
# collectionDir = r"E:\Baseline3\Kenya\20210316-141909-kenya-od-onh-rlp2-20210525T144923Z-001\20210316-141909-kenya-od-onh-rlp2"

# Partial new data that looks ok:
# collectionDir = r"C:\Users\elm77\OneDrive\Documents\ULaval\2021_2_Ete\CERVO\Projet\code\sampleFromBaseline3"

# 521 files:
# collectionDir = r"C:\Users\elm77\OneDrive\Documents\ULaval\2021_2_Ete\CERVO\Projet\code\20210316-144549-kenya-os-onh-rlp6"

# Broken test dir:
# collectionDir = r"C:\Users\elm77\OneDrive\Documents\ULaval\2021_2_Ete\CERVO\Projet\code\brokenTest"

## right eye image analysis

leftEye = False
newImages = True

grayImage = loadImages(collectionDir, leftEye=leftEye, newImages=newImages)

## change function name
dataDictionary = seperateImages(grayImage, collectionDir)
dataDictionary = removeBadImages(dataDictionary)

image = dataDictionary["image"]
laser = dataDictionary["laserImage"]
xLaser = dataDictionary["xCenter"]
yLaser = dataDictionary["yCenter"]
rLaser = dataDictionary["radius"]
imageNumber = dataDictionary["imageNumber"]

print('image number' , imageNumber)

indexShift = findImageShift(image)
shiftParameters = applyShift(xLaser, yLaser, indexShift)
gridParameters = defineGrid(image)

Label, dataDictionary, shiftParameters = getRosaLabels(gridParameters, shiftParameters, dataDictionary)
print(Label)

concentration, saturationFlag = mainAnalysis()

a= plotResult(image, shiftParameters, gridParameters,concentration)

# so2 analysis

SO2Dictionary=saveData(saturationFlag, concentration , imageNumber , Label)

# label=np.array(['A1','B2','C3','B2','B2','A1'])
# concentrationValues=np.array([1,2,3,4,5,1])


meanC,lab=meanSO2(SO2Dictionary["oxygenSat"],SO2Dictionary["rosaLabel"])
plotSO2_right= matrixSO2(lab,meanC)

#######################

collectionDir="/Users/elahe/Documents/Bresil 1511184-20210525T145240Z-001/Bresil 1511184/20210316-101640-bresil-os-onh-rlp6"

leftEye = True
newImages = True

grayImage = loadImages(collectionDir, leftEye=leftEye, newImages=newImages)
# dataDictionary = seperateImages(grayImage, collectionDir)
dataDictionary = seperateImages(grayImage, collectionDir)
dataDictionary = removeBadImages(dataDictionary)

image = dataDictionary["image"]
laser = dataDictionary["laserImage"]
xLaser = dataDictionary["xCenter"]
yLaser = dataDictionary["yCenter"]
rLaser = dataDictionary["radius"]
imageNumber = dataDictionary["imageNumber"]

print('image number' , imageNumber)

indexShift = findImageShift(image)
shiftParameters = applyShift(xLaser, yLaser, indexShift)
gridParameters = defineGridParams(image)

Label, dataDictionary, shiftParameters = getRosaLabels(gridParameters, shiftParameters, dataDictionary)
print(Label)

concentration, saturationFlag = mainAnalysis()

b= plotResult(image, shiftParameters, gridParameters,concentration,leftEye=True)


# so2 analysis


SO2Dictionary=saveData(saturationFlag, concentration , imageNumber , Label)

meanC,lab=meanSO2(SO2Dictionary["oxygenSat"],SO2Dictionary["rosaLabel"])
plotSO2_left= matrixSO2(lab,meanC,leftEye=True)



display(a,b,plotSO2_right,plotSO2_left)

# if file, all rosas place, find store uniqly!!!
#insert into calculations (pah=th,key,value):
#values ('/')
"""
# onhCenterX
# onhCenterY
# onhHeight
# onhWidth
rosaCenterX
rosaCentery
rosaRadius
displacementX
displacementY
reference
gridX
gridY
isDark

"""