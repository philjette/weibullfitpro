import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

def weibull_pdf(x, shape, scale):
    """Calculate Weibull PDF values."""
    return (shape / scale) * (x / scale)**(shape - 1) * np.exp(-(x / scale)**shape)

def weibull_cdf(x, shape, scale):
    """Calculate Weibull CDF values."""
    return 1 - np.exp(-(x / scale)**shape)

def weibull_hazard(x, shape, scale):
    """Calculate Weibull Hazard Function values."""
    return (shape / scale) * (x / scale)**(shape - 1)

def fit_weibull_to_points(x_points, y_points):
    """Fit Weibull parameters to given CDF points."""
    try:
        # For CDF fitting, we use the CDF function
        def weibull_cdf_fit(x, shape, scale):
            return 1 - np.exp(-(x / scale)**shape)

        # Fit using CDF points
        popt, _ = curve_fit(
            weibull_cdf_fit, 
            x_points, 
            y_points, 
            p0=[2, np.mean(x_points)],  # Better initial guess
            bounds=([0.1, 0.1], [50, 100])  # Reasonable bounds
        )
        return popt[0], popt[1]  # shape, scale
    except RuntimeError as e:
        print(f"Fitting error: {str(e)}")
        return None, None

def generate_weibull_curve(shape, scale, num_points=100, curve_type='pdf'):
    """Generate points for plotting a Weibull curve."""
    def find_truncation_point(shape, scale):
        if curve_type.lower() == 'cdf':
            # Find x where CDF reaches 0.9999
            return scale * (-np.log(1 - 0.9999))**(1/shape)
        elif curve_type.lower() == 'hazard':
            # For hazard function, use a reasonable range
            return scale * 3
        else:  # PDF
            # Find x where PDF drops below 0.0001
            # Use binary search to find the point
            x_left = 0
            x_right = scale * 10  # Start with a large range

            while x_right - x_left > 0.01:  # Precision of 0.01
                x_mid = (x_left + x_right) / 2
                pdf_value = weibull_pdf(x_mid, shape, scale)

                if pdf_value > 0.0001:
                    x_left = x_mid
                else:
                    x_right = x_mid

            return x_right

    x_max = find_truncation_point(shape, scale)
    x = np.linspace(0, x_max, num_points)

    if curve_type.lower() == 'pdf':
        y = weibull_pdf(x, shape, scale)
    elif curve_type.lower() == 'cdf':
        y = weibull_cdf(x, shape, scale)
    else:  # hazard
        y = weibull_hazard(x, shape, scale)
    return x, y

def validate_parameters(shape, scale):
    """Validate Weibull parameters."""
    try:
        shape = float(shape)
        scale = float(scale)
        if shape <= 0 or scale <= 0:
            return False, "Shape and scale parameters must be positive"
        return True, ""
    except ValueError:
        return False, "Invalid parameter values"