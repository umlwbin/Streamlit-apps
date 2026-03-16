# =========================================================
# units.py — Centralized Unit Normalization Map
# =========================================================

"""
Canonical UNIT_MAP for scientific datasets.

- Keys: raw unit strings as they appear in messy headers
- Values: normalized CF-style ASCII-safe units
- Grouped by domain for readability
- Multiple raw variants placed on the same line
"""

UNIT_MAP = {

    # =====================================================
    # CTD / Oceanographic Core Variables
    # =====================================================

    # Temperature (in-situ, potential)
    "deg c": "degC", "degc": "degC",

    # Salinity
    "psu": "psu",

    # Pressure
    "db": "db",

    # Conductivity
    "ms/cm": "ms cm-1",

    # Density / Sigma-theta
    "kg/m^3": "kg m-3",

    # Specific Volume Anomaly
    "10^-8 m^3/kg": "1e-8 m3 kg-1",

    # Dissolved Oxygen
    "ml/l": "ml l-1",
    "mg l^-1": "mg l-1",
    "umol/kg": "umol kg-1",

    # Specific Conductance
    "us cm^-1": "uS cm-1",

    # Turbidity
    "ntu": "ntu",

    # Chlorophyll (RFU)
    "rfub": "rfu", "rfu": "rfu",

    # PAR / Irradiance
    "ue m^-2 s^-1": "uE m-2 s-1",
    "umol photons/m^2/sec": "umol_photons m-2 s-1",

    # Oxygen Saturation
    "% saturation": "percent_sat",
    "%sat": "percent_sat",
    "%": "percent",

    # CDOM / Fluorescence
    "mg/m^3": "mg m-3",

    # Beam Attenuation
    "1/m": "m-1",

    # Decent Rate
    "m s^-1": "m s-1",

    # =====================================================
    # CEOS Common Water Chemistry
    # =====================================================

    # Nutrients, ions, TSS
    "mg/l": "mg l-1",
    "ug/l": "ug l-1",
    "umol/l": "umol l-1",

    # Nutrient wavelengths / particle size
    "um": "um",

    # Sedimentation, benthic flux, chlorophyll-a
    "mg/m2": "mg m2",

    # =====================================================
    # Atmospheric / Meteorological
    # =====================================================

    # Wind speed
    "m/s": "m s-1",
    "km/h": "km h-1",

    # Pressure
    "kpa": "kPa",
    "hpa": "hPa",

    # Radiation
    "w/m^2": "W m-2",

    # Precipitation
    "mm": "mm",

    # Relative humidity
    "%rh": "percent_rh",

    # Greenhouse gases
    "ppm": "ppm",

    # =====================================================
    # Hydrology / Cryosphere
    # =====================================================

    # Snow depth, ice thickness
    "cm": "cm",

    # Legacy salinity
    "ppt": "ppt",

    # Water equivalent
    "mwe": "mwe",

    # =====================================================
    # Optics
    # =====================================================

    # Attenuation coefficients
    "m^-1": "m-1",

    # Radiance
    "sr^-1": "sr-1",

    # Wavelengths
    "nm": "nm",

    # =====================================================
    # Biology
    # =====================================================

    # Phytoplankton
    "cells/ml": "cells ml-1",

    # Biomass
    "mg c/m^3": "mgC m-3",

    # Zooplankton counts
    "#/l": "count l-1",
}


def get_unit_map():
    """Return the canonical UNIT_MAP."""
    return UNIT_MAP
