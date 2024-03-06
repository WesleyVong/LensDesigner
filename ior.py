import numpy as np
import warnings
# Refractive Index of air based on wavelength
# Air from 0.23-1.69um
# https://refractiveindex.info
def AirRefractiveIndex(microns):
    # wavelength squared
    lsq = microns**2
    # numerator coefficients
    coeffa = [0.05792105, 0.00167917]
    # denominator coefficients
    coeffb = [238.0185, 57.362]
    # n minus 1
    nm1 = coeffa[0]/(coeffb[0]-(1/lsq))+coeffa[1]/(coeffb[1]-(1/lsq))
    return nm1+1

# Refractive Index of the material based on wavelength
# N-BK-7 Glass from 0.3-2.5um
# https://refractiveindex.info
def BK7RefractiveIndex(microns):
    # wavelength squared
    lsq = microns**2
    # numerator coefficients
    coeffa = [1.03961212, 0.231792344, 1.01046945]
    # denominator coefficients
    coeffb = [0.00600069867, 0.0200179144, 103.560653]
    # n squared minus 1
    nsqm1 = (coeffa[0]*lsq)/(lsq-coeffb[0])+(coeffa[1]*lsq)/(lsq-coeffb[1])+(coeffa[2]*lsq)/(lsq-coeffb[2])
    return np.sqrt(nsqm1 + 1)

# Refractive Index of the material based on wavelength
# N-SF-11 Glass from 0.37-2.5um
# https://refractiveindex.info
def SF11RefractiveIndex(microns):
    # wavelength squared
    lsq = microns**2
    # numerator coefficients
    coeffa = [1.73759695, 0.313747346, 1.89878101]
    # denominator coefficients
    coeffb = [0.013188707, 0.0623068142, 155.23629]
    # n squared minus 1
    nsqm1 = (coeffa[0]*lsq)/(lsq-coeffb[0])+(coeffa[1]*lsq)/(lsq-coeffb[1])+(coeffa[2]*lsq)/(lsq-coeffb[2])
    return np.sqrt(nsqm1 + 1)

# Refractive Index of the material based on wavelength
# CaF2 Glass from 0.23-9.7um
# https://refractiveindex.info
def CaF2RefractiveIndex(microns):
    # wavelength squared
    lsq = microns**2
    # numerator coefficients
    coeffa = [0.5675888, 0.4710914, 3.8484723]
    # denominator coefficients
    coeffb = [0.050263605, 0.1003909, 34.649040]
    # n squared minus 1
    nsqm1 = (coeffa[0]*lsq)/(lsq-coeffb[0])+(coeffa[1]*lsq)/(lsq-coeffb[1])+(coeffa[2]*lsq)/(lsq-coeffb[2])
    return np.sqrt(nsqm1 + 1)

# Refractive Index of the material based on wavelength
# LAH Glass from 0.32-2.4um
# https://refractiveindex.info
def LAHRefractiveIndex(microns):
    # wavelength squared
    lsq = microns**2
    # numerator coefficients
    coeffa = [1.83021453, 0.29156359, 1.28544024]
    # denominator coefficients
    coeffb = [0.0090482329, 0.0330756689, 89.3675501]
    # n squared minus 1
    nsqm1 = (coeffa[0]*lsq)/(lsq-coeffb[0])+(coeffa[1]*lsq)/(lsq-coeffb[1])+(coeffa[2]*lsq)/(lsq-coeffb[2])
    return np.sqrt(nsqm1 + 1)

def GetIOR(microns, material="BK7"):
    if material == "BK7":
        return BK7RefractiveIndex(microns)
    if material == "SF11":
        return SF11RefractiveIndex(microns)
    if material == "CaF2":
        return CaF2RefractiveIndex(microns)
    if material == "LAH":
        return LAHRefractiveIndex(microns)
    if material == "Air":
        return AirRefractiveIndex(microns)
    warnings.warn("Invalid Material")
    return 1