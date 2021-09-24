from spectrumAnalysisFromDatabase import *
from processImagesFromDatabase import *
from detectONH import *
from zilia import *
import pickle
import matplotlib.pyplot as plt
db = ZiliaDB()
componentsSpectra = '_components_spectra.csv'
whiteRefPath = "int75_WHITEREFERENCE.csv"
whiteRefBackground = "int75_LEDON_nothingInFront.csv"


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
    O2=[]
    for number in rlp:
        print(number)
        temp = analyzeSpectrums(monkey=monkey, eye=eye, rlp=number)
        if temp is not None:
            O2 = np.concatenate((O2,temp),axis=0)
    print('number of spectra : ' , len(O2))
    return O2

def getRosaPosition (eye, monkey, rlp):
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
    xONHFound = [None] * len(rosaImages)
    yONHFound = [None] * len(rosaImages)
    xROSAFound = [None] * len(rosaImages)
    yROSAFound = [None] * len(rosaImages)
    widthFound = [None] * len(rosaImages)
    heightFound = [None] * len(rosaImages)
    for image in range(len(rosaImages)):
        if rosaInfo[image] is not None:
            if rosaInfo[image]['found']:
                xONHFound[image], yONHFound[image], widthFound[image], heightFound[image] = getPropertiesForImage(retinaImages[image])
                if xONHFound[image][0] !=  []:
                    xROSAFound[image] = int(rosaInfo[image]['center']['rx'] - xONHFound[image][0])
                    yROSAFound[image] = int(rosaInfo[image]['center']['ry'] - widthFound[image][0])
        print(image)
    return xROSAFound, yROSAFound, widthFound, heightFound

rlp=[4]
monkey = 'Bresil'
eye = 'os'
xROSAFound, yROSAFound, widthFound, heightFound = getRosaPosition(eye = eye , monkey = monkey, rlp=rlp)
print(xROSAFound)
print('done')

O2 = getSO2ForAllRlp(eye = eye , monkey = monkey, rlp=rlp)

print(O2)

