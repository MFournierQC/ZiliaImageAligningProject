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



def analyzeSpectrums(monkey, eye, rlp):
    rawSpectra = db.getRawIntensities(monkey=monkey, eye=eye,rlp=rlp , timeline = 'baseline', region = 'onh')
    if rawSpectra is not None:
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
        print('concentration calculation Done!')
        return concentration
    else:
        return None

def getSO2ForAllRlp(eye,monkey):
    rlp=[2,4,6,14,24,34]
    O2=[]
    for number in rlp:
        print(number)
        temp = analyzeSpectrums(monkey=monkey, eye=eye, rlp=number)
        if temp is not None:
            O2 = np.concatenate((O2,temp),axis=0)
    print('number of spectra : ' , len(O2))
    return O2

def getRosaImages(eye,monkey):
    rlp = [2, 4, 6, 14, 24, 34]
    rosaImages=[]
    for number in rlp:
        loadedImages = db.getRGBImages(monkey=monkey, rlp = number ,  timeline='baseline 3', region='onh', content='rosa', eye=eye)
        if loadedImages is not None:
            rosaImages.append(loadedImages)
    print('number of rosa : ' , len(rosaImages))
    return rosaImages

################## for Comparing image numbers and spec ##########
# from scipy import stats
# OSbresil=getSO2ForAllRlp(eye = 'od' , monkey = 'Bresil')
# OSkenya=getSO2ForAllRlp(eye = 'od' , monkey = 'Kenya')
# OSbrwanda=getSO2ForAllRlp(eye = 'od' , monkey = 'Rwanda')
OSsomalie = getSO2ForAllRlp(eye = 'od' , monkey = 'Somalie')
print(len(OSsomalie))

rosaImages = getRosaImages(eye = 'od' , monkey = 'Somalie')
print(len(rosaImages))



# ################## for Comparing all right eye and all left eyes ##########
# from scipy import stats
# # OSbresil=getSO2ForAllRlp(eye = 'od' , monkey = 'Bresil')
# # OSkenya=getSO2ForAllRlp(eye = 'od' , monkey = 'Kenya')
# # OSbrwanda=getSO2ForAllRlp(eye = 'od' , monkey = 'Rwanda')
# OSsomalie=getSO2ForAllRlp(eye = 'od' , monkey = 'Somalie')
#
# F, p = stats.f_oneway(OSbrwanda, OSsomalie)
# print(F)
# print(p)
#
# print(stats.f_oneway(OSbrwanda, OSsomalie))


################## for Comparing two eyes for one monkey ############
# monkey='Somalie'
# OS=getSO2ForAllRlp(eye = 'os' , monkey = monkey)
# OD=getSO2ForAllRlp(eye = 'od' , monkey = monkey)
# # ODimages = db.getRGBImages(monkey=monkey , timeline='baseline 3', region='onh', eye='od')
# # print(len(ODimages))
#
# print('OS : ' , ' mean ' , np.mean(OS) , '+-' , np.std(OS) )
# print('OD : ' , ' mean ' , np.mean(OD) , '+-' , np.std(OD) )
#
# from scipy import stats
# print('ttest : ' , stats.ttest_ind(OS, OD, equal_var=False))
#
# print('now plot hist')
# n, bins, patches = plt.hist(OS, 50, range= (30,55), facecolor='g', alpha=0.75)
# plt.savefig('SomalieOS.png')
# plt.show()
#
# print('now plot hist')
# n, bins, patches = plt.hist(OD, 50, range= (30,55), facecolor='g', alpha=0.75)
# plt.savefig('SomalieOD.png')
# plt.show()



# rlp2BresilOS=
# rlp4BresilOS=analyzeSpectrums(monkey=monkey,eye=eye,rlp=4)
# rlp6BresilOS=analyzeSpectrums(monkey=monkey,eye=eye,rlp=6)
# # rlp24BresilOS=analyzeSpectrums(monkey=monkey,eye=eye,rlp=24)
# # rlp34BresilOS=analyzeSpectrums(monkey=monkey,eye=eye,rlp=34)
# print(len(rlp2BresilOS))
# print(len(rlp4BresilOS))
# print(len(np.concatenate((rlp2BresilOS,rlp4BresilOS,rlp6BresilOS),axis=0)))
# resultsToPlot=np.concatenate((rlp2BresilOS,rlp4BresilOS,rlp6BresilOS),axis=0)
# print('plot')
# n, bins, patches = plt.hist(resultsToPlot, 50, range= (30,55), facecolor='g', alpha=0.75)
# plt.savefig('KenyaOS.png')
# plt.show()
#
#
# eye = 'od'
#
# rlp2BresilOD=analyzeSpectrums(monkey=monkey,eye=eye,rlp=2)
# rlp4BresilOD=analyzeSpectrums(monkey=monkey,eye=eye,rlp=4)
# rlp6BresilOD=analyzeSpectrums(monkey=monkey,eye=eye,rlp=6)
# # rlp24BresilOS=analyzeSpectrums(monkey=monkey,eye=eye,rlp=24)
# # rlp34BresilOS=analyzeSpectrums(monkey=monkey,eye=eye,rlp=34)
# print(len(rlp2BresilOD))
# print(len(rlp6BresilOD))
# print(len(np.concatenate((rlp2BresilOD,rlp4BresilOD,rlp6BresilOD),axis=0)))
# resultsToPlot=np.concatenate((rlp2BresilOD,rlp4BresilOD,rlp6BresilOD),axis=0)
# print('plot')
# n, bins, patches = plt.hist(resultsToPlot,50, range= (30,55), facecolor='g', alpha=0.75)
# plt.savefig('KenyaOD.png')
# plt.show()
#
#
#
#
# # print(len(ONHInfo))
# #
# # totalNum=0
# # ValueNum=0
# # for num in range(len(ONHInfo)):
# #     # print(ONHInfo[num])
# #     totalNum=totalNum+1
# #     print(ONHInfo[num]['properties'])
# #     print(ONHInfo[num]['floatValues'])
# #     if ONHInfo[num]['properties'] is not None:
# #         ValueNum=ValueNum+1
# #
# #     print((ValueNum/2)/(totalNum/3))
# # print(totalNum/3)
# # print(print((ValueNum/2)/(totalNum/3)))
# #
# #
