# Req. active token.json for searching admins gmail (created using access.json)
# SheetID to be given to checkPayments and confirmOrders 
# ./Sheets requires a token2.json (created using a credentials.json)

# TODO: Make sure the quantity of time is included in checkAmt()
#       Finish up compile Orders (be sure to include the comments)
#

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
from pprint import pprint
from googleapiclient import discovery
from Sheets.sheeter import getOrders 
from Sheets.sheeter import putPaid
import os 
import datetime
from datetime import timedelta
import ashirwadScrape
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from google.auth.transport.requests import Request


SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
creds= None
flow= None



def checkPayments(SHEET_ID, orderList):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    #Setting up the Gmail API
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    #Creating the query for the search  
    today=datetime.datetime.now()
    x =  datetime.date(today.year,today.month, today.day) + timedelta(days=1)
    # x= datetime.date(2019,11,6) + timedelta(days=1)
    tDelta= timedelta(days=-2)
    x2= x+ tDelta

    stringDate= str(x.year)+"/"+str(x.month)+"/"+str(x.day)
    stringDateAfter= str(x2.year)+"/"+str(x2.month)+"/"+str(x2.day)
    query= "from venmo@venmo.com after:"+stringDateAfter+ " before:"+ stringDate
    print("query", query)
    #Get all names (who have given an order) and the menu
    #Searches the above qurey in GMAIL 
    try:
        
        response = service.users().messages().list(userId="me",
                                                q=query).execute()
        results = service.users().labels().list(userId='me').execute()

        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        print("messages", messages)
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId="me", q=query,
                                                pageToken=page_token).execute()
            messages.extend(response['messages'])
         #Confirming each order 
        print('here2', messages)
        for message in messages:
            print('here3')
            try:
                email = service.users().messages().get(userId= 'me', id= str(message["id"])).execute()
                snippet= email['snippet']
                print(snippet)
                payerName= str.lower(snippet[:snippet.index("paid You")].strip())
                dollarPos= snippet.index("$")
                decimalPos= snippet.index(".", dollarPos)
                payerAmt= snippet[dollarPos+1:decimalPos+3].strip()
                print("PAYER=", payerName, payerAmt, orderList[payerName]["amount"])
                print((float(payerAmt)- float(orderList[payerName]["amount"])))
                orderList[payerName]["paid?"]= (float(payerAmt)- float(orderList[payerName]["amount"]))>=0.0
            except (errors.HttpError):
                print ('An error occurred:')
            except: 
                print("paying email")
    except (errors.HttpError):
        print ('An error occurred:')
    return orderList

#To Insert Menu on Sheet2 
def insertMenu(menu, sheetID): 
    toInsert= []
    for key in menu.keys(): 
            toInsert.append([key, str(menu[key])])
    print("toInsert", toInsert, len(toInsert))
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    store = file.Storage('Sheets/token2.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('Sheets/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    spreadsheet_id = sheetID 
    range_ = 'Menu!A1:B'
    value_input_option = 'RAW' 
    value_range_body = {
        "majorDimension": "ROWS",
        "range": range_,
        "values": toInsert
    }

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()

def printOrder(orders): 
    for order in orders: 
        if(len(orders[order][1])>2):
            print(order, orders[order][0],"(", orders[order][1],")")
        else:
            print(order, orders[order][0])

def compileOrder(orderList): 
    compiledOrder= {}
    total= 0 
    paid = 0 
    for name in orderList:
        if(name!= ''):
            for item,num,comments in orderList[name]["items"]:
                if(comments==None):
                    comments= ""
                if(item in compiledOrder):
                    compiledOrder[item][0]+= num
                    if(comments!=""):
                        compiledOrder[item][1]+= ", "+ comments
                else: 
                    compiledOrder[item]= [num,comments]
                print(item, num, compiledOrder[item][0]) 
                total+=num
            if(orderList[name]["paid?"]):
                paid+=1
    return [compiledOrder,total,paid]
        

def main(): 
    SheetID= "1KL0IVdpYjWVxfAsnKS9KEd_D2sad6Ajh95R-DETdV0Q"
    menu= ashirwadScrape.scraper()
    orderList= getOrders(SheetID,menu)
    orderList= checkPayments(SheetID, orderList)
    print(orderList)
    order= compileOrder(orderList)
    putPaid(orderList, SheetID)
    print("COMPILED ORDER:")
    printOrder(order[0])

if __name__ == '__main__':
    main()