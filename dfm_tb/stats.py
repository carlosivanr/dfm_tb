import pandas as pd
import numpy as np
from itertools import combinations
from scipy.stats import norm
from dfm_tb.utilities import format_pval_flt

def get_steigers_z(df, corr_method):
    """
    Carlos Rodriguez, PhD. CU Anschutz Dept. of Family Medicine ---------------

    Description:
    Performs Steiger's Z test for all pairwise comparisons of correlations in 
    a DataFrame, accounting for overlapping and non-overlapping variable
    combinations.
        1) Steiger, 1980.  https://doi.org/10.1037/0033-2909.87.2.245
        2) Silver et al. 2010, https://doi.org/10.3200/JEXE.71.1.53-70 
            [implements eq 4]
        3) Bishara & Hittner (2012). https://doi.org/10.1037/a0028087
        4) Leys, R., et al. (2013). https://doi.org/10.1016/j.jesp.2013.03.013

    Parameters:
    df : pandas.DataFrame
        A dataframe containing the numeric variables of interest, where each 
        column represents a variable that will be correlated. Missing values
        accomodated by finding the common rows 
    
    corr_method : string
        A string specifying the correlation method "spearman" or "pearson".

    Returns:
    pandas.DataFrame

    Dependencies:
    - numpy
    - pandas
    - scipy.stats.norm
    - itertools.combinations
    """

    # Steiger's Z test designed for pearson correlation coefficients [1,2]
    # possible to use on Spearman coefficients with caution [3, 4].
    if corr_method not in ["spearman", "pearson"]:
        raise ValueError("method must be either 'spearman' or 'pearson'")

    # Get the first order pairs (pairwise correlations between each item)
    first_order_pairs = list(combinations(df.columns, 2))

    # Get the second order pairs (pairwise comparisons of all unique correlations)
    second_order_pairs = list(combinations(first_order_pairs, 2))

    # Initiate an empty list to store results
    results = []

    for pair in second_order_pairs:
        # Flatten the two pairs into a single list
        flat = list(pair[0]) + list(pair[1])

        # Get the unique values in flat while preserving the order to determine
        # whether or not to use the overlapping approach or not.
        flat = list(dict.fromkeys(flat))

        if len(flat) == 3:
            # Overlapping Steiger's Z test ------------------------------------    
            # If the length of flat == 3, then use the overlapping approach of
            # Steiger's Z test. If length of flat == 4, then use the 
            # non-overlapping approach of Steiger's Z test.
            # Overlapping AB vs BC (BC overlaps)
            # Non-overlapping AB vs CD (no overlapping variables)


            # Create a temporary data frame
            temp = df[flat].dropna().copy()

            # Get the common sample size
            n = len(temp)

            # Get the correlations
            corr_mat = temp.corr(method = corr_method)

            # Create a mask, just a bunch of true/false values
            mask = np.triu(np.ones_like(corr_mat, dtype=bool), k=1)

            # Get the three correlation values
            upper_vals = corr_mat.to_numpy()[mask]

            # Set the correlation values to test
            r12 = upper_vals[0]
            r13 = upper_vals[1]
            r23 = upper_vals[2]

            # Calculate Steiger's z-value
            numerator = (r12 - r13) * np.sqrt(n - 3) * np.sqrt(1 + r23)
            denominator = np.sqrt(2 * (1 - r12**2 - r13**2 - r23**2 + 2 * r12 * r13 * r23))
            z = numerator / denominator
            p_value = 2 * (1 - norm.cdf(abs(z)))  # two-tailed p-value

            # Append results as a dictionary
            results.append({
                "Comparison": f"{pair[0][0]}-{pair[0][1]} vs. {pair[1][0]}-{pair[1][1]}",
                "z": z.round(2),
                "p-value": format_pval_flt(p_value)
            })
        else:
            # Non-overlapping Steiger's Z test --------------------------------

            # Create a temporary data frame
            temp = df[flat].dropna().copy()

            # Get the common sample size
            n = len(temp)

            # Get the correlations
            corr_mat = temp.corr(method = corr_method)
            
            # Create a mask, just a bunch of true/false values
            mask = np.triu(np.ones_like(corr_mat, dtype=bool), k=1)

            # Get the three correlation values
            upper_vals = corr_mat.to_numpy()[mask]

            # Set the correlation values to test
            r12 = upper_vals[0]
            r13 = upper_vals[1]
            r14 = upper_vals[2]
            r23 = upper_vals[3]
            r24 = upper_vals[4]
            r34 = upper_vals[5]

            # Get the average correlation
            r_bar = 0.5 * (r12 + r34)

            # Compute the numerator s_12,34
            s_num = (
                (r13 - r_bar * r23) * (r24 - r_bar * r23) +
                (r14 - r_bar * r13) * (r23 - r_bar * r13) +
                (r13 - r_bar * r14) * (r24 - r_bar * r14) +
                (r14 - r_bar * r24) * (r23 - r_bar * r24)
            )

            # Compute the denominator
            s_denom = (1 - r_bar**2) * (1 - r_bar**2)
            s_1234 = 0.5 * s_num / s_denom

            # Compute the Fisher Z-transform of r12 and r34
            z12 = np.arctanh(r12)
            z34 = np.arctanh(r34)

            # Calculate Steiger's Z value
            z = np.sqrt(n - 3) * (z12 - z34) / np.sqrt(2 - 2 * s_1234)

            # Get the p-value
            p_value = 2 * (1 - norm.cdf(abs(z)))  # two-tailed p-value

            # Append results as a dictionary
            results.append({
                "Comparison": f"{pair[0][0]}-{pair[0][1]} vs. {pair[1][0]}-{pair[1][1]}",
                "z": z.round(2),
                "p-value": format_pval_flt(p_value)
            })

    return(pd.DataFrame(results))

