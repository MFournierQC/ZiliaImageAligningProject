from processImages import *
from spectrumAnalysisFromDatabase import *
from displayResult import *
from processImagesFromDatabase import *
from zilia import *
import pickle
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
    rawSpectra = db.getRawIntensities(monkey=monkey, eye=eye,rlp=rlp , timeline = 'baseline 3', region = 'onh')
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

def getSO2ForAllRlp(eye,monkey , rlp):

    # rlp = [4]
    O2=[]
    for number in rlp:
        print(number)
        temp = analyzeSpectrums(monkey=monkey, eye=eye, rlp=number)
        if temp is not None:
            O2 = np.concatenate((O2,temp),axis=0)
    print('number of spectra : ' , len(O2))
    return O2

def getRosaImages(eye,monkey):
    rlp = [2, 4, 6, 14]
    # rlp = [4]
    rosaImages=[]
    retinaImages=[]
    for number in rlp:
        print('image , rlp ' , number)
        loadedRosaImages = db.getRGBImages(monkey=monkey, rlp = number ,  timeline='baseline 3', region='onh',
                                           content='rosa', eye=eye)
        loadedRetinaImages = db.getRGBImages(monkey=monkey, rlp=number, timeline='baseline 3', region='onh',
                                             content = 'eye' ,eye=eye)

        if loadedRosaImages:
            rosaImages=rosaImages+loadedRosaImages
            retinaImages=retinaImages+loadedRetinaImages
    rosaInfo = getRosaProperties(rosaImages)
    brightnessEye = [None] * len(rosaImages)
    for image in range(len(rosaImages)):
        if rosaInfo[image]['found']:

            # retinaImages[image][:,:,0]=256*((retinaImages[image][:,:,0]-np.min(retinaImages[image][:,:,0]))/
            #                      (np.max(retinaImages[image][:,:,0])-np.min(retinaImages[image][:,:,0])))
            # retinaImages[image][:,:,1] = 256 * ((retinaImages[image][:,:,1] - np.min(retinaImages[image][:,:,1])) /
            #                              (np.max(retinaImages[image][:,:,1]) - np.min(retinaImages[image][:,:,1])))
            # retinaImages[image][:,:,2] = 256 * ((retinaImages[image][:,:,2] - np.min(retinaImages[image][:,:,2])) /
            #                              (np.max(retinaImages[image][:,:,2]) - np.min(retinaImages[image][:,:,2])))
            brightnessEye[image] = np.mean(retinaImages[image][int(rosaInfo[image]['center']['x']) ,
                                                        int(rosaInfo[image]['center']['y'])])
    print('number of rosa : ' , len(rosaImages))
    print('size of brightness array' , len(brightnessEye))
    return brightnessEye

def getRosaCoordinates(eye,monkey,rlp):
    # rlp = [2, 4, 6, 14]

    # rosaImages=[]
    # retinaImages=[]
    rosaCoord=[]
    for number in rlp:
        print('image , rlp ' , number)
        rosaImages = db.getRGBImages(monkey=monkey, rlp = number ,  timeline='baseline 3', region='onh',
                                           content='rosa', eye=eye)
        retinaImages = db.getGrayscaleEyeImages(monkey=monkey, rlp=number, timeline='baseline 3', region='onh',
                                             eye=eye)

        if rosaImages :
            print(len(rosaImages))
            rosaAbsoluteXY = getRosaProperties(rosaImages)
            print(rosaAbsoluteXY)
            shiftValueFromReferenceImage, imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)
            rosaLocationOnRefImage = applyShiftOnRosaCenter(rosaAbsoluteXY, shiftValueFromReferenceImage)
            refImage = findRefImage(imageIsValid, retinaImages)
            xONH, yONH, length = findOHNParamsInRefImage(refImage)
            absoluteRosaValue = calculateRosaDistanceFromOnhInRefImage(xONH, yONH, rosaLocationOnRefImage)
            rosaCoord = rosaCoord + absoluteRosaValue


    return rosaCoord


########## save data
rlp=[2, 4, 6, 14]
monkey = 'Bresil'
eye = 'os'
rosas = getRosaCoordinates(eye = eye , monkey = monkey, rlp=rlp)
O2 = getSO2ForAllRlp(eye = eye , monkey = monkey, rlp=rlp)
with open("rosaBresilOS.txt", "wb") as fp:  # Pickling
    pickle.dump(rosas, fp)
with open("O2BresilOS.txt", "wb") as fp:  # Pickling
    pickle.dump(O2, fp)

eye = 'od'
rosas = getRosaCoordinates(eye = eye , monkey = monkey, rlp=rlp)
O2 = getSO2ForAllRlp(eye = eye , monkey = monkey, rlp=rlp)
with open("rosaBresilOD.txt", "wb") as fp:  # Pickling
    pickle.dump(rosas, fp)
with open("O2BresilOD.txt", "wb") as fp:  # Pickling
    pickle.dump(O2, fp)

#kenya

rlp=[2, 4, 6, 14,24,34]
monkey = 'Kenya'
eye = 'os'
rosas = getRosaCoordinates(eye = eye , monkey = monkey , rlp=rlp)
O2 = getSO2ForAllRlp(eye = eye , monkey = monkey, rlp=rlp)
with open("rosaKenyaOS.txt", "wb") as fp:  # Pickling
    pickle.dump(rosas, fp)
with open("O2KenyaOS.txt", "wb") as fp:  # Pickling
    pickle.dump(O2, fp)

eye = 'od'
rosas = getRosaCoordinates(eye = eye , monkey = monkey, rlp=rlp)
O2 = getSO2ForAllRlp(eye = eye , monkey = monkey, rlp=rlp)
with open("rosaKenyaOD.txt", "wb") as fp:  # Pickling
    pickle.dump(rosas, fp)
with open("O2KenyaOD.txt", "wb") as fp:  # Pickling
    pickle.dump(O2, fp)

# Rwanda

rlp=[2, 4, 6, 14,24,34]
monkey = 'Rwanda'
eye = 'os'
rosas = getRosaCoordinates(eye = eye , monkey = monkey, rlp=rlp)
O2 = getSO2ForAllRlp(eye = eye , monkey = monkey, rlp=rlp)
with open("rosaRwandaOS.txt", "wb") as fp:  # Pickling
    pickle.dump(rosas, fp)
with open("O2RwandaOS.txt", "wb") as fp:  # Pickling
    pickle.dump(O2, fp)

eye = 'od'
rosas = getRosaCoordinates(eye = eye , monkey = monkey, rlp=rlp)
O2 = getSO2ForAllRlp(eye = eye , monkey = monkey, rlp=rlp)
with open("rosaRwandaOD.txt", "wb") as fp:  # Pickling
    pickle.dump(rosas, fp)
with open("O2RwandaOD.txt", "wb") as fp:  # Pickling
    pickle.dump(O2, fp)

# somalie

rlp=[2, 4, 6, 14,24,34]
monkey = 'Somalie'
eye = 'os'
rosas = getRosaCoordinates(eye = eye , monkey = monkey, rlp=rlp)
O2 = getSO2ForAllRlp(eye = eye , monkey = monkey, rlp=rlp)
with open("rosaSomalieOS.txt", "wb") as fp:  # Pickling
    pickle.dump(rosas, fp)
with open("O2SomalieOS.txt", "wb") as fp:  # Pickling
    pickle.dump(O2, fp)

eye = 'od'
rosas = getRosaCoordinates(eye = eye , monkey = monkey, rlp=rlp)
O2 = getSO2ForAllRlp(eye = eye , monkey = monkey, rlp=rlp)
with open("rosaSomalieOD.txt", "wb") as fp:  # Pickling
    pickle.dump(rosas, fp)
with open("O2SomalieOD.txt", "wb") as fp:  # Pickling
    pickle.dump(O2, fp)

# import imageio
# imageRef = imageio.imread('../referenceONH.png')
#
# def deleteFromList(rosa,O2):
#     l=[i for i,v in enumerate(rosa) if v is not None]
#     newRosa = [rosa[j] for j in l]
#     newO2 = [O2[j] for j in l]
#     return newRosa,newO2
#
# with open("rosaBresilOD.txt", "rb") as fp:   # Unpickling
#     rosaBresilOD = pickle.load(fp)
# with open("O2BresilOD.txt", "rb") as fp:   # Unpickling
#     O2BresilOD = pickle.load(fp)
#
#
#
#
# with open("rosaBresilOS.txt", "rb") as fp:   # Unpickling
#     rosaBresilOS = pickle.load(fp)
# with open("O2BresilOS.txt", "rb") as fp:   # Unpickling
#     O2BresilOS = pickle.load(fp)
#
# print(rosaBresilOS)
#
# with open("rosaKenyaOD.txt", "rb") as fp:   # Unpickling
#     rosaKenyaOD = pickle.load(fp)
# with open("O2KenyaOD.txt", "rb") as fp:   # Unpickling
#     O2KenyaOD = pickle.load(fp)
#
#
# rosaKenyaOD,O2KenyaOD = deleteFromList(rosaKenyaOD,O2KenyaOD)
# print(rosaKenyaOD)
# print(np.asarray(rosaKenyaOD)+1000)




################## for Comparing image numbers and spec ##########
# monkey = 'Bresil'
# eye = 'os'
# O2 = getSO2ForAllRlp(eye = eye , monkey = monkey)
# brightnessarray = getRosaImages(eye = eye , monkey = monkey)

# print(O2)
# print(brightnessarray)

# n = [i for i in range(len(brightnessarray)) if brightnessarray[i] =! None]
# del brightnessarray[int(n)]
# print(brightnessarray)
# newBright=brightnessarray.pop(n)
# newO2=O2.pop(n)
# plt.plot(O2,brightnessarray, 'ro')
# plt.ylabel('brightness')
# plt.xlabel('O2')
# plt.show()


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
