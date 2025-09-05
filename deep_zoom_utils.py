#!/usr/bin/env python3

"""
Utility functions for deep zoom operations in fractal visualization.
"""

import math

def estimate_required_iterations(zoom_level, base_iterations):
    """
    Estimate the required number of iterations based on zoom level.
    As we zoom deeper, more iterations are needed for detail.
    
    Args:
        zoom_level: Current zoom level multiplier
        base_iterations: Base iteration count at zoom level 1.0
        
    Returns:
        int: Estimated iterations needed
    """
    # Logarithmic scale works well for iteration scaling
    if zoom_level <= 1.0:
        return base_iterations
        
    # Use log base 10 of the zoom level plus 1 to ensure continuous growth
    estimated = int(base_iterations * math.log10(zoom_level + 1) + base_iterations)
    
    # Cap at some reasonable maximum (50,000 is a good limit for most GPUs)
    return min(estimated, 50000)

def adjust_color_parameters(zoom_level):
    """
    Adjust color parameters based on zoom level to maintain visual interest.
    
    Args:
        zoom_level: Current zoom level multiplier
        
    Returns:
        dict: Adjusted color parameters
    """
    # At deeper zooms, we often want more color variation
    if zoom_level < 10:
        stripe_density = 16
        cycle_density = 32
    elif zoom_level < 100:
        stripe_density = 20
        cycle_density = 48
    elif zoom_level < 1000:
        stripe_density = 24
        cycle_density = 64
    else:
        stripe_density = 32
        cycle_density = 96
    
    return {
        "stripe_s": stripe_density,
        "ncycle": cycle_density
    }

def get_precision_at_zoom(zoom_level):
    """
    Get numerical precision info for a given zoom level.
    
    Python floats are 64-bit (double precision) with ~15-17 decimal digits of precision.
    This function estimates how many decimal places are needed at the current zoom.
    
    Args:
        zoom_level: float
            Current zoom level
            
    Returns:
        dict: Precision information
    """
    # Calculate decimal digits needed for the current zoom
    # Each 10x zoom requires ~1 more decimal digit
    # Guard against zero/negative values
    safe_zoom = max(float(zoom_level), 1.0)
    decimal_digits_needed = max(1, int(math.log10(safe_zoom)) + 2)
    
    # Check if we're approaching float64 precision limits
    float64_max_digits = 15
    precision_warning = decimal_digits_needed > float64_max_digits * 0.8
    
    return {
        'decimal_digits_needed': decimal_digits_needed,
        'precision_warning': precision_warning,
        'float64_max_digits': float64_max_digits,
        'precision_percent': min(100, decimal_digits_needed / float64_max_digits * 100)
    }
