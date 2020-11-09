from flask import Flask, render_template
import collector.collect_server as c
from data_streamer import iothub_client_init
from azure.iot.device import Message

# from .collector.collect_server import get_samples
app = Flask(__name__)

client = iothub_client_init()
MSG_TXT = '{{"acceleration": {acceleration}}}'

@app.route('/data')
def getData():
    # Send data to cloud IoT as well
    data = c.get_samples(1200, 200)
    # data = [[s], [s], [s], [s]]
    for sample in data: 
        msg_txt_formatted = MSG_TXT.format(acceleration=sample[0])
        message = Message(msg_txt_formatted)
        client.send_message(message)

    return str(data)

@app.route('/')
def welcome():
    return render_template('welcome.html')

if __name__ == '__main__':
    app.run(debug=True)