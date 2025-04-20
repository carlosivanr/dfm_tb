# /////////////////////////////////////////////////////////////////////////////
# Format one p-value from a statsmodel test
def format_pval_flt(p, digits):
    """
    Format a numpy floating-point number.
    - If p < 0.0001, return "<0.0001"
    - Else, format to specified number of digits

    Parameters:
    p : a numpy floating-point number
    digits : int, number of decimal digits to display

    Returns:
    Formatted string
    """
    # should change the name to format_pval_flt
    # if isinstance(p, np.ndarray):
    #     p = p.item()  # Extracts the first element as a float

    # Set default number of digits if none provided
    if digits is None:
        digits = 4

    
    if p < 0.0001:
        return "<0.0001"
    else:
        return f"{p:.{digits}f}"




# /////////////////////////////////////////////////////////////////////////////
# Format p-values in a column of a pandas data frame
def format_pval_df(pvals, digits = None):
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
    # Set default number of digits if none provided
    if digits is None:
        digits = 4

    return pvals.apply(lambda p: "<0.0001" if p < 0.0001 else f"{p:.{digits}f}")
