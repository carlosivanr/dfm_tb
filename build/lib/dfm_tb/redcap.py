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
    import requests
    from io import StringIO
    import pandas as pd


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
    r = requests.post('https://redcap.ucdenver.edu/api/', data = form_data)

    # Convert the redcap data to a DataFrame
    df = pd.read_csv(StringIO(r.text), low_memory = False)

    return df




