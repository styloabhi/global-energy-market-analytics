from millify import millify


def format_number(value, decimals=2):
    """
    Safely format numbers for display.
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def format_percentage(value, decimals=2):
    """
    Format percentage values safely.
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_large_number(value, precision=2):
    """
    Format large numbers using millify (e.g. 1.2M, 3.4B)
    """
    if value is None:
        return "N/A"
    return millify(value, precision=precision)


def normalize_series(series):
    """
    Normalize a price series for comparison charts.
    """
    return series / series.iloc[0] * 100
