# Python Libraries
import requests
import json 
import os
import time

# Import Configurations
import config

# Azure IoT Hub
URI = config.azure_uri
KEY = config.azure_key
IOT_DEVICE_ID = config.device_id
POLICY = config.policy