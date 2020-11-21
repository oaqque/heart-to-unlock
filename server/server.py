from flask import Flask, render_template
import collector.collect_server as c
import collector.signal_processing as sp
import pandas as pd
import pickle
import joblib
from flask import Response, jsonify, make_response
from collections import Counter
# from data_streamer import iothub_client_init
# from azure.iot.device import Message

# from .collector.collect_server import get_samples
app = Flask(__name__)

# client = iothub_client_init()
# MSG_TXT = '{{"acceleration": {acceleration}}}'

@app.route('/data')
def getData():
    # Send data to cloud IoT as well
    data = c.get_samples(1200, 200)
    data = sp.bandFilter(data)
    [data,heartRateIndicies] = sp.lowPassFilter(data, 3)
    # data = [[s], [s], [s], [s]]
    
    # send_to_iot(data)

    return str(data)

@app.route('/main')
def collectSamples():
    return render_template('welcome.html')

@app.route('/home')
def welcome():
    return "Navigate to either /test or /main"

@app.route('/')
def testData():
    return render_template('signalProcessing.html')


@app.route('/auth/user')
def auth_user():
    return render_template('authenticate.html')

@app.route('/authenticate/user')
def authenticate_sample_user():
    sample_user = pd.read_csv('collector/data/features/sample_false.csv') #Load extracted features of the user
    model_path = 'collector/data/model/auth_model.pkl' #load the trained model
    matrix = joblib.load(model_path)
    pred = Counter(list(matrix.predict(sample_user))) #Get frequency of every predicted class

    authentication_status = pred.most_common(1)[0][0] #Find mode of the predictions. Uses majority voting strategy
    
    if authentication_status==1:
        return make_response(jsonify({"is_success":True}), 200)
    else:
        return make_response(jsonify({"is_success":False}), 200)

@app.route('/test/data')
def testGetData():
    data = sp.getSavedData(16)
    # data = c.lowPassFilter(c.getSavedData(),2)
    data = sp.bandFilter(data)
    [data,heartRateIndicies] = sp.lowPassFilter(data, 3)
    print(data)
    # print(heartRateIndicies)
    return str(data)

# def send_to_iot(data):
#     for sample in data: 
#         msg_txt_formatted = MSG_TXT.format(acceleration=sample[0])
#         message = Message(msg_txt_formatted)
#         client.send_message(message)

if __name__ == '__main__':
    app.run(debug=True)