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
  return smooth(normailised)

def smooth(data, alpha=0.2):
  # Data = [[v],[v],[v]]
  returnData = []
  returnData.append([data[0][0]])


  # filtered = lowPassFilter(data)
  filtered = data
  
  for i, sample in enumerate(filtered):
    stprev = returnData[-1][0]
    xtprev = sample[0]
    st = stprev + alpha * (xtprev - stprev)
    # returnData.append([filtered[i][0],st])
    returnData.append([st])
  return returnData

def lowPassFilter(data, filterVal=2):
  tot = 0
  num = 0
  for s in data:
    tot += s[0]
    num += 1
  avg = tot/num
    
  filtered = []
  i = 0
  while i < len(data):
    s = data[i]
    v = s[0]
    j=0
    prev = s[0]
    gradient=0
    prevGrad=0
    lastIndex = 0
    while abs(avg - data[i+j][0]) < filterVal:
      if i+j == len(data)-1:
        break
      gradient = prev-data[i+j][0]
      if gradient*prevGrad < 0:
        lastIndex = i+j
      prev = data[i+j][0]
      prevGrad = gradient
      v = s[0]
      j += 1
    for k in range(0,lastIndex):
        filtered.append([v])
    if lastIndex == 0:
      filtered.append([v])
    i += lastIndex+1
  return filtered


if __name__ == "__main__":
  # get_samples(600,200)
  print(get_samples(100,200))