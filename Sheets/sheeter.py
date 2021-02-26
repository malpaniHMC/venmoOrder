from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.json.
def getOrders(sheetID, menu):
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('Sheets/token.pickle'):
        with open('Sheets/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Sheets/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('Sheets/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheetID,
                                range="Orders!B5:I100").execute()
    result = result.get('values', [])
    orderList= {}
    print(result)
    orders = result
    cnt= 4

    for order in orders:
        if(len(order)<5):
            continue
        cnt+=1 
        name = str.lower(order[0].lstrip(" ").rstrip(" "))
        orderItem= str.lower(order[2].lstrip(" ").rstrip(" "))
        orderNo=1 #Quantity
        if(name==""):
            continue
        print("current", order)
        orderNo= int(order[4])
       
        comments= None
        
       
        if(len(order)>7):
            comments= str.lower(order[-1].lstrip(" ").rstrip(" "))
        try:
            orderAmt= round(menu[orderItem],2)
        except(KeyError):
            print("order ERROR: ", order)
            continue    
        if(orderItem== "box with garlic naan"):
            print(orderItem, orderNo)
        if(name in orderList):
            orderList[name]["items"].append([orderItem,orderNo, comments]) 
            orderList[name]["amount"]= round((orderAmt*orderNo) +orderList[name]["amount"],2)
            orderList[name]["row"].append(cnt)
        else: 
            orderList[name]= {"items":[[orderItem,orderNo,comments]], 
                                "amount": orderAmt*orderNo,
                                "paid?": False,
                                "row": [cnt] }
    return orderList        


def putPaid(orderList, sheetID):
    for name in orderList:
        if(orderList[name]["paid?"]):
            for row in orderList[name]["row"]:
                print(row)
                spreadsheet_id= sheetID
                range_ = "Orders!"+'J'+ str(row)
                value_input_option = 'RAW'  
                value_range_body = {
                    "majorDimension": "ROWS",
                    "values": [["Paid"]],
                    "range": "Orders!"+'J'+ str(row)
                }
                # SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
                # store = file.Storage('Sheets/token2.json')
                # creds = store.get()
                # if not creds or creds.invalid:
                #     flow = client.flow_from_clientsecrets('Sheets/credentials.json', SCOPES)
                #     creds = tools.run_flow(flow, store)
                # service = build('sheets', 'v4', http=creds.authorize(Http()))
                SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
                creds = None
                # The file token.pickle stores the user's access and refresh tokens, and is
                # created automatically when the authorization flow completes for the first
                # time.
                if os.path.exists('Sheets/token.pickle'):
                    with open('Sheets/token.pickle', 'rb') as token:
                        creds = pickle.load(token)
                # If there are no (valid) credentials available, let the user log in.
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'Sheets/credentials.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open('Sheets/ token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
                service = build('sheets', 'v4', credentials=creds)
                request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=value_range_body)
                response = request.execute()
    print("DONE")
