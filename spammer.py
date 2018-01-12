import http.client
import json
import time
import datetime
from base64 import b64encode


#Wallet allowed rpc address and port
CONN = http.client.HTTPConnection("127.0.0.1:35001")
#RPC user
RPCUSER = "x"
#RPC password
RPCPASSWORD = "y"
#timeinterval for sends
TIMEOUT_BETWEEN_SENDS = 3.0 #value in seconds
#send amount
SEND_AMOUNT = 1.00

AUTH = str(RPCUSER+":"+RPCPASSWORD)
HEADERS = {
    'Content-Type': "application/json",
    'Authorization': "Basic {}".format(b64encode(AUTH.encode()).decode("ascii")),
    'Cache-Control': "no-cache",
}

#Make JSON RPC (http post) call to wallet
#defaults to getbalance if no paramaters
def action(rpcaction = "getbalance", params=None):
    
    if params is None: 
        payload = {"jsonrpc": 2.0, "id": 0, "method": rpcaction}
    elif params is not None:
        payload = {"jsonrpc": 2.0, "id": 0, "method": rpcaction, "params": params}
    CONN.request("POST", "", json.dumps(payload), HEADERS)
    res = CONN.getresponse()
    data = res.read()
    return data

#get testnet addresses from addresses.txt
def getaddresses():
    addresses = []
    with open("adresses.txt") as f:
        addresses = f.readlines()
    return addresses

def main():
    #get addresses where to send
    addresses = getaddresses()
    #get wallet accounts
    accountnames = json.loads(action("listaccounts"))["result"]

    #loop until wallet balance over 10xby
    while(True):
        try:
            #send by wallet account
            for account in accountnames.keys():
                if account is None:
                    account = "\"\""
                sendaccounts = {}
                counter = 0
                #get current account balance        
                balance = json.loads(action("getbalance", [account]))["result"]
                if balance > SEND_AMOUNT:
                    print("//////////////////////////////////////")
                    print("Sendig from account: \"{}\" balance: {}".format(account, balance))
                    #go over addresses and add to payee list if there is balance left
                    for address in addresses:
                        #check  if wallet has enough for transaction fee, if not, don't add address to payee list
                        if balance >= SEND_AMOUNT:            
                            sendaccounts.update({address.rstrip():SEND_AMOUNT})
                            balance = balance - 2.0 # I don't know whats real transaction fee per address in sendmamy, so using 1
                            counter =  counter + 1
                    #make sendmany call to wallet
                    res = action("sendmany", [account, sendaccounts])
                    resobj = json.loads(res)
                    if(resobj["result"] is None and resobj["error"] is not None):
                        print("Error occurred, response: {}".format(res))
                    else:
                        print("Send done, transaction id: {}".format(resobj["result"]))
                    print("sended to {} accounts, from Account \"{}\" calculated \"remaining\" balance: {}".format(counter, account, balance))
                    print("//////////////////////////////////////")
                    print("press Ctrl+C to stop")
                    time.sleep(TIMEOUT_BETWEEN_SENDS)
        except KeyboardInterrupt:
            break

if __name__ == "__main__": main()
