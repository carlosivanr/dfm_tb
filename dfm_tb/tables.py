# /////////////////////////////////////////////////////////////////////////////
# Define a function that generates frequency and proportions of one column
def freq_prop(df: pd.DataFrame, column: str) -> GT:
    """
    Generates a GT table displaying frequency and proportions for a given column.

    Parameters:
        df (pd.DataFrame): The input dataframe.
        column (str): The column for which to compute frequency and proportions.

    Returns:
        GT: A GT table object.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in dataframe.")
    
    # Compute frequency and proportion
    value_counts = df[column].value_counts()
    proportions = df[column].value_counts(normalize=True).mul(100).round(1)

    # Format results as "n (%)"
    formatted = value_counts.astype(str) + " (" + proportions.astype(str) + "%)"
    
    # Create a DataFrame and return as GT object
    result_df = (
        formatted
        .reset_index()
        .rename(columns={"index": column, column: f"N = {len(df)}"})
    )
    
    return GT(result_df)


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
    out_df["formatted"] = out_df.apply(lambda row: f"{row['count']}, ({row['proportion']})", axis=1)

    # Keep only relevant columns
    out_df = out_df[[group_title, "formatted"]].rename(columns={"formatted": f"N = {N}"})

    return GT(out_df)


