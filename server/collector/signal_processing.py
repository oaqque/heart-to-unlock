import os
FILEPATH = os.path.dirname(os.path.realpath(__file__))+"/data/"

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
  
  return [filtered, heartSections]

def nextThreshBreaker(data, start, threshhold):
  i = 0
  gradient = 0
  for i in range(start, len(data)):
    v = data[i][0]
    if abs(v) > threshhold:
      gradient = abs(v)/v
      break
  # retData[fistIndex, PeakIndex]
  if (i > len(data)-3):
    return [-1, -1]
  return [followBackwardGradient(data, i, gradient), followForwardGradient(data, i, gradient)]

def followForwardGradient(data, start, sign):
  gradient = data[start][0]/abs(data[start][0])*sign
  prevGradient = sign
  j = start
  for j in range(start, len(data)-1):
    if gradient*prevGradient <= 0:
      break
    gradient = data[j+1][0]-data[j][0]
  return j

def followBackwardGradient(data, start, sign):
  gradient = data[start][0]/abs(data[start][0])*sign
  prevGradient = sign
  j = start
  for j in reversed(range(0, start)):
    if gradient*prevGradient <= 0:
      break
    gradient = data[j][0]-data[j-1][0]
  return j

def findHeartRateIndicies(sections, numSampleThresh=10):
  heartBeatSections = []
  initIndex = sections[0][0]
  i = 1
  while i < len(sections):
    initIndex = sections[i-1][0]
    j = i
    while j < len(sections):
      if abs(sections[j-1][1]-sections[j][0]) > numSampleThresh:
        break
      j += 1
    heartBeatSections.append([initIndex, sections[j-1][1]])
    i = j+1
  return heartBeatSections

def extract_heart_beats(data, heart_indices):
    heart_data = []
    i = 0
    for i_set in heart_indices:
        tmp_set = []
        for j in range(i_set[0], i_set[1]):
            tmp_set.append(data[j][0])
        heart_data.append(tmp_set)
        i += 1
    return heart_data

def compute_integrals(heart_sets):
    ivals = []
    abs_ints = []
    lengths = []
    for h_set in heart_sets:
        integral = 0
        abs_integral = 0
        i = 0
        for val in h_set:
            abs_integral += abs(val)
            integral += val
            i += 1
        ivals.append(integral)
        abs_ints.append(abs_integral)
        lengths.append(i)
    return [ivals, abs_ints, lengths]

# def filterFeatures(raw_data, lmin=0, lmax=100, imin=20, imax=30, aimin=20, aimax=30):
# def filterFeatures(raw_data, lmin=0, lmax=100, imin=0, imax=300, aimin=15, aimax=30):
def filterFeatures(raw_data, lmin=0, lmax=100, imin=-100, imax=300, aimin=0, aimax=1000):
  indices = []
  [f, ints, ais, l] = extract_split_features(raw_data)
  print("Unfiltered features length = " + str(len(f)))
  for i in range(len(l)):
    if l[i] > lmax or l[i] < lmin or ints[i] > imax or ints[i] < imin or ais[i] > aimax or ais[i] < aimin:
      indices.append(i)
  remove_indexes(f, indices)
  remove_indexes(ints, indices)
  remove_indexes(ais, indices)
  remove_indexes(l, indices)
  return [f, ints, ais, l]

def remove_indexes(my_list, indexes):
  for index in sorted(indexes, reverse=True):
    del my_list[index]

def getSavedData(index = 0, dir="raw/"):
  # for filename in os.listdir(FILEPATH):
  path = FILEPATH+dir
  filename = os.listdir(path)[index]
  data = []
  with open(path + filename, 'r') as File:
    printedData = File.read()
  for line in printedData.split("\n"):
    try:
      data.append([int(line)])
    except ValueError:
      pass
  return data

def extract_split_features(raw_data, thresh=2.5):
    data = bandFilter(raw_data)
    [data, featureIndices] = lowPassFilter(data, thresh)
    f = extract_heart_beats(data, featureIndices)
    [ints, abs_ints, l] = compute_integrals(f)
    return [f, ints, abs_ints, l]

def getAllSavedData(dir="raw/"):
  data = []
  for i in range(1, len(os.listdir(FILEPATH+dir))):
    data += getSavedData(i)
  return data