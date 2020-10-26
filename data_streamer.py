# Python Libraries
import requests
import json 
import os
import time
import argparse

# For Token Generation
from base64 import b64encode, b64decode
from hashlib import sha256
from urllib.parse import quote_plus, urlencode
from hmac import HMAC

# Import Configurations
import config

# Azure IoT Hub
URI = config.azure_uri
KEY = config.azure_key
IOT_DEVICE_ID = config.device_id
POLICY = config.policy

def parse_args():
    parser = argparse.ArgumentParser(description="Run Data Stream Server")
    parser.add_argument('--sr', type=int, default=200, help="Sample Rate of Data Collection in Hertz")
    return parser.parse_args()

def generate_sas_token(): 
    """ Generates a Shared Access Signature (SAS) Token
    
    https://docs.microsoft.com/en-us/rest/api/eventhub/generate-sas-token
    """

    expiry=3600
    ttl = time.time() + expiry
    sign_key = (quote_plus(URI) + '\n' + str(ttl)).encode('utf-8')
    signature = b64encode(HMAC(b64decode(KEY), sign_key, sha256).digest())

    rawtoken = {
        'sr' :  URI,
        'sig': signature,
        'se' : str(int(ttl))
    }

    rawtoken['skn'] = POLICY

    return 'SharedAccessSignature ' + urlencode(rawtoken)

def send_message(token, message): 
    """ Sends a message to IoT Azure Hub

    token - Shared Access Signature (SAS) Token

    message - json ready message to be sent 
    """

    url = 'https://{0}/devices/{1}/messages/events?api-version=2016-11-14'.format(URI, IOT_DEVICE_ID)
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    data = json.dumps(message)
    print("\nSending Data:")
    print(data)
    response = requests.post(url, data=data, headers=headers)

def read_from_sensortag():
    #### TEMPORARY ####
    data = 35
    return data

if __name__ == '__main__': 
    # Parse arguments
    args = parse_args()
    sample_rate = args.sr
    period = 1 / sample_rate

    # Generate Shared Access Signatures (SAS) Token for Azure
    token = generate_sas_token()

    # Get data from Sensortag at 200Hz and send a message to Azure
    while True: 
        sens_data = read_from_sensortag() #### <- WRITE THIS FUNCTION ####
        message = { "Acceleration": str(sens_data) }
        send_message(token, message)
        time.sleep(period)