# /////////////////////////////////////////////////////////////////////////////
# Download REDCap report
def pull_report(token, id, type):
    """
    Download a REDCap report.

    Parameters:
    token : a string, of the API token saved to a Windows environmental 
      variable
    id : a string of the REDCap report id (found online in the REDCap Project)
    type : a string identifying raw or label for the data format

    Returns:
    Returns a pandas data frame

    Example:
    baseline = pull_report("token", "id", "label")

    Dependencies
    os
    requests
    StringIO
    pandas

    """
    import os
    from io import StringIO

    import pandas as pd
    import requests


    form_data = {
        'token': os.getenv(token),
        'content': 'report',
        'format': 'csv',
        'report_id': id,
        'csvDelimiter': '',
        'rawOrLabel': type,
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'returnFormat': 'csv'
    }

    # Create a response object
    r = requests.post('https://redcap.ucdenver.edu/api/', data = form_data, verify=False)

    # Convert the redcap data to a DataFrame
    df = pd.read_csv(StringIO(r.text), low_memory = False)

    return df


# /////////////////////////////////////////////////////////////////////////////
# Convert timestamps to date
def convert_timestamps(data):
    """
    Convert timestamps from a RedCap data set to date format.

    Parameters:
    df : a pandas data frame

    Returns:
    Returns a pandas data frame

    Example:
    data = convert_timestamps(data)

    Dependencies
    os
    requests
    StringIO
    pandas

    """
    from datetime import datetime
    
    import pandas as pd

    # Set the columns by searching for the suffix "_timestamp"
    timestamp_cols = data.columns[data.columns.str.endswith('_timestamp')].tolist()

    for col in timestamp_cols:
        data[col] = pd.to_datetime(
          data[col], 
          format="%Y-%m-%d %H:%M:%S", 
          errors="coerce"
        ).dt.date

    # Print the columns modified to the terminal
    timestamp_cols = data.columns[data.columns.str.endswith('_timestamp')].tolist()
    print("The following columns were modified:")
    for col in timestamp_cols:
        print(f"  - {col}")

    # Return the modified data frame    
    return data
