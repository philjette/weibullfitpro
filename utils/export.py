import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
from utils.weibull_functions import generate_weibull_curve

def export_curve_data(shape, scale, curve_type='both', num_points=1000):
    """Generate and export curve data points."""
    # Use the same function that generates plot points to ensure consistency
    if curve_type == 'pdf':
        x, pdf = generate_weibull_curve(shape, scale, num_points=num_points, curve_type='pdf')
        df = pd.DataFrame({
            'X_Value': x,
            'Probability_Density': pdf
        })
    elif curve_type == 'cdf':
        x, cdf = generate_weibull_curve(shape, scale, num_points=num_points, curve_type='cdf')
        df = pd.DataFrame({
            'X_Value': x,
            'Cumulative_Probability': cdf
        })
    else:  # both
        x, pdf = generate_weibull_curve(shape, scale, num_points=num_points, curve_type='pdf')
        _, cdf = generate_weibull_curve(shape, scale, num_points=num_points, curve_type='cdf')
        df = pd.DataFrame({
            'X_Value': x,
            'Probability_Density': pdf,
            'Cumulative_Probability': cdf
        })

    return df

def get_csv_download(df, filename_prefix):
    """Convert DataFrame to CSV bytes for download."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    return df.to_csv(index=False).encode('utf-8'), filename

def get_excel_download(df, filename_prefix):
    """Convert DataFrame to Excel bytes for download."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue(), filename