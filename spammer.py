import http.client
import json
import time
import datetime
from base64 import b64encode


#Wallet allowed rpc address
CONN = http.client.HTTPConnection("127.0.0.1:35001")
#RPC user
RPCUSER="x"
#RPC password
RPCPASSWORD="y"

AUTH = str(RPCUSER+":"+RPCPASSWORD)
HEADERS = {
    'Content-Type': "application/json",
    'Authorization': "Basic {}".format(b64encode(AUTH.encode()).decode("ascii")),
    'Cache-Control': "no-cache",
}

#Make JSON RPC (http post) call to wallet
#defaults to getbalance if no paramaters
def action(rpcaction = "getbalance", params=None):
    
    if params == None: 
        payload = {"jsonrpc": 2.0, "id": 0, "method": rpcaction}
    elif params != None:
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
    #get current wallet balance
    balance = json.loads(action("getbalance"))["result"]
    #inits

    #loop until wallet balance over 10xby
    while(balance > 10):
        sendaccounts = {}
        counter = 0
        #go over addresses and add to payee list there is balance left
        for address in addresses:
            #check  if wallet has enough for transaction fee, if not don't add address to payee list
            if balance >= 2:            
                sendaccounts.update({address.rstrip():1.00})
                balance = balance - 2
                counter =  counter + 1
        #make send many call to wallet
        res = action("sendmany", ["", sendaccounts])
        print(res)
        print("sended to {} accounts, remaining balance: {}".format(counter, balance))
        time.sleep(30)
        
if __name__ == "__main__": main()
