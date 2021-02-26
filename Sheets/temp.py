from pprint import pprint
from googleapiclient import discovery

# TODO: Change placeholder below to generate authentication credentials. See
# https://developers.google.com/sheets/quickstart/python#step_3_set_up_the_sample
#
# Authorize using one of the following scopes:
#     'https://www.googleapis.com/auth/drive'
#     'https://www.googleapis.com/auth/drive.file'
#     'https://www.googleapis.com/auth/spreadsheets'
credentials = None

service = discovery.build('sheets', 'v4', credentials=credentials)

# The ID of the spreadsheet to update.
spreadsheet_id = '1Bx9sXu1656AQhdRzt_M6Y-yEHdXxtXiFOUWaCxl4Vnc'

# The A1 notation of the values to update.
range_ = 'G4'

# How the input data should be interpreted.
value_input_option = 'RAW'  

value_range_body = {
    {
    "majorDimension": "ROWS",
    "values": [["Paid"]],
    "range": "G"+
    }
}

request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=value_range_body)
response = request.execute()
