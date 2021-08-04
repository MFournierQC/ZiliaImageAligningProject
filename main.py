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

dark = findDarkImages(retinaImages)

rosaAbsoluteXY=getRosaProperties(rosaImages)
# useful info:  int(['center']['x']) , int(['center']['y']) , ['rradius'] , and ['found']

shiftValueFromReferenceImage , imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)

rosaLocationOnRefImage = applyShiftOnRosaCenter(rosaAbsoluteXY,shiftValueFromReferenceImage)

refImage = findRefImage(imageIsValid , retinaImages)

xONH,yONH,length = findRosaParamsInRefImage(refImage)

absoluteRosaValue = calculateRosaDistanceFromOnhInRefImage (xONH, yONH , rosaLocationOnRefImage)

# shift = calculateShiftInOneAcquisition (retinaImages)
# # Calculate shifts regarding the first good image in an acquisition

