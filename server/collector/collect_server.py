#!/usr/bin/python

import socket
import time
import datetime
import struct
# import StringIO
from threading import Thread
import sys
import os
import signal_processing as sp
import plotter as plotter

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
  data = udpListenThread(num, freq) #.replace("(","[").replace(")","]").replace("\n\r",",")
  # (x,y,z)\n\r
  #
  normailised = []

  tuples = data.strip("\n\r").split("\n\r")
  for t in tuples:
    d = t.strip("(").strip(")")
    split = d.split(",")
    normailised.append([int(split[2])])
    # normailised.append([int(split[0]), int(split[2])])
    # normailised.append([int(split[0]) + int(split[2])])
    # [[v],[v],[v]]
  # return smooth(normailised)

  saveData(normailised)
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
  # get_samples(600,200)
  # saveData(get_samples(600,200))
  [f, i, l] = sp.filterFeatures()
  saveData2(f, "features/", "sample_true")
  print(len(i))
  # print(i)
  # print(l)
  plotter.plot_hist_pyplot(i, "Heart Integral Histogram")
  plotter.plot_hist_pyplot(l, "Heartbeat Duration Histogram")