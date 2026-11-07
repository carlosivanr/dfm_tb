import pandas as pd
import numpy as np
from itertools import combinations
from scipy.stats import norm
from dfm_tb.utilities import format_pval_flt
from collections import Counter

def get_steigers_z(df, corr_method):
    """
    Carlos Rodriguez, PhD. CU Anschutz Dept. of Family Medicine ---------------

    Description:
    Performs Steiger's Z test for all pairwise comparisons of correlations in 
    a DataFrame, accounting for overlapping and non-overlapping variable
    combinations. For each comparison, only complete cases are considered,
    which will result in different sample sizes if the input data contain 
    missing values. Either input all complete cases only, or manually set n if
    this will pose a problem.
        1) Steiger, 1980.  https://doi.org/10.1037/0033-2909.87.2.245
        2) Silver et al. 2010, https://doi.org/10.3200/JEXE.71.1.53-70 
            [implements eq 4]
        3) Bishara & Hittner (2012). https://doi.org/10.1037/a0028087
        4) Leys, R., et al. (2013). https://doi.org/10.1016/j.jesp.2013.03.013

    Parameters:
    df : pandas.DataFrame
        A dataframe containing the numeric variables of interest, where each 
        column represents a variable that will be correlated. Missing values
        accomodated by subsetting to the complete cases in each set of
        variables.
    
    corr_method : string
        A string specifying the correlation method "spearman" or "pearson".

    Returns:
    pandas.DataFrame

    Dependencies:
    - numpy
    - pandas
    - scipy.stats.norm
    - itertools.combinations
    - dfm_tb.utilities.format_pval_flt 
    - collections.Counter
    """

    # Steiger's Z test designed for pearson correlation coefficients [1,2]
    # possible to use on Spearman coefficients with caution [3, 4].
    if corr_method not in ["spearman", "pearson"]:
        raise ValueError("method must be either 'spearman' or 'pearson'")

    # Ensure that there are not duplicated columns in the input data frame
    if df.columns.duplicated().any():
        print("Warning: There are duplicated column names.")
    
    # Get the first order pairs (pairwise correlations between each variable)
    first_order_pairs = list(combinations(df.columns, 2))

    # Get the second order pairs (pairwise comparisons between unique correlations)
    second_order_pairs = list(combinations(first_order_pairs, 2))

    # Initiate an empty list to store results
    results = []

    for pair in second_order_pairs:
        # Flatten the two pairs into a single list from the tuple in
        # second_order_pairs to get the variables necessary for 
        # computation.
        all_vars = list(pair[0]) + list(pair[1])

        # Get the unique variables to determine which approach to use,
        # overlapping vs non-overlapping formulat and to select the columns
        # of interest
        unique_vars = list(dict.fromkeys(all_vars))

        if len(unique_vars) == 3:
            # Overlapping Steiger's Z test ------------------------------------    
            # If the length of unique_vars is 3, then use the overlapping approach of
            # Steiger's Z test. If length is 4, then use the 
            # non-overlapping approach of Steiger's Z test.
            # Overlapping AB vs BC (BC overlaps)
            # Non-overlapping AB vs CD (no overlapping variables)

            # Create a temporary data frame
            # temp = df[flat].dropna().copy()
            temp = df[unique_vars].copy()

            # Get the common sample size
            n = 348

            # Get the correlations
            corr_mat = temp.corr(method = corr_method)

            # Specify the correlations r1 r2 and r3. Comparisons are maded
            # between r1 and r2
            
            # Identify the overlapping variable  
            counts = Counter(all_vars)
            repeated = [item for item, count in counts.items() if count > 1]
            overlap_vars = tuple([x for x in all_vars if x != repeated[0]])

            r1 = corr_mat.loc[pair[0]]

            r2 = corr_mat.loc[pair[1]]

            # This will be the overlapping correlation
            r3 = corr_mat.loc[overlap_vars]

            # Calculate Steiger's z-value
            numerator = (r1 - r2) * np.sqrt(n - 3) * np.sqrt(1 + r3)
            denominator = np.sqrt(2 * (1 - r1**2 - r2**2 - r3**2 + 2 * r1 * r2 * r3))
            z = numerator / denominator
            p = 2 * (1 - norm.cdf(abs(z)))  # two-tailed p-value

            # Append results as a dictionary
            results.append({
                "Comparison": f"{pair[0][0]}-{pair[0][1]} vs. {pair[1][0]}-{pair[1][1]}",
                "z": z.round(2),
                "p-value": format_pval_flt(p)
            })
        else:
            # Non-overlapping Steiger's Z test --------------------------------

            # Create a temporary data frame
            # temp = df[flat].dropna().copy()
            temp = df[unique_vars].copy()


            # Get the common sample size
            n = len(temp)

            # Get the correlations
            corr_mat = temp.corr(method = corr_method)

            # Set the correlation values to test ----------
            var1 = unique_vars[0]
            var2 = unique_vars[1]
            var3 = unique_vars[2]
            var4 = unique_vars[3]

            r12 = corr_mat[var1][var2]
            r13 = corr_mat[var1][var3]
            r14 = corr_mat[var1][var4]
            r23 = corr_mat[var2][var3]
            r24 = corr_mat[var2][var4]
            r34 = corr_mat[var3][var4]
            # ---------------------------------------------

            # Get the average correlation between AB vs CD
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
            p = 2 * (1 - norm.cdf(abs(z)))  # two-tailed p-value

            # Append results as a dictionary
            results.append({
                "Comparison": f"{pair[0][0]}-{pair[0][1]} vs. {pair[1][0]}-{pair[1][1]}",
                "z": z.round(2),
                "p-value": format_pval_flt(p)
            })

    return(pd.DataFrame(results))
