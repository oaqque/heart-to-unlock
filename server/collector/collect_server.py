#!/usr/bin/python

# Python Standard Libraries
import socket
import time
import datetime
import struct
import sys
import os
from threading import Thread

# Local packages
import signal_processing as sp
import plotter as plotter

# Python packages
import numpy as np
import pandas as pd

UDP_TIMESYNC_PORT = 3001 # node listens for timesync packets on port 4003
UDP_REPLY_PORT = 3000 # node listens for reply packets on port 7005
# SENSORTAG2_ADDR = "aaaa::212:4b00:1204:b6d5"
SENSORTAG2_ADDR = "aaaa::212:4b00:1665:a880"
FILEPATH = os.path.dirname(os.path.realpath(__file__))+"/data/"

x_list = []
y_list = []
z_list = []

def setupSockets(num, freq):
  # listen on UDP socket port UDP_TIMESYNC_PORT
  recvSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
  recvSocket.bind(("aaaa::1", UDP_REPLY_PORT))
  recvSocket.settimeout(0.5)
  udpSend(num, freq)
  return recvSocket

def udpListenThread(num=600, freq=200):
  rcvSocket = setupSockets(num, freq)
  data = ""

  while 1:
    try:
      chunk, addr = rcvSocket.recvfrom( 1024 )
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
  data = udpListenThread(num, freq)   
  # (x,y,z)\n\r
  normailised = []

  tuples = data.strip("\n\r").split("\n\r")
  for t in tuples:
    d = t.strip("(").strip(")")
    split = d.split(",")
    normailised.append([int(split[2])])

  saveData(normailised, my_dir="user_2/")
  return normailised

def saveData(data, my_dir="raw/", name="data"):
  filename = name + "-" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
  dataString = ""
  for d in data:
    dataString += str(d[0]) + "\n"
  dataString.strip("\n")
  with open(FILEPATH+my_dir+filename, 'w') as file:
    file.write(dataString)

def saveData2(data, my_dir="raw/", name="data"):
  filename = name + "-" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
  dataString = ""
  for d in data:
    dataString += str(d) + "\n"
  dataString.strip("\n")
  with open(FILEPATH+my_dir+filename, 'w') as file:
    file.write(dataString)

if __name__ == "__main__":
  raw_data_samples = sp.getAllSavedData("user_1/")
  heartbeats = sp.getHeartbeatFromSamples(raw_data_samples)
  print(f"Shape of heartbeat return: {heartbeats.shape}")
  sp.saveHeartbeats(heartbeats, "./data/features/sample_false.csv")

