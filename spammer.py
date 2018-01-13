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
#TIMEOUT_BETWEEN_SENDS = 3.0 #value in seconds !!!NOT USED!!!
#send amount
SEND_AMOUNT = 1
TX_FEE = 2

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

    while(True):
        try:
                 
            balance = json.loads(action("getbalance"))["result"]
            if balance > SEND_AMOUNT + TX_FEE:
                print("//////////////////////////////////////")
                #go over addresses and send if there is balance left
                for address in addresses:
                    #check  if wallet has enough for transaction fee, if not, don't add address to payee list
                    if balance >= SEND_AMOUNT + TX_FEE:            
                        #sendaccounts.update({address.rstrip():SEND_AMOUNT})
                        balance = balance - (SEND_AMOUNT + TX_FEE) #  transaction fee 1
                        res = action("sendtoaddress", [address.rstrip(), SEND_AMOUNT])
                        resobj = json.loads(res)
                        if(resobj["result"] is None and resobj["error"] is not None):
                            print("Error occurred, response: {}".format(res))
                        else:
                            print("Send done, transaction id: {}".format(resobj["result"]))
                        print("Sended {} XBY to address {} calculated \"remaining\" balance: {}".format(SEND_AMOUNT, address.rstrip(), balance))
                        print("//////////////////////////////////////")

            print("press Ctrl+C to stop")
            #time.sleep(TIMEOUT_BETWEEN_SENDS)
        except KeyboardInterrupt:
            break

if __name__ == "__main__": main()
