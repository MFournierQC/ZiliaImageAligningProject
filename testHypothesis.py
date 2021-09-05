from processImages import *
from spectrumAnalysisFromDatabase import *
from displayResult import *
from processImagesFromDatabase import *
from zilia import *
import matplotlib.pyplot as plt
db = ZiliaDB()
componentsSpectra = '_components_spectra.csv'
whiteRefPath = "int75_WHITEREFERENCE.csv"
whiteRefBackground = "int75_LEDON_nothingInFront.csv"

# acquisition info
# monkey = 'bresil'
# rlp = 6
# timeline = 'baseline 2'
# region = 'onh'
# eye = 'od'

monkey = 'Bresil'
rlp = None
timeline = 'baseline 3'
region = 'onh'
eye = 'od'
limit= None
# analysis


# retinaImages = db.getGrayscaleEyeImages(monkey=monkey , rlp=rlp, timeline=timeline, region=region, eye=eye , limit = limit)
# rosaImages = db.getRGBImages(monkey=monkey , rlp=rlp, timeline=timeline, region=region, eye=eye, limit = limit)
# rosaAbsoluteXY=getRosaProperties(rosaImages)
# # useful info:  int(['center']['x']) , int(['center']['y']) , ['rradius'] , and ['found']
# shiftValueFromReferenceImage , imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)
# rosaLocationOnRefImage = applyShiftOnRosaCenter(rosaAbsoluteXY,shiftValueFromReferenceImage)
# refImage = findRefImage(imageIsValid , retinaImages)
# xONH,yONH,length = findOHNParamsInRefImage(refImage)
# absoluteRosaValue = calculateRosaDistanceFromOnhInRefImage (xONH, yONH , rosaLocationOnRefImage)
# print(absoluteRosaValue)
# print(len(absoluteRosaValue))

rawSpectra = db.getRawIntensities(rlp=rlp) #, timeline=timeline) #, region=region, eye=eye)
print(rawSpectra)
print(len(rawSpectra))
wavelengths = db.getWavelengths()
rawSpectraData = wavelengths, rawSpectra
darkRefData = db.getBackgroundIntensities(rlp=rlp)
whiteRefData = loadWhiteRef(whiteRefPath, whiteRefBackground)
whiteRef = formatWhiteRef(whiteRefData)
spectra = formatSpectra(rawSpectraData)
_, darkRefSpectra = darkRefData
darkRefData = wavelengths, darkRefSpectra
darkRef = formatDarkRef(darkRefData)
normalizedSpectrum = normalizeSpectrum(spectra, darkRef)
absorbance = absorbanceSpectrum(whiteRef, normalizedSpectrum)
croppedComponents = cropComponents(absorbance, componentsSpectra)
features = componentsToArray(croppedComponents)
coefficients = getCoefficients(absorbance, features)
concentration = getConcentration(coefficients)
print(concentration)
print(len(concentration))





# print(len(ONHInfo))
#
# totalNum=0
# ValueNum=0
# for num in range(len(ONHInfo)):
#     # print(ONHInfo[num])
#     totalNum=totalNum+1
#     print(ONHInfo[num]['properties'])
#     print(ONHInfo[num]['floatValues'])
#     if ONHInfo[num]['properties'] is not None:
#         ValueNum=ValueNum+1
#
#     print((ValueNum/2)/(totalNum/3))
# print(totalNum/3)
# print(print((ValueNum/2)/(totalNum/3)))
#
#
