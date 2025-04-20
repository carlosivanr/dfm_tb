# Example function to format p-values in a column of a pandas data frame
# defined in a script named utilities.py
def format_pval_df(pvals):
    """
    Format a pandas series of p-values.
    - If p < 0.0001, return "<0.0001"
    - Else, format to specified number of digits

    Parameters:
    pvals : pandas Series or array-like
    digits : int, number of decimal digits to display

    Returns:
    Formatted pandas Series of strings
    """
    digits=4

    return pvals.apply(lambda p: "<0.0001" if p < 0.0001 else f"{p:.{digits}f}")