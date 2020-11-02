#!/usr/bin/python

import socket
import time
import datetime
import struct
# import StringIO
from threading import Thread
import sys
# import numpy as np

UDP_TIMESYNC_PORT = 3001 # node listens for timesync packets on port 4003
UDP_REPLY_PORT = 3000 # node listens for reply packets on port 7005
SENSORTAG2_ADDR = "aaaa::212:4b00:1204:b6d5"

x_list = []
y_list = []
z_list = []

def udpListenThread(num=600, freq=200):
 # listen on UDP socket port UDP_TIMESYNC_PORT
  recvSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
  recvSocket.bind(("aaaa::1", UDP_REPLY_PORT))
  recvSocket.settimeout(0.5)
  data = ""

  udpSend(num, freq)

  while 1:
    try:
      chunk, addr = recvSocket.recvfrom( 1024 )
      # print(chunk)
      if "End of data" in chunk:
        break
      else:
        data += chunk
    except socket.timeout:
      pass
  return data
    
def udpSend(num=600, freq=200):
  sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, 0)
  string = "GET /acceleration/"+str(num)+"/"+str(freq)+" "
  print("Calling: " + string + "\n")
  sock.sendto(string, (SENSORTAG2_ADDR, UDP_TIMESYNC_PORT))

def get_samples(num=600, freq=200):
  return udpListenThread(num, freq).replace("(","[").replace(")","]").replace("\n\r",",")

if __name__ == "__main__":
  print(get_samples(600,200))
# if __name__ == "__main__":
#   # start UDP listener as a thread
#   t1 = Thread(target=udpListenThread)
#   t1.start()
#   print("Listening for incoming packets on UDP port", UDP_REPLY_PORT)

#   time.sleep(1)

#   # start UDP timesync sender as a thread
#   t2 = Thread(target=udpSendThread)
#   t2.start()

#   print("Sending packets on UDP port", UDP_TIMESYNC_PORT)
#   print("Exit application by pressing (CTRL-C)")

#   try:
#     while True:
#       # wait for application to finish (ctrl-c)
#       time.sleep(1)
#   except KeyboardInterrupt:
#     print("Keyboard interrupt received. Exiting.")
#     print("Saving csv")

#     #np_x = np.array(x_list)
#     #np_y = np.array(y_list)
#     #np_z = np.array(z_list)
#     #np_data = np.vstack((np_x, np_y, np_z)).T
#     #np.savetxt("data/test.csv", np_data, delimiter=',')
#     isRunning = False
