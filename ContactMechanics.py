# -*- coding: utf-8 -*-
"""
ContactMechanics.py

Contact mechanics models for analyzing atomic force microscopy (AFM) force-distance curves.
This module contains implementations of three common contact mechanics models:
- Hertz model: Assumes no adhesion between tip and sample
- DMT (Derjaguin-Muller-Toporov) model: Accounts for adhesion at pull-off
- JKR (Johnson-Kendall-Roberts) model: Accounts for adhesion during contact

Each model calculates the Young's modulus (E) of the sample based on force-distance
curve data from AFM measurements.

Author: Scott Dietrich
Created: 2025
"""

import numpy as np


def hertz_model(approach, nu, R, threshold):
    """Calculate Young's modulus using the Hertz contact mechanics model."""
    
    # Extract separation and force data
    Zarray = approach.iloc[:,2]
    Farray = approach.iloc[:,1]
    Farray = np.asarray(Farray)
    Zarray = np.asarray(Zarray)
    
    # Check for sufficient data
    if len(Farray) < 5:
        # print(f"Hertz: Insufficient data ({len(Farray)} points)")  # Uncomment for debug
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    
    # Use the entire cleaned approach curve
    Fsub = Farray
    Zsub = Zarray
    
    # Find maximum
    imax = np.argmax(Fsub)
    Fmax = Fsub[imax]*1E-9
    Zmax = Zsub[imax]*1E-6
    
    # Find threshold point
    Fth = threshold*Fmax
    
    if imax > 0:
        # CRITICAL FIX: Make sure we're searching in the right region
        # The threshold should be between start and max
        search_region = Fsub[:imax+1]
        ith = (np.abs(search_region - Fth*1E9)).argmin()
    else:
        # print(f"Hertz: Max at first point")  # Uncomment for debug
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    
    Zth = Zsub[ith]*1E-6
    
    # Check for valid separation difference
    dZ = np.abs(Zmax - Zth)
    if dZ < 1e-15:
        # print(f"Hertz: Zero separation difference")  # Uncomment for debug
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    
    # Calculate stiffness
    k = -(Fmax - Fth)/dZ
    if k < 0: 
        k = np.nan
    
    # Calculate modulus - add bounds checking
    if Fmax <= 0 or Fth < 0 or not np.isfinite(Fmax) or not np.isfinite(Fth):
        E = np.nan
    else:
        try:
            E = (1E-9) * 0.75 * (1-nu)**2 * ((Fmax**(2/3) - Fth**(2/3)) / dZ)**(3/2) / np.sqrt(R)
        except:
            E = np.nan
    
    return Zth*1E9, Fth*1E9, Zmax*1E9, Fmax*1E9, k, E


def dmt_model(retract, nu, R, threshold, drift_fraction=0.75):
    """
    Calculate Young's modulus using the DMT (Derjaguin-Muller-Toporov) model.
    
    The DMT model:
    - Accounts for adhesion forces at pull-off
    - Assumes adhesion acts only outside the contact area
    - Appropriate for stiff materials with low adhesion
    
    This implementation includes drift correction by using a point at drift_fraction
    (default 75%) of the maximum force instead of the actual maximum. This avoids
    issues with baseline drift that can occur in AFM retract curves.
    
    The model uses three points on the retract curve:
    1. Maximum force point (or 75% of max to avoid drift)
    2. Minimum force point (maximum adhesion/pull-off)
    3. Threshold point for stiffness calculation
    
    Parameters:
    -----------
    retract : pandas.DataFrame
        Force-distance curve for the retract phase
        Must contain columns: 'Separation (um)', 'F (nN)'
    nu : float
        Poisson's ratio of the sample (dimensionless)
    R : float
        Tip radius in meters
    threshold : float
        Fraction of maximum force to use for stiffness calculation
    drift_fraction : float, optional
        Fraction of maximum force to use (default 0.75 = 75%)
        This helps avoid drift artifacts in the baseline
        
    Returns:
    --------
    tuple : (Z1, F1, Z2, F2, Z3, F3, k, E)
        Z1 : float - Separation at minimum force/pull-off (nm)
        F1 : float - Minimum force/adhesion force (nN)
        Z2 : float - Separation at threshold point (nm)
        F2 : float - Force at threshold point (nN)
        Z3 : float - Separation at maximum/effective maximum force (nm)
        F3 : float - Maximum/effective maximum force (nN)
        k : float - Effective stiffness (N/m)
        E : float - Young's modulus (GPa)
        
    Notes:
    ------
    The drift_fraction parameter allows you to use a point at, e.g., 75% of
    the maximum force instead of the actual maximum. This helps avoid drift
    artifacts while staying in the valid contact region.
    """
    
    # Extract separation and force data from the retract curve
    Zarray = retract.iloc[:,2]  # Separation in micrometers
    Farray = retract.iloc[:,1]  # Force in nanoNewtons
    
    # Find the maximum (at start of retract) and minimum (at pull-off) indices
    imax = np.argmax(Farray)
    imin = np.argmin(Farray)
    
    # Extract only the portion between max and min (the retract phase)
    Fsub = Farray[imax:imin]
    Zsub = Zarray[imax:imin]
    Fsub = np.asarray(Fsub)
    Zsub = np.asarray(Zsub)
    
    # Check if we have valid data
    if len(Fsub) == 0:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    
    # DRIFT AVOIDANCE STRATEGY:
    # AFM retract curves can show baseline drift, where the force reading
    # slowly drifts up or down over time. This causes the "maximum" force
    # to be incorrectly identified. To avoid this, we use a point at 
    # drift_fraction (default 75%) of the apparent maximum force.
    # This keeps us in the contact region but avoids drift artifacts.
    
    # Find the global maximum (even if affected by drift)
    imax_global = np.argmax(Fsub)
    Fmax_global = Fsub[imax_global]
    
    # Calculate target force as drift_fraction of the maximum
    # For drift_fraction = 0.75, we use the point at 75% of max force
    F_target = drift_fraction * Fmax_global
    
    # Find the point closest to our target force value
    # Search only up to the global max to ensure we're on the loading portion
    i_effective = (np.abs(Fsub[:imax_global+1] - F_target)).argmin()
    
    # Use this drift-corrected point as our "effective maximum"
    Fmax = Fsub[i_effective]*1E-9  # Convert nN to N
    Zmax = Zsub[i_effective]*1E-6  # Convert μm to m
    
    # Find the minimum force point (maximum adhesion at pull-off)
    # This is the most negative force in the curve
    ineg = np.argmin(Fsub)
    Fneg = Fsub[ineg]*1E-9  # Convert nN to N
    Zneg = Zsub[ineg]*1E-6  # Convert μm to m
    
    # Find the threshold point for stiffness calculation
    # Use threshold relative to our effective maximum
    Fth = threshold*Fmax
    
    # FIXED: Search for threshold point BETWEEN effective max and minimum
    # Not before the effective max (which would catch the plateau)
    # The threshold point should be on the descending part of the curve
    ith = i_effective + (np.abs(Fsub[i_effective:] - Fth*1E9)).argmin()
    Zth = Zsub[ith]*1E-6
    
    # Calculate effective stiffness
    if (Zmax - Zth) == 0: 
        k = np.nan  # Avoid division by zero
    else:
        k = -(Fmax - Fth)/(Zmax - Zth)
    if k < 0: 
        k = np.nan  # Negative stiffness is unphysical
    
    # Calculate Young's modulus using the DMT equation
    # The DMT model accounts for adhesion by using (F - F_adhesion) in calculations
    # E = 0.75 * (1-ν²) * [((F_max - F_adh)^(2/3) - (F_th - F_adh)^(2/3)) / |Z_max - Z_neg|]^(3/2) / √R
    E = (1E-9) * 0.75 * (1-nu)**2 * (((Fmax-Fneg)**(2/3) - (Fth-Fneg)**(2/3)) / np.abs(Zmax-Zneg))**(3/2) / np.sqrt(R)
    
    # Return the three points used (in nm and nN) plus k and E
    return Zneg*1E9, Fneg*1E9, Zth*1E9, Fth*1E9, Zmax*1E9, Fmax*1E9, k, E


def jkr_model(retract, nu, R):
    """
    Calculate Young's modulus using the JKR (Johnson-Kendall-Roberts) model.
    
    The JKR model:
    - Accounts for adhesion forces during contact (not just at pull-off)
    - Assumes adhesion acts inside the contact area
    - Appropriate for soft, compliant materials with high adhesion
    
    The model uses two points on the retract curve:
    1. The zero-force point (where tip loses contact)
    2. The minimum force point (maximum adhesion)
    
    Parameters:
    -----------
    retract : pandas.DataFrame
        Force-distance curve for the retract phase
        Must contain columns: 'Separation (um)', 'F (nN)'
    nu : float
        Poisson's ratio of the sample (dimensionless)
    R : float
        Tip radius in meters
        
    Returns:
    --------
    tuple : (Z1, Z2, F2, E)
        Z1 : float - Separation at zero force (nm)
        Z2 : float - Separation at minimum force (nm)
        F2 : float - Minimum force/adhesion force (nN)
        E : float - Young's modulus (GPa)
        
    Notes:
    ------
    The JKR model is most accurate for soft materials where adhesion forces
    significantly affect the contact area. If Zneg < Zo (unphysical condition),
    returns NaN for the modulus.
    """
    
    # Extract separation and force data
    Zarray = retract.iloc[:,2]  # Separation in micrometers
    Farray = retract.iloc[:,1]  # Force in nanoNewtons
    
    # Find maximum (start of retract) and minimum (pull-off) indices
    imax = np.argmax(Farray)
    imin = np.argmin(Farray)
    
    # Extract the retract portion of the curve
    Fsub = Farray[imax:imin]
    Zsub = Zarray[imax:imin]
    Fsub = np.asarray(Fsub)
    Zsub = np.asarray(Zsub)
    
    # Check for valid data
    if len(Fsub) == 0:
        return np.nan, np.nan, np.nan, np.nan
    
    # Find the minimum force point (maximum negative force = maximum adhesion)
    ineg = np.argmin(Fsub)
    Fneg = Fsub[ineg]*1E-9  # Convert nN to N
    Zneg = Zsub[ineg]*1E-6  # Convert μm to m
    
    # Find the zero-force point (where force crosses from negative to positive)
    # This is where the tip loses contact with the surface
    io = (np.abs(Fsub)).argmin()  # Find point closest to zero force
    Zo = Zsub[io]*1E-6  # Convert μm to m
    
    # Calculate Young's modulus using the JKR equation
    # The JKR model relates adhesion force to contact mechanics:
    # E = 0.75 * (1-ν²) * (1 + 16^(1/3)) / 3)^(3/2) * |F_adhesion| / √(R * (Z_neg - Z_o)³)
    # 
    # The term (1 + 16^(1/3))/3 ≈ 1.755 comes from JKR theory
    # 
    # Physical constraint: Zneg should be less than Zo (tip retracts before losing contact)
    if Zneg > Zo:
        # Calculate the modulus
        E = (1E-9) * 0.75 * (1-nu)**2 * ((1+16**(1/3))/3)**(3/2) * np.abs(Fneg) / np.sqrt(R*(Zneg-Zo)**3)
    else:
        # Unphysical condition - return NaN
        E = np.nan
    
    # Return the two points used (in nm and nN) plus the modulus
    return Zo*1E9, Zneg*1E9, Fneg*1E9, E