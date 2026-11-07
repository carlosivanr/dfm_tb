import numpy as np
import pandas as pd
from great_tables import GT, html, loc, md, style

# /////////////////////////////////////////////////////////////////////////////
def tbl_summary(
    df: pd.DataFrame,
    by: str | None = None,
    digits: int = 1,
) -> GT:
    """
    Create a descriptive summary table using great_tables.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing variables to summarize.
    by : str, optional
        Categorical column used to stratify the summary.
    digits : int, default 1
        Number of decimal places for statistics.

    Returns
    -------
    GT
        Formatted summary table.
    """

    if df.empty:
        raise ValueError("The DataFrame must not be empty.")

    if not df.columns.is_unique:
        raise ValueError("DataFrame column names must be unique.")

    if by is not None and by not in df.columns:
        raise ValueError(f"Column '{by}' not found in DataFrame.")

    if not isinstance(digits, int) or digits < 0:
        raise ValueError("digits must be a nonnegative integer.")

    variables = [col for col in df.columns if col != by]

    if not variables:
        raise ValueError("No variables available to summarize.")

    # Establish groups and their ordering
    if by is None:
        groups = [(None, df)]
    else:
        group_var = df[by]

        if (
            pd.api.types.is_numeric_dtype(group_var)
            and not isinstance(group_var.dtype, pd.CategoricalDtype)
        ):
            raise ValueError(
                "'by' must be categorical or string. "
                "Convert numeric groups to category first."
            )

        if isinstance(group_var.dtype, pd.CategoricalDtype):
            group_levels = [
                level
                for level in group_var.cat.categories
                if (group_var == level).any()
            ]
        else:
            group_levels = group_var.dropna().unique().tolist()

        groups = [
            (level, df.loc[group_var == level])
            for level in group_levels
        ]

        if not groups:
            raise ValueError("The grouping variable has no valid groups.")

    group_keys = [f"stat_{i}" for i in range(len(groups))]

    group_labels = {
        key: (
            f"**N = {len(subset):,}**"
            if by is None
            else f"**{level}**<br>N = {len(subset):,}"
        )
        for key, (level, subset) in zip(group_keys, groups)
    }

    rows = []
    summary_types = set()

    # Helper for continuous statistics
    def summarize_continuous(series):
        values = series.dropna()

        if len(values) == 0:
            return "NA"

        mean = values.mean()

        if len(values) < 2:
            return f"{mean:.{digits}f} (NA)"

        sd = values.std()

        return f"{mean:.{digits}f} ({sd:.{digits}f})"

    # Build summary rows
    for variable in variables:
        series = df[variable]

        is_continuous = (
            pd.api.types.is_numeric_dtype(series)
            and not pd.api.types.is_bool_dtype(series)
        )

        # Missing counts across groups
        missing_counts = {
            key: int(subset[variable].isna().sum())
            for key, (_, subset) in zip(group_keys, groups)
        }

        has_missing = any(count > 0 for count in missing_counts.values())

        if is_continuous:
            summary_types.add("continuous")

            row = {
                "Variable": str(variable),
                "is_level": False,
            }

            for key, (_, subset) in zip(group_keys, groups):
                row[key] = summarize_continuous(subset[variable])

            rows.append(row)

        else:
            summary_types.add("categorical")

            # Variable heading
            heading = {
                "Variable": str(variable),
                "is_level": False,
            }

            heading.update({key: "" for key in group_keys})
            rows.append(heading)

            # Respect categorical level order
            if isinstance(series.dtype, pd.CategoricalDtype):
                levels = [
                    level
                    for level in series.cat.categories
                    if (series == level).any()
                ]
            else:
                levels = series.dropna().unique().tolist()

            # Add category rows
            for level in levels:
                row = {
                    "Variable": str(level),
                    "is_level": True,
                }

                for key, (_, subset) in zip(group_keys, groups):
                    valid = subset[variable].dropna()
                    n_valid = len(valid)

                    count = int((valid == level).sum())

                    pct = (
                        100 * count / n_valid
                        if n_valid > 0
                        else 0
                    )

                    row[key] = (
                        f"{count:,} ({pct:.{digits}f}%)"
                        if n_valid > 0
                        else "NA"
                    )

                rows.append(row)

        # Add Unknown immediately after the variable summary
        # (or after its categorical levels)
        if has_missing:
            unknown_row = {
                "Variable": "Unknown",
                "is_level": True,
            }

            for key in group_keys:
                unknown_row[key] = f"{missing_counts[key]:,}"

            rows.append(unknown_row)

    summary_df = pd.DataFrame(rows)

    # Determine footnote
    notes = []

    if "categorical" in summary_types:
        notes.append("n (%)")

    if "continuous" in summary_types:
        notes.append("Mean (SD)")

    if any(df[variable].isna().any() for variable in variables):
        notes.append("Unknown = missing observations")

    footnote = "; ".join(notes)

    # Row indices for styling
    level_rows = summary_df.index[
        summary_df["is_level"]
    ].tolist()

    heading_rows = summary_df.index[
        ~summary_df["is_level"]
    ].tolist()

    # Build GT table
    table = (
        GT(summary_df)
        .cols_hide(columns="is_level")
        .cols_label(
            Variable=md("**Characteristic**"),
            **{
                key: md(label)
                for key, label in group_labels.items()
            },
        )
        .tab_source_note(footnote)
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(
                columns="Variable",
                rows=heading_rows,
            ),
        )
    )

    if level_rows:
        table = table.tab_style(
            style=style.css("padding-left: 25px;"),
            locations=loc.body(
                columns="Variable",
                rows=level_rows,
            ),
        )

    return table




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