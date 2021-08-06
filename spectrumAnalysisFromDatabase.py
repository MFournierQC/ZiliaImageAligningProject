import pandas as pd
import numpy as np
import tkinter as tk
from tkinter.filedialog import askopenfilename
from scipy.optimize import nnls
import matplotlib.pyplot as plt

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

def loadWhiteRef(backgroundPath, whiteRefPath,
                 skipRowsNothing=24, skipRowsWhite=24, wavelengthColumn=1,
                 firstSpecColumn=4):
    background = pd.read_csv(backgroundPath, sep=',', skiprows=skipRowsNothing).to_numpy()
    refWhite = pd.read_csv(whiteRefPath, sep=',', skiprows=skipRowsWhite).to_numpy()
    wavelengths = refWhite[:,wavelengthColumn]
    spectra = refWhite[:,firstSpecColumn:]
    background = background[:,firstSpecColumn:]

    return wavelengths, spectra, background

def formatWhiteRef(whiteRefData, lowerLimitNormalization=510, upperLimitNormalization=590, lowerLimitOximetry=530, upperLimitOximetry=585):
    # returns cropped (between 500 to 600) white reference and the wavelength"
    wavelengths = whiteRefData[0]
    spectra = whiteRefData[1]
    background = whiteRefData[2]
    meanSpectra = np.mean(spectra, axis=1) - np.mean(background, axis=1)
    refSpectrum = Spectrum()
    refSpectrum.data = meanSpectra
    refSpectrum.wavelength = wavelengths
    croppedRef = cropFunction(refSpectrum, lowerLimitNormalization, upperLimitNormalization)
    refCroppedNormalized = normalizeRef(croppedRef)
    refOximetry = cropFunction(refCroppedNormalized, lowerLimitOximetry, upperLimitOximetry)
    return refOximetry

def formatDarkRef(darkRefData, lowerLimitNormalization=510, upperLimitNormalization=590):
    ''' returns cropped (between 500 to 600) dark reference and the wavelength'''
    wavelengths = darkRefData[0]
    darkRefSpectra = darkRefData[1]
    darkRefSpec = Spectrum()
    darkRefSpec.data = np.mean(darkRefSpectra, axis=1)
    darkRefSpec.wavelength = wavelengths
    croppedDarkRef = cropFunction(darkRefSpec, lowerLimitNormalization, upperLimitNormalization)
    croppedDarkRef.data[np.isnan(croppedDarkRef.data)] = 0
    return croppedDarkRef

def formatSpectra(spectraData, lowerLimitNormalization=510, upperLimitNormalization=590):
    ''' returns dark reference and the wavelength'''
    wavelengths = spectraData[0]
    spectra = spectraData[1]
    spec = Spectrum()
    spec.data = spectra
    spec.wavelength = wavelengths
    croppedSpectrum = cropFunction(spec, lowerLimitNormalization, upperLimitNormalization)
    croppedSpectrum.data[np.isnan(croppedSpectrum.data)] = 0
    return croppedSpectrum

def setSaturationFlag(spectrum, saturatedValue=65535):
    """If the spectrum is saturated the flag will be 1, other wise it will be 0"""
    saturationFlag = np.zeros(spectrum.data.shape[1])
    for i in range(spectrum.data.shape[1]):
        if np.max(spectrum.data[:,i]) == saturatedValue:
            saturationFlag[i] = 1
    return saturationFlag

def normalizeSpectrum(spec, darkRef, lowerLimitOximetry=530, upperLimitOximetry=585):
    """returns the normalized spectrum for the data"""
    dRefTile = np.tile(darkRef.data, (spec.data.shape[1], 1)).T
    spectrumData = spec.data - dRefTile
    STDspectrum = np.std(spectrumData,axis=0)
    spectrumDataNormalized = Spectrum()
    spectrumDataNormalized.data = (spectrumData.T/STDspectrum[:,None]).T
    spectrumDataNormalized.wavelength = spec.wavelength
    croppedSpectrumOxymetry = cropFunction(spectrumDataNormalized, lowerLimitOximetry, upperLimitOximetry)
    croppedSpectrumOxymetry.data[np.isnan(croppedSpectrumOxymetry.data)] = 0
    return croppedSpectrumOxymetry

def findNearest(array, value):
    """find the nearest value to a value in an array and returns the index"""
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def absorbanceSpectrum(refSpec, normalizedSpec):
    """calculate the absorbance spectrum using white reference and normalized spectrum"""
    modifiedData = np.zeros(normalizedSpec.data.shape)
    for i in range(normalizedSpec.wavelength.shape[0]):
        modifiedData[i,:] = refSpec.data[findNearest(refSpec.wavelength, normalizedSpec.wavelength[i])]
    modifiedSpec = Spectrum()
    normalizedSpec.data[normalizedSpec.data==0] = 0.0001
    modifiedSpec.data = np.log(np.divide(modifiedData, normalizedSpec.data, out=None, where=True, casting='same_kind',
                                order='K', dtype=None))
    modifiedSpec.wavelength = normalizedSpec.wavelength
    modifiedSpec.data[np.isnan(modifiedSpec.data)] = 0
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
    variables[np.isnan(features)] = 0
    return variables

def getCoefficients(absorbance, variables):
    """apply nnls and get coefs"""
    allCoef = np.zeros([absorbance.data.shape[1], variables.shape[0]])
    for i in range(absorbance.data.shape[1]):
        coef = nnls(variables.T, absorbance.data[:,i], maxiter=2000 )
        allCoef[i,:] = coef[0]
    return allCoef

def getConcentration(coefficients):
    concentration = 100 * coefficients[:,1] / (coefficients[:,1] + coefficients[:,2])
    concentration[np.isnan(concentration)] = 0
    return concentration

def saveData(saturationFlag , oxygenSat , imageNumber , rosaLabel):
    keptFlag=saturationFlag[(imageNumber-1). astype(int)]
    keptOxygenSat=oxygenSat[(imageNumber-1). astype(int)]

    dataDic = {
        "saturationFlag": keptFlag,
        "oxygenSat": keptOxygenSat,
        "rosaLabel": rosaLabel}
    return dataDic

def meanSO2 (concentrationValues, labels):
    uniqueLabel = np.unique(labels)
    meanConcentration = np.zeros(uniqueLabel.shape)
    for i in range(uniqueLabel.shape[0]):
        meanConcentration[i] = np.mean(concentrationValues[(np.where(labels==np.array(uniqueLabel[i]))[0])])

    return meanConcentration, uniqueLabel

def mainAnalysis(darkRefData, spectraData, componentsSpectra=r'_components_spectra.csv',
                whiteRefPath=r"int75_WHITEREFERENCE.csv", whiteRefBackground=r"int75_LEDON_nothingInFront.csv"):
    """
    Load data, do all the analysis, get coefs as concentration
    WARNING: For blood sample, another white reference and white ref background
    are needed.
    Return concentration, absorbance if blood samples???
    """
    whiteRefData = loadWhiteRef(whiteRefBackground=whiteRefBackground, whiteRefPath=whiteRefPath)
    whiteRef = formatWhiteRef(whiteRefData)
    darkRef = formatDarkRef(darkRefData)
    spectra = formatSpectra(spectraData)

    saturationFlags = setSaturationFlag(spectra)
    normalizedSpectrum = normalizeSpectrum(spectra, darkRef)
    absorbance = absorbanceSpectrum(whiteRef, normalizedSpectrum)
    croppedComponent = cropComponents(absorbance, componentsSpectra)
    features = componentsToArray(croppedComponent)
    coefficients = getCoefficients(absorbance, features)
    concentration = getConcentration(coefficients)

    return concentration, saturationFlags
