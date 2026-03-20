# -*- coding: utf-8 -*-
"""
DataUtils.py

Utility functions for AFM force-distance curve data processing and analysis.
This module contains helper functions for:
- Outlier detection and removal (IQR method)
- Finding zero crossings and specific values in arrays
- Height and deformation calculations
- Force-separation transformations
- Power law curve fitting

Author: Scott Dietrich
Created: 2025
"""

import numpy as np
from sklearn.linear_model import LinearRegression


def remove_plateau_and_overshoot(approach):
    """
    Remove plateau and overshoot regions from approach curve.
    
    Detects where the tip stops indenting continuously and the AFM
    feedback takes over to maintain constant force. Truncates the
    curve before this plateau region.
    
    Strategy:
    1. Calculate dF/dZ (stiffness) along the curve
    2. Find where stiffness drops below 30% of the maximum
    3. Check for sustained low stiffness (3+ consecutive points)
    4. Truncate curve before this region
    
    Parameters:
    -----------
    approach : pandas.DataFrame
        Approach curve with columns 'F (nN)' and 'Separation (um)'
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned approach curve with plateau/overshoot removed
    """
    if len(approach) < 10:
        # Too few points to analyze
        return approach
    
    F = approach['F (nN)'].values
    Z = approach['Separation (um)'].values
    
    # Calculate point-to-point stiffness: dF/dZ
    dF = np.diff(F)
    dZ = np.diff(Z)
    
    # Avoid division by zero
    dZ[np.abs(dZ) < 1e-10] = 1e-10
    
    # Calculate absolute stiffness (force increases as Z decreases, so negative)
    stiffness = np.abs(dF / dZ)
    
    # Find the maximum stiffness in the first 80% of the curve
    # (avoids using the plateau region to define "maximum")
    n_80 = int(0.8 * len(stiffness))
    if n_80 < 5:
        n_80 = len(stiffness)
    max_stiffness = np.max(stiffness[:n_80])
    
    # Define threshold as 30% of maximum stiffness
    # When stiffness drops below this, feedback has likely engaged
    threshold = 0.3 * max_stiffness
    
    # Find regions where stiffness is below threshold
    low_stiffness = stiffness < threshold
    
    # Look for sustained low stiffness (3+ consecutive points)
    # This indicates we've entered the plateau region
    for i in range(len(low_stiffness) - 2):
        if (low_stiffness[i] and 
            low_stiffness[i+1] and 
            low_stiffness[i+2]):
            # Found plateau start - truncate here
            # Use i (not i+1) because diff() shortens array by 1
            return approach.iloc[:i].copy()
    
    # No plateau detected - return original curve
    return approach

def remove_plateau_and_overshoot_retract(retract):
    """
    Remove plateau region from retract curve.
    
    At the start of retract, the AFM holds at force setpoint, creating a plateau.
    This function uses TWO methods to detect and remove this plateau:
    1. Force threshold: Skip until force drops below 80% of initial
    2. Derivative check: Skip until tip is actively retracting (negative dF/dZ)
    
    Parameters:
    -----------
    retract : pandas.DataFrame
        Retract curve with columns 'F (nN)' and 'Separation (um)'
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned retract curve with initial plateau removed
    """
    if len(retract) < 10:
        return retract
    
    F = retract['F (nN)'].values
    Z = retract['Separation (um)'].values
    
    # METHOD 1: Force threshold - skip initial high-force plateau
    # Use 80% instead of 90% to be more aggressive
    F_initial = F[0]
    force_threshold = 0.8 * F_initial
    
    # Find where force drops below threshold
    below_threshold = np.where(F < force_threshold)[0]
    
    if len(below_threshold) > 0:
        i_start_force = below_threshold[0]
    else:
        i_start_force = 0
    
    # METHOD 2: Derivative check - find where tip is actively retracting
    # Calculate dF/dZ - should be negative when tip is pulling away
    if len(F) > 5:
        dF = np.diff(F)
        dZ = np.diff(Z)
        dZ[np.abs(dZ) < 1e-10] = 1e-10
        
        # dF/dZ should be significantly negative during retraction
        # (force decreasing as separation increases)
        stiffness = dF / dZ
        
        # Find where we have sustained negative stiffness (retracting)
        # Look for 3+ consecutive points with negative stiffness
        for i in range(len(stiffness) - 2):
            if (stiffness[i] < -0.1 and 
                stiffness[i+1] < -0.1 and 
                stiffness[i+2] < -0.1):
                i_start_deriv = i
                break
        else:
            i_start_deriv = 0
    else:
        i_start_deriv = 0
    
    # Use the LATER of the two cutoff points to be conservative
    i_start = max(i_start_force, i_start_deriv)
    
    if i_start > 0 and i_start < len(retract):
        return retract.iloc[i_start:].copy()
    
    return retract


def remove_outliers_IQR(data_array):
    """
    Remove outliers from a numpy array using the Interquartile Range (IQR) method.
    
    The IQR method is a robust statistical technique that identifies outliers
    as values falling outside the range [Q1 - 1.5*IQR, Q3 + 1.5*IQR], where:
    - Q1 is the 25th percentile (first quartile)
    - Q3 is the 75th percentile (third quartile)  
    - IQR = Q3 - Q1 (the interquartile range, containing middle 50% of data)
    
    This is the same criterion used by boxplots to identify outlier points.
    The factor 1.5 is standard for "outliers" (use 3.0 for "extreme outliers").
    
    For a normal distribution, this removes approximately the most extreme 0.7%
    of data on each tail. However, the method is robust and adapts to the
    actual data distribution without assuming normality.
    
    Parameters:
    -----------
    data_array : numpy array
        Array containing the data, may include NaN values which are preserved
        
    Returns:
    --------
    numpy array
        Same array with outliers replaced by NaN
        
    Notes:
    ------
    - Requires at least 5 valid (non-NaN) data points to perform filtering
    - NaN values in the input are ignored for statistics but preserved in output
    - Returns a copy of the array, does not modify the original
    
    Example:
    --------
    >>> data = np.array([1, 2, 3, 100, 4, 5, 6])  # 100 is an outlier
    >>> filtered = remove_outliers_IQR(data)
    >>> # filtered = [1, 2, 3, nan, 4, 5, 6]
    """
    
    # Create a copy to avoid modifying the original array
    filtered_data = data_array.copy()
    
    # Extract only the valid (non-NaN) values for calculating statistics
    # Boolean indexing with ~np.isnan() selects all non-NaN elements
    valid_data = filtered_data[~np.isnan(filtered_data)]
    
    # Only proceed if we have enough data points
    # Need at least 5 points to calculate meaningful quartiles
    if len(valid_data) > 4:
        # Calculate the first quartile (25th percentile)
        # This is the value below which 25% of the data falls
        Q1 = np.percentile(valid_data, 25)
        
        # Calculate the third quartile (75th percentile)
        # This is the value below which 75% of the data falls
        Q3 = np.percentile(valid_data, 75)
        
        # Calculate the interquartile range (IQR)
        # This is the range containing the middle 50% of the data
        # It's a robust measure of statistical dispersion
        IQR = Q3 - Q1
        
        # Define outlier boundaries using the 1.5*IQR rule
        # Data points outside these bounds are considered outliers
        # The factor 1.5 is a standard choice from Tukey's method
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Create a boolean mask identifying outliers
        # Use logical OR (|) to catch values that are either too low OR too high
        outlier_mask = (filtered_data < lower_bound) | (filtered_data > upper_bound)
        
        # Replace outliers with NaN
        # This preserves the array shape while marking outliers as invalid
        filtered_data[outlier_mask] = np.nan
        
        # Optional diagnostic output (commented out to avoid console spam)
        # Uncomment for debugging to see how many outliers were removed
        # num_outliers = np.sum(outlier_mask)
        # if num_outliers > 0:
        #     print(f"  Removed {num_outliers} outliers (bounds: {lower_bound:.2f} - {upper_bound:.2f})")
    
    return filtered_data


def find_first_crossing(x, y):
    """
    Find the first point where data crosses from positive to negative.
    
    This function is used to find the zero-force point in AFM force curves,
    which indicates where the tip loses contact with the surface.
    
    Parameters:
    -----------
    x : array-like
        Independent variable (e.g., separation distance)
    y : array-like
        Dependent variable (e.g., force)
        
    Returns:
    --------
    float
        The x-value where y crosses from positive to negative,
        calculated using linear interpolation between the two points
        bracketing the zero crossing. Returns minimum of x if no crossing found.
        
    Notes:
    ------
    Uses linear interpolation to find the exact crossing point between
    the two data points that bracket the zero crossing.
    
    Example:
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([5, 3, 1, -2, -4])  # Crosses zero between x=3 and x=4
    >>> crossing = find_first_crossing(x, y)
    >>> # crossing ≈ 3.33 (by linear interpolation)
    """
    
    # Find where y changes from positive to negative
    # [:-1] and [1:] create arrays offset by one element
    # This compares each point to the next point
    # The result is an array of indices where sign changes occur
    sign_changes = np.where((y[:-1] > 0) & (y[1:] <= 0))[0]
    
    # If no zero crossing is found, return the minimum x value
    # This can happen if the tip never loses contact or data is incomplete
    if len(sign_changes) == 0:
        return np.min(x)
    
    # Get the index of the first zero crossing
    # This is the point just before the force goes negative
    i = sign_changes[0]
    
    # Extract the two points bracketing the zero crossing
    x1, y1 = x[i], y[i]      # Point before crossing (y1 > 0)
    x2, y2 = x[i+1], y[i+1]  # Point after crossing (y2 <= 0)
    
    # Use linear interpolation to find the exact x where y = 0
    # Formula: x_crossing = x1 - y1 * (x2 - x1) / (y2 - y1)
    # This assumes the data varies linearly between the two points
    crossing_x = x1 - y1 * (x2 - x1) / (y2 - y1)
    
    return crossing_x


def find_index(array, value):
    """
    Find the index of the element in an array closest to a given value.
    
    Searches only in the physically meaningful region between the minimum
    and maximum of the array, which for AFM force curves corresponds to
    the region between zero force and maximum indentation.
    
    Parameters:
    -----------
    array : array-like
        Array to search (typically force data)
    value : float
        Value to find in the array
        
    Returns:
    --------
    int
        Index of the element closest to the specified value
        
    Notes:
    ------
    For AFM force curves, this function handles both approach curves
    (where min comes before max) and retract curves (where max comes before min).
    
    Example:
    --------
    >>> force = np.array([0, 5, 10, 15, 20, 15, 10, 5, 0])  # Approach then retract
    >>> idx = find_index(force, 12)
    >>> # Returns index of value closest to 12 (either 10 or 15)
    """
    
    # Find the indices of minimum and maximum values
    imax = np.argmax(array)
    imin = np.argmin(array)
    
    # Determine the order and extract the relevant portion
    if imin > imax:
        # Retract curve case: max comes first, then min (pull-off)
        # Extract the portion from max force to minimum (adhesion)
        Fsub = array[imax:imin]
        Fsub = np.asarray(Fsub)
        
        # Find the closest point to the target value in this subset
        idx = imax + (np.abs(Fsub - value)).argmin()
        
    elif imin < imax: 
        # Approach curve case: min (zero) comes first, then max (indentation)
        # Extract the portion from zero force to maximum force
        Fsub = array[imin:imax]
        Fsub = np.asarray(Fsub)
        
        # Find the closest point to the target value in this subset
        idx = imin + (np.abs(Fsub - value)).argmin()
    
    return idx


def getHeightandDeformation(FDCurve):
    """
    Calculate the height and deformation of a sample from a force-distance curve.
    
    Height is determined by the zero-force crossing point (where tip touches surface).
    Deformation is the distance from this zero-crossing to the maximum force point.
    
    Parameters:
    -----------
    FDCurve : pandas.DataFrame
        Force-distance curve with columns at positions:
        Column 1: Force (nN)
        Column 2: Separation (μm)
        
    Returns:
    --------
    tuple : (Height, Fzero, Zmax, Fmax, defrm)
        Height : float - Surface height at zero force (nm)
        Fzero : float - Force at zero crossing, always 0 (nN)
        Zmax : float - Separation at maximum force (nm)
        Fmax : float - Maximum force value (nN)
        defrm : float - Sample deformation (nm), = Height - Zmax
        
    Notes:
    ------
    - Separation array is flipped (reversed) for easier processing
    - Returns defrm = 0 if calculated deformation is negative (unphysical)
    - All returned values are in convenient units (nm, nN) not SI units
    """
    
    # Extract and flip the arrays for easier processing
    # Flipping reverses the order: [end, ..., middle, ..., start]
    # This puts the data in chronological order for approach curves
    Zarray = np.flip(FDCurve.iloc[:,2])  # Separation in μm
    Farray = np.flip(FDCurve.iloc[:,1])  # Force in nN
    Zarray = np.asarray(Zarray)
    Farray = np.asarray(Farray)

    # Find the maximum force and its corresponding separation
    imax = np.argmax(Farray)
    Zmax = Zarray[imax]  # Separation at maximum indentation
    Fmax = Farray[imax]  # Maximum applied force
    
    # Find the zero-force crossing (where tip first contacts surface)
    # This defines the "height" of the sample surface
    Z0 = find_first_crossing(Zarray, Farray)
    F0 = 0  # Force at contact is by definition zero
    
    # The sample height is the separation at which contact occurs
    Height = Z0
    
    # Calculate deformation as the difference between:
    # - Zero-force point (undeformed surface)
    # - Maximum force point (fully indented surface)
    defrm = Z0 - Zmax
    
    # Negative deformation is unphysical (would mean tip penetrates through sample)
    # Set to zero in these cases
    if defrm < 0: 
        defrm = 0

    # Return all values in convenient units (nm and nN)
    return Height*1000, F0, Zmax*1000, Fmax, defrm*1000


def find_zeroHeight(data):
    """
    Find the separation value where force crosses zero (surface contact point).
    
    This is a simpler version of finding height that just returns the zero-crossing
    separation value without calculating deformation.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Force-distance curve with columns:
        Column 1: Force (nN)
        Column 2: Separation (μm)
        
    Returns:
    --------
    float
        Separation at zero force crossing (μm)
        
    Notes:
    ------
    Searches only in the region between minimum and maximum force to avoid
    false zero crossings far from the contact region.
    """
    
    # Extract force and separation arrays
    Zarray = data.iloc[:,2]  # Separation in μm
    Farray = data.iloc[:,1]  # Force in nN
    
    # Find the region of interest (between min and max force)
    imax = np.argmax(Farray)
    imin = np.argmin(Farray)
    
    if imin > imax:
        # Retract case: search from max to min
        Fsub = Farray[imax:imin]
        Fsub = np.asarray(Fsub)
        # Find point closest to zero force
        idx = imax + (np.abs(Fsub)).argmin()
    elif imin < imax: 
        # Approach case: search from min to max
        Fsub = Farray[imin:imax]
        Fsub = np.asarray(Fsub)
        # Find point closest to zero force
        idx = imin + (np.abs(Fsub)).argmin()
    
    # Return the separation at the zero-force point
    return Zarray.iloc[idx]


def get_Fsep_approach(F, d, dF):
    """
    Transform approach curve data to force vs. deformation format.
    
    Converts raw force-separation data into force vs. deformation by:
    1. Finding the zero-force point (contact)
    2. Shifting deformation to start at zero at contact
    3. Applying an optional force offset
    
    Parameters:
    -----------
    F : array-like
        Force values (nN)
    d : array-like
        Separation values (nm)
    dF : float
        Force offset to apply (nN), used for drift correction
        
    Returns:
    --------
    tuple : (F_transformed, d_transformed, d0)
        F_transformed : array - Force with offset applied (nN)
        d_transformed : array - Deformation from contact point (nm)
        d0 : float - Separation offset used for transformation (nm)
        
    Notes:
    ------
    - Removes all data before the zero-force point (non-contact region)
    - Deformation is calculated as negative separation relative to contact
    - The d0 value is needed to process the corresponding retract curve
    """
    
    # Find the index where force crosses zero (contact point)
    i0 = find_index(F, 0)
    
    # Keep only data from contact onwards (discard pre-contact region)
    d = d[i0:]
    F = F[i0:]
    
    # Find the minimum separation value (reference point)
    # and flip sign to make deformation positive
    d0 = np.min(-d)
    d = -d - d0  # Deformation from contact (now positive, starts at zero)
    
    # Apply force offset (useful for correcting baseline drift)
    F = F + dF
    
    return F, d, d0


def get_Fsep_retract(F, d, dF, d0):
    """
    Transform retract curve data to force vs. deformation format.
    
    Converts raw retract curve data using the same reference point (d0)
    as the approach curve to maintain consistency between curves.
    
    Parameters:
    -----------
    F : array-like
        Force values (nN)
    d : array-like
        Separation values (nm)
    dF : float
        Force offset to apply (nN)
    d0 : float
        Separation offset from approach curve (nm)
        This ensures approach and retract use the same reference
        
    Returns:
    --------
    tuple : (F_transformed, d_transformed)
        F_transformed : array - Force with offset applied (nN)
        d_transformed : array - Deformation from contact point (nm)
        
    Notes:
    ------
    - Uses the minimum force point to define the end of useful data
    - Deformation is calculated using the same d0 as the approach curve
    - Only data from start to minimum force (pull-off) is kept
    """
    
    # Find the minimum force point (maximum adhesion/pull-off)
    imin = np.argmin(F)
    
    # Find the zero-force crossing point
    i0 = find_index(F, 0)
    
    # Keep only data from start to zero crossing
    dr = d[:i0]
    F = F[:i0] + dF  # Apply force offset
    
    # Calculate deformation using the same reference (d0) as approach curve
    # This ensures both curves are in the same coordinate system
    d = -dr - d0
    
    return F, d


def power(x, b, c):
    """
    Simple power law function: y = b * x^c
    
    Used for fitting force-deformation relationships.
    
    Parameters:
    -----------
    x : array-like
        Independent variable (force)
    b : float
        Amplitude/scale factor
    c : float
        Exponent
        
    Returns:
    --------
    array-like
        y = b * x^c
    """
    return b * np.power(x, c)


def powerlawfit(xdata, ydata):
    """
    Fit a power law relationship (y = A * x^m) to data using log-linear regression.
    
    Converts power law to linear form: log(y) = log(A) + m*log(x)
    Then uses linear regression to find optimal A and m.
    
    This is useful for analyzing force-deformation relationships in AFM,
    where power law relationships are common (e.g., Hertz model predicts
    deformation ~ force^(2/3)).
    
    Parameters:
    -----------
    xdata : array-like
        Independent variable (typically force in nN)
    ydata : array-like
        Dependent variable (typically deformation in nm)
        
    Returns:
    --------
    tuple : (x, y, A, m)
        x : array - Linearly spaced x values for plotting fit
        y : array - Fitted y values corresponding to x
        A : float - Amplitude/scale factor in y = A*x^m
        m : float - Exponent in y = A*x^m
        
    Notes:
    ------
    - Automatically removes zero and negative values (can't take log)
    - Returns NaN for A and m if fitting fails
    - Creates 50 evenly-spaced points for smooth fit curve
    
    Example:
    --------
    For Hertz contact: deformation ~ force^(2/3)
    So m should be approximately 0.667
    """
    
    # Make copies to avoid modifying originals
    x = xdata.copy()
    y = ydata.copy()
    
    # Remove zero and negative values
    valid = (x > 0) & (y > 0) & np.isfinite(x) & np.isfinite(y)
    
    if np.sum(valid) < 3:
        # Not enough valid points
        x_out = np.linspace(np.nanmin(xdata), np.nanmax(xdata), 50)
        y_out = np.full_like(x_out, np.nan)
        return x_out, y_out, np.nan, np.nan
    
    x = x[valid]
    y = y[valid]
    
    # Create smooth x array for plotting
    x_out = np.linspace(np.min(x), np.max(x), 50)
    
    try:
        # Convert to log space
        logx = np.log(x).reshape((-1, 1))
        logy = np.log(y)
        
        # Linear regression in log-log space
        model = LinearRegression().fit(logx, logy)
        
        # Extract parameters
        A = np.exp(model.intercept_)
        m = model.coef_[0]
        
        # Calculate fitted values
        y_out = A * x_out**m
        
        # Sanity check the exponent (should be between -2 and 2 for physical systems)
        if not (-2 < m < 2):
            return x_out, y_out, np.nan, np.nan
        
        return x_out, y_out, A, m
        
    except Exception as e:
        y_out = np.full_like(x_out, np.nan)
        return x_out, y_out, np.nan, np.nan