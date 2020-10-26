This project attempts to recreate the work in [Unlock with Your Heart: Heartbeat-based Authentication on Commercial Mobile Phones](https://doi.org/10.1145/3264950) for our project in COMP6733.

We have chosen to use Contiki OS and the TI SensorTag 2650 as our chosen hardware for measuring heartbeat data through the accelerometer. 

# Setup

In order to configure the server to connect to Azure IoT Hub, use `config.py.example` as a template for entering your API keys. Remove the `.example` extension to use the config file in your code. 