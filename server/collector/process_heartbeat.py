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

def compute_abs_integral(heart_sets):
    ivals = []
    lengths = []
    for h_set in heart_sets:
        integral = 0
        i = 0
        for val in h_set:
            integral += abs(val)
            i += 1
        ivals.append(integral)
        lengths.append(i)
    return [ivals, lengths]
