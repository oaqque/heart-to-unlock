#!/usr/bin/python

import socket
import time
import datetime
import struct
# import StringIO
from threading import Thread
import sys
import os
# import numpy as np

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

def bandFilter(data, windowSize=100):
  returnData = []
  window = []
  tot = 0.0
  num = 0
  avg = 0.0
  m = min(windowSize, len(data)-1)
  for i in range(0,m):
    sample = data[i]
    window.append(sample[0])
    tot += sample[0]
    num += 1
  avg = tot/num

  for i, sample in enumerate(data):
    res = 0
    if i < windowSize or i > len(data)-windowSize:
      res = sample[0]-avg
      returnData.append([sample[0]-avg])
    else:
      tot += sample[0]-window.pop(0)
      window.append(sample[0])
      avg = tot/num
      res = sample[0] - avg
    returnData.append([res])

  return returnData

def lowPassFilter(data, filterVal=2):
  filtered = []
  i = 0
  sections = []
  while i < len(data):
    # s = data[i]
    # v = s[0]
    # if abs(v) < filterVal:
    #   filtered.append([0])
    # else:
    #   filtered.append([v])
    # i += 1
    indices = nextThreshBreaker(data, i, filterVal)
    i = indices[1]
    i += 1
    if i <= 0:
      break
    sections.append(indices)

  heartSections = findHeartRateIndicies(sections)
  i = 0
  for j in range(0, len(heartSections)):
    while (i < heartSections[j][0]):
      filtered.append([0])
      i += 1
    while (i < heartSections[j][1]):
      filtered.append(data[i])
      i += 1
  while (i < len(data)):
    filtered.append([0])
    i += 1
  
  return filtered

def nextThreshBreaker(data, start, threshhold):
  i = 0
  gradient = 0
  for i in range(start, len(data)):
    v = data[i][0]
    if abs(v) > threshhold:
      gradient = abs(v)/v
      break
  # retData[fistIndex, PeakIndex]
  print("Location is "+ str(i))
  if (i > len(data)-3):
    return [-1, -1]
  return [followBackwardGradient(data, i, gradient), followForwardGradient(data, i, gradient)]

def followForwardGradient(data, start, sign):
  print(sign)
  print(start)
  gradient = data[start][0]/abs(data[start][0])*sign
  prevGradient = sign
  j = start
  for j in range(start, len(data)-1):
    if gradient*prevGradient <= 0:
      print("breaking " + str(j))
      print(data[j+1][0])
      break
    gradient = data[j+1][0]-data[j][0]
  return j

def followBackwardGradient(data, start, sign):
  print(sign)
  print(start)
  gradient = data[start][0]/abs(data[start][0])*sign
  print("Gradient = " + str(gradient))
  prevGradient = sign
  j = start
  for j in reversed(range(0, start)):
    if gradient*prevGradient <= 0:
      print("breaking " + str(j))
      break
    gradient = data[j][0]-data[j-1][0]
  return j

def findHeartRateIndicies(sections, numSampleThresh=10):
  heartBeatSections = []
  initIndex = sections[0][0]
  i = 1
  while i < len(sections):
    initIndex = sections[i-1][0]
    print(initIndex)
    j = i
    while j < len(sections):
      if abs(sections[j-1][1]-sections[j][0]) > numSampleThresh:
        break
      j += 1
    heartBeatSections.append([initIndex, sections[j-1][1]])
    i = j+1
  return heartBeatSections
    
def saveData(data):
  filename = "data-" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
  dataString = ""
  for d in data:
    dataString += str(d[0]) + "\n"
  dataString.strip("\n")
  with open(FILEPATH+filename, 'w') as file:
    file.write(dataString)

def getSavedData():
  # for filename in os.listdir(FILEPATH):
  filename = os.listdir(FILEPATH)[8]
  data = []
  with open(FILEPATH + filename, 'r') as File:
    printedData = File.read()
  for line in printedData.split("\n"):
    try:
      data.append([int(line)])
    except ValueError:
      pass

  return data

if __name__ == "__main__":
  # get_samples(600,200)
  # saveData(get_samples(600,200))
  data = bandFilter(getSavedData())
  data = lowPassFilter(data, 2.5)
  # print(data)
  # indices = nextThreshBreaker(data, 580, 3)
  # print(indices)
  # print(len(data))
  # print(getSavedData())