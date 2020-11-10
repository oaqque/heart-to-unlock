from flask import Flask, render_template
import collector.collect_server as c
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
    data = c.bandFilter(data)
    data = c.lowPassFilter(data, 3)
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

@app.route('/test/data')
def testGetData():
    # data = c.getSavedData()
    # data = c.lowPassFilter(c.getSavedData(),2)
    data = c.bandFilter(c.getSavedData())
    data = c.lowPassFilter(data,2.5)
    # print(data)
    return str(data)

# def send_to_iot(data):
#     for sample in data: 
#         msg_txt_formatted = MSG_TXT.format(acceleration=sample[0])
#         message = Message(msg_txt_formatted)
#         client.send_message(message)

if __name__ == '__main__':
    app.run(debug=True)