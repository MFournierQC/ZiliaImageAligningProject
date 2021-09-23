# from processImages import *
# from spectrumAnalysis import *
# from displayResult import *
from processImagesFromDatabase import *
from zilia import *
import matplotlib.pyplot as plt

eye='od'
db = ZiliaDB()
retinaImages = db.getGrayscaleEyeImages(monkey='Kenya', rlp=2, timeline='baseline 3', region='onh', eye=eye )
rosaImages = db.getRGBImages(monkey='Kenya', rlp=2, timeline='baseline 3', region='onh', content='rosa', eye=eye )

rosaAbsoluteXY=getRosaProperties(rosaImages)
# useful info:  int(['center']['x']) , int(['center']['y']) , ['rradius'] , and ['found']

shiftValueFromReferenceImage , imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)
print(shiftValueFromReferenceImage)

rosaLocationOnRefImage = applyShiftOnRosaCenter(rosaAbsoluteXY,shiftValueFromReferenceImage)

# print(imageIsValid)
refImage = findRefImage(imageIsValid , retinaImages)

xONH,yONH,length = findOHNParamsInRefImage(refImage)

absoluteRosaValue = calculateRosaDistanceFromOnhInRefImage (xONH, yONH , rosaLocationOnRefImage)

# print(absoluteRosaValue)

# shift = calculateShiftInOneAcquisition (retinaImages)
# # Calculate shifts regarding the first good image in an acquisition

