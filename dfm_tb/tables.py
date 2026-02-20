import pandas as pd
import numpy as np
from great_tables import GT, md, html, style

# /////////////////////////////////////////////////////////////////////////////
# Define a function that generates frequency and proportions of one column
def freq_prop(df: pd.DataFrame, column: str,  by: str | None = None) -> GT:
    """
    Generates a GT table displaying frequency and proportions for a given column.

    Parameters:
        df (pd.DataFrame): The input dataframe.
        column (str): The column for which to compute frequency and proportions.
        by: A string variable to display by a second variable

    Returns:
        GT: A GT table object.

    Dependencies:
    - pandas
    - great_tables
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in dataframe.")
    

    if by is None:
        # Compute frequency and proportion
        value_counts = df[column].value_counts()
        proportions = df[column].value_counts(normalize=True).mul(100).round(1)

        # Format results as "n (%)"
        formatted = value_counts.astype(str) + " (" + proportions.astype(str) + "%)"
        
        # Create a DataFrame and return as GT object
        result_df = (
            formatted
            .reset_index()
        #   .rename(columns={"index": column, column: f"N = {len(df)}"})
            .rename(columns={0: f"N = {len(df)}"})
        )
    else:


        result_df = pd.DataFrame(columns=[column])   # or whatever your merge key is


        for b in df[by].unique():
            subset = df[df[by] == b][column]
            
            value_counts = subset.value_counts()
            proportions = subset.value_counts(normalize = True).mul(100).round(1)

            formatted = value_counts.astype(str) + " (" + proportions.astype(str) + "%)"

            sub_df = (
                formatted
                .reset_index()
                .rename(columns={0: f"{b}, N = {len(df)}"})
            )

            # Merge the data frames
            result_df = result_df.merge(sub_df, on = column, how = "outer")
    
    # Collect all of the column names and add ** suffixes and prefixes to bold the
    # column labels in the gt table
    label_map = {col: md(f"**{col}**") for col in result_df.columns}

    gt_table = (
        GT(result_df)
        .cols_label(**label_map)
    )
    
    return gt_table



# /////////////////////////////////////////////////////////////////////////////
# Define a function that generates frequencies and proportions for a set of
# columns that are a result of select all that apply questions
def all_apply(df: pd.DataFrame, columns: list, group_title: str, sort_by_percentage: bool) -> GT:
    """
    Generates a GT table displaying frequencies and proportions for 
    "select all that apply" survey questions.

    Args:
        df (pd.DataFrame): The input dataframe.
        columns (list): List of columns representing binary responses.
        group_title (str): Title for the output group.
        sort_by_percentage (bool): If True, sorts by descending frequency.

    Returns:
        GT: A GT table object.

    Dependencies:
    - pandas
    - GT
    """
    if not columns:
      raise ValueError("Column list cannot be empty.")
    
    N = len(df)  # Total sample size

    # Convert columns to binary (1 if not missing, 0 otherwise)
    temp = df[columns].notna().astype(int)

    # Initialize list to store results
    results = []

    for col in columns:
      unique_vals = temp[col].unique()
      if len(unique_vals) != 2:
          raise ValueError(f"Column '{col}' is not binary. Reformat before proceeding.")
    
      # Compute count and proportion
      count = temp[col].sum()
      proportion = (count / N) * 100

      results.append((col, count, f"{proportion:.1f}%"))

    # Convert to DataFrame
    out_df = pd.DataFrame(results, columns=[group_title, "count", "proportion"])

    # Sort if required
    if sort_by_percentage:
        out_df = out_df.sort_values(by="count", ascending=False)

    # Create formatted output column
    out_df["formatted"] = out_df.apply(lambda row: f"{row['count']} ({row['proportion']})", axis=1)

    # Keep only relevant columns
    out_df = out_df[[group_title, "formatted"]].rename(columns={"formatted": f"N = {N}"})

    return GT(out_df)


# /////////////////////////////////////////////////////////////////////////////

def summarize(data, column):
    """
    Generate a table with the mean and standard deviation of a continuous variable.

    Parameters:
    - data (pd.DataFrame): The dataset
    - column (str): The name of the continuous variable

    Returns:
    - GT object displaying the mean and standard deviation
    """
    N = data[column].notna().sum().astype(str)

    summary = (GT(pd.DataFrame({
    "Characteristic": [column],
    "Value": [f"{data[column].mean():.2f} ({data[column].std():.2f})"]
    }).rename(columns = {"Value":("N = " + N )}))
    .tab_source_note(source_note=html("<sup>1</sup> Mean (SD)")))

    return summary