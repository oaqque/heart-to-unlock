#!/usr/bin/python

import socket
import time
import datetime
import struct
import StringIO
from threading import Thread
import sys
import numpy as np

UDP_TIMESYNC_PORT = 3001 # node listens for timesync packets on port 4003
UDP_REPLY_PORT = 3000 # node listens for reply packets on port 7005
SENSORTAG2_ADDR = "aaaa::212:4b00:1205:2a01"

isRunning = True
x_list = []
y_list = []
z_list = []

def udpListenThread():
 # listen on UDP socket port UDP_TIMESYNC_PORT
  recvSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
  recvSocket.bind(("aaaa::1", UDP_REPLY_PORT))
  recvSocket.settimeout(0.5)

  while isRunning:
    try:
      data, addr = recvSocket.recvfrom( 1024 )
      print(data)
      split = data.split(", ")
      print(len(split))
      x = split[0]
      y = split[1]
      z = split[2]
      x_list.append(int(x))
      y_list.append(int(y))
      z_list.append(int(z))
    except socket.timeout:
      pass
    
def udpSendThread():

  sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, 0)
  sendFlag = True
  while isRunning:
    timestamp = int(time.time())


    # send UDP packet to nodes
    # change the IP Address with your sensorTag accordingly.
    # you may start with one sensortag.
    if sendFlag:
        print("Sending Init")
        sock.sendto(struct.pack("I", timestamp), (SENSORTAG2_ADDR, UDP_TIMESYNC_PORT))
        sendFlag = False
    # sock.sendto(struct.pack("I", timestamp), ("Address For Sensortag2", UDP_TIMESYNC_PORT))
    # sendto(bytes, flags, address)
    # address = (IPAddr, Port)
    
    # sleep for some seconds
    # the frequency of sending the sych timestamps packet is very importantfreadf
    # you will see how this affect the sych accuracy in your experiment
    time.sleep(1)


# start UDP listener as a thread
t1 = Thread(target=udpListenThread)
t1.start()
print("Listening for incoming packets on UDP port", UDP_REPLY_PORT)

time.sleep(1)

# start UDP timesync sender as a thread
t2 = Thread(target=udpSendThread)
t2.start()

print("Sending timesync packets on UDP port", UDP_TIMESYNC_PORT)
print("Exit application by pressing (CTRL-C)")

try:
  while True:
    # wait for application to finish (ctrl-c)
    time.sleep(1)
except KeyboardInterrupt:
  print("Keyboard interrupt received. Exiting.")
  print("Saving csv")
  np_x = np.array(x_list)
  np_y = np.array(y_list)
  np_z = np.array(z_list)
  np_data = np.vstack((np_x, np_y, np_z)).T
  np.savetxt("data/test.csv", np_data, delimiter=',')
  isRunning = False




