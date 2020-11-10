from flask import Flask, render_template
from flask_socketio import Sockets
import collector.collect_server as c
import socket
# from data_streamer import iothub_client_init
# from azure.iot.device import Message

# from .collector.collect_server import get_samples
app = Flask(__name__)

sockets = Sockets(app)

# client = iothub_client_init()
# MSG_TXT = '{{"acceleration": {acceleration}}}'

@app.route('/data')
def getData():
    # Send data to cloud IoT as well
    data = c.get_samples(600, 200)
    # data = [[s], [s], [s], [s]]

    # send_to_iot(data)

    return str(data)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@sockets.route('/wsData')
def send_ws_data(ws):
    rcvSocket = c.setupSockets(600, 200)
    while True:
        try:
            chunk, addr = rcvSocket.recvfrom( 1024 )
            # print(chunk)
            if "End of data" in chunk:
                break
            else:
                ws.send(chunk)
        except socket.timeout:
            pass

# def send_to_iot(data):
#     for sample in data: 
#         msg_txt_formatted = MSG_TXT.format(acceleration=sample[0])
#         message = Message(msg_txt_formatted)
#         client.send_message(message)

if __name__ == '__main__':
    app.run(debug=True)