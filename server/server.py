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

@app.route('/collect/<directory>')
def getData(directory):
    """Collects and saves raw data and heartbeat features

    Raw data samples saved in data/directory
    Heartbeat feature vectors aved in data/features/directory.csv
    """
    # Save raw data
    data = c.get_samples(1200, 200)
    c.saveData2(data, my_dir=directory)
    
    # Get raw data and transform into heartbeat features
    raw_data_samples = sp.getAllSavedData(directory)
    heartbeats = sp.getHeartbeatFromSamples(raw_data_samples)
    sp.saveHeartbeats(heartbeats, directory)
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

@app.route('/authenticate/<sample>')
def authenticate_sample_user(sample):
    # Define path to sample and model
    dir_path = "collector/data/features/"
    path = dir_path + sample + '.csv'
    model_path = 'collector/data/model/auth_model.pkl' #load the trained model

    # Load extracted features of user
    sample_user = pd.read_csv(path)
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
    [data,_] = sp.lowPassFilter(data, 3)
    print(data)
    return str(data)

if __name__ == '__main__':
    app.run(debug=True)