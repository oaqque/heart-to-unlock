This project attempts to recreate the work in [Unlock with Your Heart: Heartbeat-based Authentication on Commercial Mobile Phones](https://doi.org/10.1145/3264950) for our project in COMP6733.

We have chosen to use Contiki OS and the TI SensorTag 2650 as our chosen hardware for measuring heartbeat data through the accelerometer. 

# Setup

You would require two SensorTags to run this project.

Program udp-server.c file in one of the sensortags by navigating to the sensortag-sampler directory. 

Program RPL Border Router in another sensortag. 

Navigate to collect_server.py file in /server/collector directory. 

Change the SENSORTAG2_ADDR tothe IPV6 address of the sensortag running UDP Server. 

Please ensure you have Python3 installed on your system. Then install the dependencies by running pip3 install requirements.txt

In the server directory, run the following command in the terminal: export FLASK_APP = server.py

Run the following command in the terminal: flask run

Navigate to http://localhost:5000/collect/true to collect data for an actual user and train the model. 

Navigate to http://localhost:5000/authenticate/true to authenticate that user. 
