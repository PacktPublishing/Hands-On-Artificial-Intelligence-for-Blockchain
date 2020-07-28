import os
import sys
import flask
from flask import request, jsonify
from web3 import Web3
import web3
import json
import http
from flask_cors import CORS
import pandas as pd
from sklearn.cluster import DBSCAN

# API configurations
app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

# Defining some of the commonly used constants for interaction with Blockchain
blockchain_url = 'https://kovan.infura.io/v3/' + \
    os.environ['WEB3_INFURA_PROJECT_ID']
abi = """[{"anonymous": false,"inputs": [{"indexed": false,"internalType": "address","name": "deviceID","type": "address"},{"indexed": false,"internalType": "string","name": "latestCID","type": "string"}],"name": "MappingUpdated","type": "event"},{"inputs": [{"internalType": "address","name": "deviceID","type": "address"},{"internalType": "string","name": "latestCID","type": "string"}],"name": "setLatestCID","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "getDeviceIDsLength","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "index","type": "uint256"}],"name": "getIDByIndex","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "deviceID","type": "address"}],"name": "getLatestCID","outputs": [{"internalType": "string","name": "latestCID","type": "string"}],"stateMutability": "view","type": "function"}]"""

# Defining some of the commonly used constants for interaction with MoiBit
conn = http.client.HTTPSConnection("kfs2.moibit.io")
moibit_url = 'https://kfs2.moibit.io/moibit/v0/'
moibit_header_obj = {
    'api_key': os.environ['MOIBIT_API_KEY'],
    'api_secret': os.environ['MOIBIT_API_SECRET'],
    'content-type': "application/json"
}

# Defining the root endpoint
@app.route('/', methods=['GET'])
def home():
    return "<h1>DICTAO - Decentralized Intelligent Contact Tracing of Animals and Objects</h1><p>This is a simple demonstration of applying blockchain, decentralized storage and AI to solve the COVID-19 crisis.</p>"


# Defining the HTTP 404 response
@app.errorhandler(404)
def page_not_found(e):
    return "The given ID could not be found", 404


# Defining the HTTP 500 response
@app.errorhandler(500)
def internal_server_error(e):
    return e, 500


# Defining the main endpoint
@app.route('/api/v0/get_infections', methods=['GET'])
def get_infections():
    masterDataSet = []
    # Extracting the input parameters sent by the API calling client
    query_parameters = request.args

    # Scanning for the input parameter named 'id'
    if 'id' in query_parameters:
        # Reading the value attached to the query parameter 'id'
        id = query_parameters.get('id')
        print("Received ID from the user: "+id)

        # Checking if the value of 'id' query parameter is null
        if getLatestCID(id) == "":
            # Since no value was passed to 'id', we are returning 404
            return page_not_found(404)
        else:
            # Initiating the web3 object
            w3 = Web3(Web3.HTTPProvider(blockchain_url))

            # Loading the contract object based on the contract address and ABI
            contract = w3.eth.contract(
                os.environ['PROOF_SMART_CONTRACT_ADDRESS'], abi=abi)

            # Calling the smart contract function getDeviceIDsLength() in the smart contract
            length = contract.functions.getDeviceIDsLength().call()
            print("Length of the deviceIDs: "+str(length))
            for i in range(length):
                # Read the ID/Wallet Address from the contract
                tempId = contract.functions.getIDByIndex(i).call()
                
                # Read the latest CID of the corresponding ID
                tempHash = contract.functions.getLatestCID(tempId).call()
                
                # Based on the CID, download the latest location history from MoiBit
                jsonData = getJsonDataFromMoiBit(tempHash)
                
                '''
                Append each location update to a dataset, so that we obtain one monolithic dataset
                that contains the location history of all the sensors
                '''
                for location in jsonData:
                    masterDataSet.append(location)
            '''
            With the location history of each sensor downloaded and extracted, 
            let us print the complete dataset
            '''
            print("Generated live dataset of length: %d" % len(masterDataSet))
            
            # Write the data into a JSON file named "live_dataset.json"
            try:
                with open('live_dataset.json', 'x') as outfile:
                    json.dump(masterDataSet, outfile, indent=2)
            except FileExistsError:
                os.remove('live_dataset.json')
                print("File Removed!")
                with open('live_dataset.json', 'x') as outfile:
                    json.dump(masterDataSet, outfile, indent=2)
            
            # Send the received input ID to identify potential infections
            results = get_infected_ids(id)
            
            # With the results obtained, remove the live dataset from the server
            os.remove("live_dataset.json")

            # Build the response object which consists of the input ID and the potentially infected IDs
            response = {
                "id": id,
                "potential_infected_ids": results
            }

            # Return the JSON data as a response back to the client
            return (jsonify(response))
    else:
        return "Error: Please specify an ID to identify potential infections."


'''
get_infected_ids is the function used to identify any potential infections
made by the given ID. It returns a list of IDs that might be infected by the given ID.
'''
def get_infected_ids(input_id):
    # Reading the live dataset by the file
    basePath = os.path.dirname(os.path.abspath('live_dataset.json'))
    dflive = pd.read_json(basePath + '/' + 'live_dataset.json')

    # Setting some of the parameters for running DBSCAN algorithm to cluster the datapoints
    epsilon = 0.0018288 # a radial distance of 6 feet, which is medically presribed
    min_sample = 2 # Suggesting that a cluster needs to contain a minimum of 2 IDs

    # Defining the DBSCAN model for clustering the datapoints by passing the parameters and the lat-long input
    model = DBSCAN(eps=epsilon, min_samples=min_sample, metric='haversine').fit(dflive[['latitude', 'longitude']])
    
    # Updating the dataset with the cluster ID for each datapoint
    dflive['cluster'] = model.labels_.tolist()

    # Initiating an array for listing all the cluster IDs
    input_id_clusters = []
    
    # Scanning the updated dataset for a list of unique cluster IDs
    for i in range(len(dflive)):
        if dflive['id'][i] == input_id:
            if dflive['cluster'][i] in input_id_clusters:
                pass
            else:
                input_id_clusters.append(dflive['cluster'][i])
    
    # Initiating the result object. We'll use this to append every potentially infected ID.
    infected_ids = []

    # Scanning the updated dataset to check if other IDs exist in each cluster where the input ID already exist
    for cluster in input_id_clusters:
        if cluster != -1:
            ids_in_cluster = dflive.loc[dflive['cluster'] == cluster, 'id']
            for i in range(len(ids_in_cluster)):
                member_id = ids_in_cluster.iloc[i]
                if (member_id not in infected_ids) and (member_id != input_id):
                    infected_ids.append(member_id)
                else:
                    pass
    return infected_ids


'''
getJsonDataFromMoiBit function is used to download the location history data
for a given ID from MoiBit
'''
def getJsonDataFromMoiBit(cid):
    pre_payload = {"hash": cid}
    payload = json.dumps(pre_payload)
    conn.request("POST", moibit_url+"readfilebyhash",
                 payload, moibit_header_obj)
    res = conn.getresponse()
    if res.status == 200:
        responseObject = json.loads(res.read())
        print(
            "updateLocationHistory(): Appending the captured data to historic data.")
        return responseObject


'''
getLatestCID function is used to fetch the latest CID for coressponding IDs
'''
def getLatestCID(id):
    w3 = Web3(Web3.HTTPProvider(blockchain_url))
    contract = w3.eth.contract(
        os.environ['PROOF_SMART_CONTRACT_ADDRESS'], abi=abi)
    cid = ""
    try:
        cid = contract.functions.getLatestCID(id).call()
    except web3.exceptions.ValidationError:
        print("ID does not exist!")
        return ""
    except:
        print("Some other error occured!")
        return ""
    else:
        print(cid)
        return cid


app.run()
