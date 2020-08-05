import requests
import os
import datetime
import calendar
import time
import json
from web3 import Web3
import http.client

Tracking_ID = ""

url = 'https://www.googleapis.com/geolocation/v1/geolocate'
myobj = {'key': os.environ['GMAPS_API_KEY']}

conn = http.client.HTTPSConnection("kfs2.moibit.io")
moibit_url = 'https://kfs2.moibit.io/moibit/v0/'
moibit_header_obj = {
    'api_key': os.environ['MOIBIT_API_KEY'],
    'api_secret': os.environ['MOIBIT_API_SECRET'],
    'content-type': "application/json"
}

blockchain_url = 'https://kovan.infura.io/v3/' + \
    os.environ['WEB3_INFURA_PROJECT_ID']
abi = """[{"anonymous": false,"inputs": [{"indexed": false,"internalType": "address","name": "deviceID","type": "address"},{"indexed": false,"internalType": "string","name": "latestCID","type": "string"}],"name": "MappingUpdated","type": "event"},{"inputs": [{"internalType": "address","name": "deviceID","type": "address"},{"internalType": "string","name": "latestCID","type": "string"}],"name": "setLatestCID","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "getDeviceIDsLength","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "index","type": "uint256"}],"name": "getIDByIndex","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "deviceID","type": "address"}],"name": "getLatestCID","outputs": [{"internalType": "string","name": "latestCID","type": "string"}],"stateMutability": "view","type": "function"}]"""


def getGeoCordinates():
    res = requests.post(url, data=myobj)
    # print("HTTP RESPONSE STATUS FROM GOOGLE SERVERS: %d" % res.status_code)
    geoCordinates = res.json()['location']
    # accuracy = res.json()['accuracy'] # Accuracy is not considered in the POC because optimizations are out of scope
    # print("Latitude: %s" % geoCordinates['lat'])
    # print("Longitude: %s" % geoCordinates['lng'])
    # print("Accuracy of the location: %s (in metres)" % accuracy)
    lat = float("{:.7f}".format(geoCordinates['lat']))
    long = float("{:.7f}".format(geoCordinates['lng']))
    return (lat, long)


def getCurrentTime():
    dt = datetime.datetime.utcnow()
    timestamp = time.mktime(dt.timetuple())
    # print("Unix Timestamp: %d" % timestamp)
    timestamp = int(timestamp)
    return timestamp


def Marshal(Tracking_ID, lat, long, timestamp):
    # data_tuple_format = (id, lat, long, accuracy, timestamp)
    data = {"id": Tracking_ID,
            "latitude": lat,
            "longitude": long,
            "timestamp": timestamp
            }
    # json_data = json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True)
    # return json_data
    return data


def CommitTxn(id, cid):
    # print("Received wallet ID: "+id)
    # print("Received latest CID: "+cid)
    print("CommitTxn(): Connecting to the ethereum network")
    w3 = Web3(Web3.HTTPProvider(blockchain_url))
    # print(w3.eth.blockNumber)
    print("CommitTxn(): Initializing the live contract instance at " +
          os.environ['PROOF_SMART_CONTRACT_ADDRESS'])
    contract = w3.eth.contract(
        os.environ['PROOF_SMART_CONTRACT_ADDRESS'], abi=abi)
    # print(contract.address)
    # print(contract.abi)

    print("CommitTxn(): Creating a raw transaction to call smart contract function setLatestCID()")
    nonce = w3.eth.getTransactionCount(os.environ['WALLET_ADDRESS'])
    setLatestCID_txn = contract.functions.setLatestCID(
        os.environ['WALLET_ADDRESS'],
        cid,
    ).buildTransaction({
        'chainId': 42,
        'gas': 3000000,
        'gasPrice': w3.toWei('1', 'gwei'),
        'nonce': nonce,
    })
    print("CommitTxn(): Signing the raw transaction with private key")
    signed_txn = w3.eth.account.sign_transaction(
        setLatestCID_txn, private_key=os.environ['WALLET_PRIVATE_KEY'])
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    tx_hash = w3.toHex(w3.keccak(signed_txn.rawTransaction))
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print("CommitTxn(): Sucessfully updated the CID in the blockchain. Transaction receipt:\n", tx_receipt)

    print("CommitTxn(): Checking the new/latest hash for the wallet from blockchain: " +
          contract.functions.getLatestCID(os.environ['WALLET_ADDRESS']).call())
    return tx_hash


def updateLocationHistory(walletAddress, jsonData):
    (exists, cid) = checkIfFileExists(walletAddress)
    if exists:
        pre_payload = {"hash": cid}
        payload = json.dumps(pre_payload)
        conn.request("POST", moibit_url+"readfilebyhash",
                     payload, moibit_header_obj)
        res = conn.getresponse()
        if res.status == 200:
            responseObject = json.loads(res.read())
            print(
                "updateLocationHistory(): Appending the captured data to historic data.")
            responseObject.append(jsonData)
            # print(responseObject)

            updatedLocationHistory = json.dumps(responseObject, indent=2)
            # print(updatedLocationHistory)
            pre_payload = {
                "fileName": "/dictao/"+walletAddress+".json",
                "create": "true",
                "createFolders": "false",
                "pinVersion": "true",
                "text": updatedLocationHistory
            }
            payload = json.dumps(pre_payload)
            # print(payload)
            print("updateLocationHistory(): Updating the remote file /dictao/" +
                  walletAddress+".json with latest location history...")
            conn.request("POST", moibit_url+"writetexttofile",
                         payload, moibit_header_obj)
            res = conn.getresponse()
            # print(res.status)
            if res.status == 200:
                print("updateLocationHistory(): Update successful!")
                latest_cid = json.loads(res.read())['data']['Hash']
                return latest_cid
            else:
                print(
                    "updateLocationHistory(): Update FAILED!\nResponse code:"+res.status)
                print("More info from response body:\n"+res)
    else:
        print("updateLocationHistory(): Initializing a new location history!")
        init_list = []
        # updatedLocationHistory = json.dumps(jsonData, indent=2)
        init_list.append(jsonData)
        updatedLocationHistory = json.dumps(init_list, indent=2)
        # print(updatedLocationHistory)

        pre_payload = {
            "fileName": "/dictao/"+walletAddress+".json",
            "create": "true",
            "createFolders": "false",
            "pinVersion": "true",
            "text": updatedLocationHistory
        }
        payload = json.dumps(pre_payload)
        # print(payload)
        print("updateLocationHistory(): Creating a new remote file /dictao/" +
              walletAddress+".json with initial location history")
        conn.request("POST", moibit_url+"writetexttofile",
                     payload, moibit_header_obj)
        res = conn.getresponse()
        # print(res.status)
        if res.status == 200:
            print("updateLocationHistory(): Created new file successful!")
            latest_cid = json.loads(res.read())['data']['Hash']
            return latest_cid
        else:
            print(
                "updateLocationHistory(): Creation of new file FAILED!\nResponse code:"+res.status)
            print("More info from response body:\n"+res)


def checkIfFileExists(walletAddress):
    print("checkIfFileExists(): Checking if /dictao/" +
          walletAddress+".json exists.")
    pre_payload = {"path": "/dictao/"}
    payload = json.dumps(pre_payload)
    conn.request("POST", moibit_url+"listfiles", payload, moibit_header_obj)
    res = conn.getresponse()
    responseObject = json.loads(res.read())
    if res.status == 200:
        # print(responseObject['data']['Entries'])
        if responseObject['data']['Entries'] == None:
            print("checkIfFileExists(): /dictao/" +
                  walletAddress+".json does not exist!")
            return False, ""
        else:
            # print(len(responseObject['data']['Entries']))
            for fileObject in responseObject['data']['Entries']:
                # print(fileObject['Name'])
                if walletAddress+".json" == fileObject['Name']:
                    print("checkIfFileExists(): Found /dictao/"+walletAddress +
                          ".json "+"with the hash "+fileObject['Hash'])
                    return True, fileObject['Hash']
    print("checkIfFileExists(): /dictao/" +
          walletAddress+".json does not exist!")
    return False, ""


def main():
    # # Fetching the Tracking ID locally, or generating a new one
    global Tracking_ID
    # if Tracking_ID is "":
    #     Tracking_ID = createID()
    Tracking_ID = os.environ['WALLET_ADDRESS']
    print("# Setting tracking ID: ", os.environ['WALLET_ADDRESS'])

    # Getting the current geo-coordinates of the device
    print("# Getting the current geo-coordinates of the device from GMaps API")
    (lat, long) = getGeoCordinates()
    # print("Received location data: ", lat, long)

    # Reading the current UTC based Unix timestamp of the device
    print("# Reading the current UTC based Unix timestamp of the device")
    timestamp = getCurrentTime()
    # print("Got the current timestamp: ", timestamp)

    # Generate the JSON structure
    jsonData = Marshal(Tracking_ID, lat, long, timestamp)
    # print(jsonData)

    # Updating the location history to IPFS-based MoiBit network
    print("# Updating the location history to IPFS-based MoiBit network")
    latest_cid = updateLocationHistory(Tracking_ID, jsonData)
    # print(latest_cid)

    # Publishing the proof to Ethereum
    print("# Publishing the proof to Ethereum")
    txnHash = CommitTxn(Tracking_ID, latest_cid)
    print("https://kovan.etherscan.io/tx/"+txnHash)


if __name__ == "__main__":
    main()
