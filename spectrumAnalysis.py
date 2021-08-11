import pandas as pd
import numpy as np
import tkinter as tk
from tkinter.filedialog import askopenfilename
from scipy.optimize import nnls
import matplotlib.pyplot as plt

#global variables for cropping wavelength
lowerLimitNormalization = 510
upperLimitNormalization = 590
lowerLimitOximetry = 530
upperLimitOximetry = 585
saturatedValue = 65535


# These 3 will always be the same for every test
whiteRefName = r"int75_WHITEREFERENCE.csv"
refNameNothinInfront = r"int75_LEDON_nothingInFront.csv"
componentsSpectraGlobal = r'_components_spectra.csv'

# whiteRefName = '/Users/elahe/Documents/GitHub/Human acquisition/1104_whiteRef.csv'
# refNameNothinInfront = '/Users/elahe/Documents/GitHub/Human acquisition/spectro_data_DARKRLP60.csv'


class Spectrum:
    data = np.array([])
    wavelength = np.array([])

def loadComponentsSpectra(componentsSpectra):
    '''load components spectrums for the analysis'''
    spectrumComponents = pd.read_csv(componentsSpectra)
    npComponents = spectrumComponents.to_numpy()
    wavelengths = npComponents[:,0]
    oxyhemoglobin = npComponents[:,1]
    deoxyhemoglobin = npComponents[:,2]
    methemoglobin = npComponents[:,3]
    carboxyhemoglobin = npComponents[:,4]
    eumelanin = npComponents[:,5]
    yc1a = npComponents[:,6]
    yc2a = npComponents[:,7]

    components_spectra = {
            "wavelengths": wavelengths,
            "oxyhemoglobin": oxyhemoglobin,
            "deoxyhemoglobin": deoxyhemoglobin,
            "methemoglobi": methemoglobin,
            "carboxyhemoglobin": carboxyhemoglobin,
            "eumelanin": eumelanin,
            "yc1a": yc1a,
            "yc2a": yc2a
        }
    return components_spectra

def cropFunction(Spec, lowerLimit, upperLimit):
    """crop the spectrum between lower limit and upper limit"""
    croppedSpectrum = Spectrum()
    croppedSpectrum.wavelength = Spec.wavelength[
        np.where(np.logical_and(lowerLimit <= Spec.wavelength, Spec.wavelength <= upperLimit))]
    croppedSpectrum.data = Spec.data[
        np.where(np.logical_and(lowerLimit <= Spec.wavelength, Spec.wavelength <= upperLimit))]
    return croppedSpectrum

def normalizeRef(Spec):
    """divide the spectrum by its standard deviation"""
    Spec.data = Spec.data/np.std(Spec.data)
    return Spec

def loadWhiteRef(refNameNothinInfront, whiteRefName,
                 skipRowsNothing=24, skipRowsWhite=24, wavelengthColumn=1,
                 firstSpecColumn=4):
    # returns cropped (between 500 to 600) white reference and the wavelength"
    refNothingInfront = pd.read_csv(refNameNothinInfront, sep=',', skiprows=skipRowsNothing).to_numpy()
    refWhite = pd.read_csv(whiteRefName, sep=',', skiprows=skipRowsWhite).to_numpy()
    refSpectrum = Spectrum()
    refSpectrum.wavelength = refWhite[:,wavelengthColumn]
    refSpectrum.data = np.mean(refWhite[:,firstSpecColumn:],axis=1)-np.mean(refNothingInfront[:,firstSpecColumn:],axis=1)
    croppedRef = cropFunction(refSpectrum, lowerLimitNormalization, upperLimitNormalization)
    refCroppedNormalized = normalizeRef(croppedRef)
    refOximetry = cropFunction(refCroppedNormalized,lowerLimitOximetry,upperLimitOximetry)
    return refOximetry

def loadDarkRef(darkRefPath=None, skipRows=4, wavelengthColumn=0, firstSpecColumn=3):
    ''' returns cropped (between 500 to 600) dark reference and the wavelength'''
    filetypes = [("csv files", "*.csv")]
    if darkRefPath is None:
        csv_file_path = askopenfilename(title="select the dark reference .csv file", filetypes=filetypes)
    else:
        csv_file_path = darkRefPath
    darkRef = pd.read_csv(csv_file_path, sep=',', skiprows=skipRows).to_numpy()
    darkRefSpec = Spectrum()
    darkRefSpec.data = np.mean(darkRef[:,firstSpecColumn:],axis=1)
    darkRefSpec.wavelength = darkRef[:,wavelengthColumn]
    croppedDarkRef = cropFunction(darkRefSpec,lowerLimitNormalization,upperLimitNormalization)
    return croppedDarkRef

def loadSpectrum(spectrumPath=None, skipRows=4, wavelengthColumn=0, firstSpecColumn=3):
    ''' returns dark reference and the wavelength'''
    filetypes = [("csv files", "*.csv")]
    if spectrumPath is None:
        csv_file_path = askopenfilename(title="select the spectrum .csv file", filetypes=filetypes)
    else:
        csv_file_path = spectrumPath
    spectrumData = pd.read_csv(csv_file_path, sep=',', skiprows=skipRows).to_numpy()
    spec = Spectrum()
    spec.data = spectrumData[:, firstSpecColumn:]
    spec.wavelength = spectrumData[:, wavelengthColumn]
    croppedSpectrum = cropFunction(spec,lowerLimitNormalization,upperLimitNormalization)
    return croppedSpectrum

def setSaturationFlag(spectrum):
    """If the spectrum is saturated the flag will be 1, other wise it will be 0"""
    saturationFlag=np.zeros(spectrum.data.shape[1])
    for i in range(spectrum.data.shape[1]):
        if np.max(spectrum.data[:,i]) == saturatedValue :
            saturationFlag[i] = 1
    return saturationFlag


def normalizeSpectrum(spec,darkRef):
    """returns the normalized spectrum for the data"""
    dRefTile = np.tile(darkRef.data, (spec.data.shape[1], 1)).T
    spectrumData=spec.data-dRefTile
    STDspectrum=np.std(spectrumData,axis=0)
    spectrumDataNormalized = Spectrum()
    spectrumDataNormalized.data = (spectrumData.T/STDspectrum[:,None]).T
    spectrumDataNormalized.wavelength = spec.wavelength
    croppedSpectrumOxymetry = cropFunction(spectrumDataNormalized, lowerLimitOximetry, upperLimitOximetry)
    return croppedSpectrumOxymetry


def find_nearest(array, value):
    """find the nearest value to a value in an array and returns the index"""
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def absorbanceSpectrum(refSpec, normalizedSpec):
    """calculate the absorbance spectrum using white reference and normalized spectrum"""
    modifiedData = np.zeros(normalizedSpec.data.shape)
    for i in range(normalizedSpec.wavelength.shape[0]):
        modifiedData[i,:] = refSpec.data[find_nearest(refSpec.wavelength, normalizedSpec.wavelength[i])]
    modifiedSpec = Spectrum()
    normalizedSpec.data[normalizedSpec.data==0] = 0.0001
    modifiedSpec.data = np.log(np.divide(modifiedData, normalizedSpec.data, out=None, where=True, casting= 'same_kind',
                                order = 'K', dtype = None))
    modifiedSpec.wavelength = normalizedSpec.wavelength
    return modifiedSpec



def scattering(spec, bValue=1.5):
    """calculate the scattering spectrum"""
    return (spec.wavelength / 500) ** (-1 * bValue)

def reflection(spec):
    """calculate the reflection spectrum"""
    return np.squeeze(-np.log(spec.wavelength.reshape(-1, 1)))

def cropComponents(absorbanceSpectrum, componentsSpectra):
    """crop the components regarding the upper limit and lower limit wavelengths"""
    Components = loadComponentsSpectra(componentsSpectra)
    # absorbance, spectrumWavelength = absorbanceSpectrum()
    oxyhemoglobin = np.zeros(absorbanceSpectrum.wavelength.shape)
    deoxyhemoglobin = np.zeros(absorbanceSpectrum.wavelength.shape)
    melanin = np.zeros(absorbanceSpectrum.wavelength.shape)
    scat = scattering(absorbanceSpectrum)
    ref = reflection(absorbanceSpectrum)
    for i, wavelength in enumerate(absorbanceSpectrum.wavelength):
        oxyhemoglobin[i] = Components["oxyhemoglobin"][find_nearest(Components["wavelengths"], wavelength)]
        deoxyhemoglobin[i] = Components["deoxyhemoglobin"][find_nearest(Components["wavelengths"], wavelength)]
        melanin[i] = Components["eumelanin"][find_nearest(Components["wavelengths"], wavelength)]
    componentsCrop = {
        "scattering": scat,
        "reflection": ref,
        "oxyhemoglobin": oxyhemoglobin,
        "deoxyhemoglobin": deoxyhemoglobin,
        "melanin": melanin}
    return componentsCrop

def componentsToArray(components):
    """make an n*m array of the components to use as input of the nnls"""
    variables = np.ones(components["oxyhemoglobin"].shape)
    variables = np.vstack([variables, components["oxyhemoglobin"]])
    variables = np.vstack([variables, components["deoxyhemoglobin"]])
    variables = np.vstack([variables, components["melanin"]])
    variables = np.vstack([variables, components["scattering"]])
    variables = np.vstack([variables, components["reflection"]])
    return variables

def getCoef(absorbance, variables):
    """apply nnls and get coefs"""
    allCoef = np.zeros([absorbance.data.shape[1], variables.shape[0]])
    for i in range(absorbance.data.shape[1]):
        coef = nnls(variables.T, absorbance.data[:,i],maxiter=2000 )
        allCoef[i,:] = coef[0]
    return allCoef

def saveData(saturationFlag , oxygenSat , imageNumber , rosaLabel):
    keptFlag=saturationFlag[(imageNumber-1). astype(int)]
    keptOxygenSat=oxygenSat[(imageNumber-1). astype(int)]

    dataDic = {
        "saturationFlag": keptFlag,
        "oxygenSat": keptOxygenSat,
        "rosaLabel": rosaLabel}
    return dataDic


def mainAnalysis(darkRefPath = None, spectrumPath = None, componentsSpectra=r'_components_spectra.csv',
                whiteRefName=r"int75_WHITEREFERENCE.csv", refNameNothinInfront=r"int75_LEDON_nothingInFront.csv"):
    """load data, do all the analysis, get coefs as concentration"""
    whiteRef = loadWhiteRef(refNameNothinInfront=refNameNothinInfront, whiteRefName=whiteRefName)
    if darkRefPath is None:
        darkRef = loadDarkRef()
    else:
        darkRef = loadDarkRef()
    darkRef.data[np.isnan(darkRef.data)] = 0
    if spectrumPath is None:
        spectrums = loadSpectrum()
    else:
        spectrums = loadSpectrum()
    saturationFlags = setSaturationFlag(spectrums)
    spectrums.data[np.isnan(spectrums.data)] = 0
    normalizedSpectrum = normalizeSpectrum(spectrums, darkRef)
    normalizedSpectrum.data[np.isnan(normalizedSpectrum.data)] = 0
    absorbance = absorbanceSpectrum(whiteRef, normalizedSpectrum)
    absorbance.data[np.isnan(absorbance.data)] = 0

    if componentsSpectra is None:
        croppedComponent = cropComponents(absorbance, componentsSpectraGlobal)
    else:
        croppedComponent = cropComponents(absorbance, componentsSpectra)
    features = componentsToArray(croppedComponent)
    features[np.isnan(features)] = 0
    coef = getCoef(absorbance,features)
    concentration = 100 * coef[:,1] /(coef[:,1]+coef[:,2])
    concentration[np.isnan(concentration)] = 0

    return concentration,saturationFlags

#
darkRefPath = r"./tests/TestSpectrums/bresilODrlp14/background.csv"
spectrumPath = r"./tests/TestSpectrums/bresilODrlp14/spectrum.csv"
#
# mainAnalysis(darkRefPath, spectrumPath)
concent, flags = mainAnalysis(darkRefPath, spectrumPath)
# print(concent)

#### This is for test
####### blood sample test

def bloodTest(refNameNothinInfront='./tests/TestSpectrums/blood/int75_LEDON_nothingInFront.csv',
                whiteRefName='./tests/TestSpectrums/blood/int75_WHITEREFERENCE.csv',
                darkRefPath=None, spectrumPath=None, componentsSpectra=None):
    """load data, do all the analysis, get coefs as concentration"""
    whiteRef = loadWhiteRef(refNameNothinInfront=refNameNothinInfront, whiteRefName=whiteRefName)
    if darkRefPath is None:
        darkRef = loadDarkRef(skipRows=24, wavelengthColumn=1, firstSpecColumn=4)
    else:
        darkRef = loadDarkRef(darkRefPath=darkRefPath, skipRows=24, wavelengthColumn=1, firstSpecColumn=4)
    darkRef.data[np.isnan(darkRef.data)] = 0
    if spectrumPath is None:
        spectrums = loadSpectrum(skipRows=24, wavelengthColumn=1, firstSpecColumn=4)
    else:
        spectrums = loadSpectrum(spectrumPath=spectrumPath, skipRows=24, wavelengthColumn=1, firstSpecColumn=4)
    spectrums.data[np.isnan(spectrums.data)] = 0
    normalizedSpectrum = normalizeSpectrum(spectrums,darkRef)
    normalizedSpectrum.data[np.isnan(normalizedSpectrum.data)] = 0
    absorbance = absorbanceSpectrum(whiteRef,normalizedSpectrum)
    absorbance.data[np.isnan(absorbance.data)] = 0

    if componentsSpectra is None:
        croppedComponent = cropComponents(absorbance, componentsSpectraGlobal)
    else:
        croppedComponent = cropComponents(absorbance, componentsSpectra)
    features = componentsToArray(croppedComponent)
    features[np.isnan(features)] = 0


    coef = getCoef(absorbance, features)
    concentration = 100 * coef[:,1] /(coef[:,1]+coef[:,2])
    concentration[np.isnan(concentration)] = 0

    return concentration, absorbance

# bloodTest()

def meanSO2 (concentrationValues,labels):
    uniqueLabel=np.unique(labels)
    meanConcentration=np.zeros(uniqueLabel.shape)
    for i in range(uniqueLabel.shape[0]):
        meanConcentration[i]=np.mean(concentrationValues[(np.where(labels==np.array(uniqueLabel[i]))[0])])

    return meanConcentration,uniqueLabel
