import os
import numpy as np
import scipy.signal as signal
FILEPATH = os.path.dirname(os.path.realpath(__file__))+"/data/"

def smooth(data: list, alpha=0.2):
  """A moving average smoothing algorithm

  Data takes input of the following [[v], [v], [v], [v]]
  Returns a smooth signal of the same format.
  """

  # Data = [[v],[v],[v]]
  returnData = []
  
  for i, sample in enumerate(data):
    stprev = returnData[-1][0]
    xtprev = sample[0]
    st = stprev + alpha * (xtprev - stprev)
    returnData.append([st])
  return returnData

def bandFilter(data, windowSize=100):
  """Applies a bandfilter on signal

  Data takes input of the following [[v], [v], [v], [v]]
  Returns a signal of the same format.
  """

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
  """Applies a low pass filter on signal

  Data takes input of the following [[v], [v], [v], [v]]
  """

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

def getSavedData(index = 0, dir="user_1/"):
  # for filename in os.listdir(FILEPATH):
  path = FILEPATH+dir
  filename = os.listdir(path)[index]
  data = []
  with open(path + filename, 'r') as File:
    printedData = File.read()
  for line in printedData.split("\n"):
    try:
      data.append(int(line))
    except ValueError:
      pass
  return data

def extract_split_features(raw_data, thresh=2.5):
    data = bandFilter(raw_data)
    [data, featureIndices] = lowPassFilter(data, thresh)
    f = extract_heart_beats(data, featureIndices)
    [ints, abs_ints, l] = compute_integrals(f)
    return [f, ints, abs_ints, l]

def norm(data):
    """Normalises a signal so that the amplitude will lie between 0 and 1"""

    new_data = np.array([])
    maxr = max(data)
    minr = min(data)
    
    for i, y in enumerate(data):
        new_data = np.append(((y-minr) / (maxr - minr)), new_data)
    return new_data

def normalise_mm(data, maximum, minimum):
  # data = [[x], [x], [x]]
  normalised = []
  for x in data: 
    xnew = (x - minimum) / (maximum - minimum)
    normalised.append(xnew)
  return normalised

def normalise_features(features):
  maximum = 0
  minimum = 0
  for feature in features:
    if max(feature) > maximum:
      maximum = max(feature)
    else: 
      continue
  for feature in features:
    if min(feature) < minimum:
      minimum = min(feature)
    else: 
      continue
  new_features = []
  for feature in features:
    new_feature = normalise_mm(feature, maximum, minimum)
    new_features.append(new_feature)
  return new_features

def getAllSavedData(fn):
  """Retrieves all samples in the folder FILEPATH + fn

  Returns a list of samples [[sample],[sample],[sample]]
  """
  data = []
  for i in range(1, len(os.listdir(FILEPATH+fn))):
    data.append([getSavedData(i)]) 
  return data

def sigmoid(data):
  """Applied a sigmoid to the input data"""
  return 1/(1+np.exp(-data))

def find_peaks(data): 
  """Return the indexes of the peaks of a signal"""
  return signal.find_peaks(data)[0]

def svgolay_filter(data):
  """Applies a Savitsky-Golay filter to the input signal"""
  return signal.savgol_filter(data, 101, 5)

def isNoise(new_peaks, peak, tau = 40):
  """Determines if a peak already exists within +-tau in new_peaks"""
  for p in new_peaks:
      maxr = p + tau
      minr = p - tau
      if minr <= peak <= maxr:
          return True
  return False

def pad_zeros(data, maxlen = 200, pad = int(0)):
  """Pads input data to maxlen

  maxlen defaults to 200
  pad defaults to 0
  Makes a copy of the input data and returns the copy
  """
  new_data = data.copy()
  num_pad = maxlen - len(data)
  for _ in range(num_pad):
      new_data = np.append(new_data, pad)
  return new_data

def normaliseHeartbeat(heartbeat):
  """Normalise and pad heartbeat samples"""
  y_data = pad_zeros(norm(heartbeat))
  return y_data

def getHeartbeatFromSamples(samples):
  """Returns all heartbeats from a list of samples"""
  heartbeats_ret = []
  for sample in samples:
    heartbeats = getHeartbeats(sample[0]) # <- unwrapping sample
    for heartbeat in heartbeats:
      heartbeats_ret.append(heartbeat)
  return np.asarray(heartbeats_ret)

def getHeartbeats(data, maxlen=200):
  """Returns all heartbeats from a single sample"""
  # Apply savgol filter
  new_data = signal.savgol_filter(data, 51, 3)
  new_data = signal.savgol_filter(new_data, 51, 3)
  new_data = signal.savgol_filter(new_data, 51, 3)

  peaks, _ = signal.find_peaks(new_data)
  indices = np.argsort(new_data[peaks])
  sorted_peaks = peaks[indices]

  new_peaks = np.array([], dtype=np.int)
  for i, peak in enumerate(sorted_peaks):
      if peak == sorted_peaks[0]: 
          new_peaks = np.append(new_peaks, peak)
          continue
      
      if isNoise(new_peaks, peak):
          continue
      else:
          new_peaks = np.append(new_peaks, peak)
  new_peaks = np.sort(new_peaks)

  heartbeats = []
  for i, peak in enumerate(new_peaks):
        if i == 0: continue
        if peak > peaks[i-1]:
            mu = peak - peaks[i-1]
            minr = int(peak - 0.5 * mu)
            maxr = int(peak + 1.5 * mu)
            heartbeat = data[minr:maxr]
            if len(heartbeat) < maxlen:
                heartbeats.append(normaliseHeartbeat(heartbeat))
        else:
            continue
  return heartbeats

def saveHeartbeats(heartbeats, filepath):
  """Save heartbeats to filepath"""
  np.savetxt(filepath, heartbeats, delimiter=',')