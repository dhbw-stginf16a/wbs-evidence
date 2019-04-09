# -------------Abbreviations --------------
# features:
# fob = furrowing of brow
# lea = left eye aperture
# rea = right eye aperture
# lbd = left brow distance
# rbd = right brow distance
# hnc = horizontal nose crinkles
# vnc = vertical nose crinkles
# lcw = left cheek wrinkle
# rcw = right cheek wrinkle
# ma = mouth aperture
# ----------------------------------------
# emotions:
# n = neutral
# s = sadness
# f = fear
# h = happiness
# d = disgust
# -----------------------------------------

# Package Definition
import csv
import operator
import sys
import json

#TO-DO doku 0=small, n/a=None

def create_emotion_object(fob, lea, rea, lbd, rbd, hnc, vnc, lcw, rcw, ma):
    return {
        "fob": fob,
        "lea": lea,
        "lbd": lbd,
        "rea": rea,
        "rbd": rbd,
        "hnc": hnc,
        "vnc": vnc,
        "lcw": lcw,
        "rcw": rcw,
        "ma": ma
    }


emotions = {
    "n": create_emotion_object(['s'], ['m'], ['m'], ['m'], ['m'], ['s'], ['s'], ['s'], ['s'], [None]),
    "s": create_emotion_object(['h'], ['s', 'm'], ['s', 'm'], ['m'], ['m'], ['m'], [None], ['s', 'm'], ['s', 'm'], [None]),
    "f": create_emotion_object(['l'], ['l'], ['l'], ['l'], ['l'], ['l'], [None], [None], [None], ['l']),
    "h": create_emotion_object(['m'], ['l'], ['l'], ['l'], ['l'], ['s'], [None], ['m', 'l'], ['m', 'l'], [None]),
    "d": create_emotion_object(['s'], ['s'], ['s'], ['s'], ['s'], ['s', 'm', 'l'], [None], ['m'], ['m'], [None])
}

def import_csv(file):
    """
    Creates a list of frame objects

    Parameters:
        file: path of the csv file that should be read

    Return:
        list of frames containing the different attributes
    """
    try:
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            next(csv_file)  # skip header
            frames = []
            for row in csv_reader:
                frames.append({
                        "sec": int(row[0]),
                        "fob": int(row[5]),
                        "lea": int(row[6]),
                        "lbd": int(row[7]),
                        "rea": int(row[8]),
                        "rbd": int(row[9]),
                        "hnc": int(row[10]),
                        "vnc": int(row[11]),
                        "lcw": int(row[12]),
                        "rcw": int(row[13]),
                        "ma": int(row[14])
                    })

            return frames

    except FileNotFoundError:
        print(f"File {file} not found")
        raise


def evaluate_features(frames):
    mapped_frames = []
    for frame in frames:
        mapped_frame = frame.copy()
        for key in frame:
            if key != 'sec':
                range = value_range(frames, key)
                if frame[key] >= range['min'] and frame[key] < range['min'] + range['step_size']:
                    mapped_frame[key] = 's'
                elif frame[key] >= range['min'] + range['step_size'] and frame[key] < range['min'] + 2 * range['step_size']:
                    mapped_frame[key] = 'm'
                else:
                    mapped_frame[key] = 'l'

        mapped_frames.append(mapped_frame)

    return mapped_frames


def value_range(frames, column_name):
    # Get Range of values the map values to small, medium & large
    column = [f[column_name] for f in frames]
    min_val = min(column)
    max_val = max(column)
    range = max_val - min_val
    step_size = range / 3

    return {
        "min": min_val,
        "max": max_val,
        "step_size": step_size
    }


"""
This function takes the information that is given on a frame (values for the features) and calculates the basismasse for the emotions based on this
"""
def calc_m(frame):
    m_vals = {
        'sec': frame['sec'],
    }
    m_vals['masse'] = []
    # iterating over the features
    for key in frame:
        # check that the key is not the number of seconds since this is just our frame id and does not help with determining the Basismass
        if key != "sec":
            # creating a model for a single Basismass
            specific_m = {
                'emotions': 0.8,
                'O': 0.2
            }
            # iterating over the emotions
            emotion_list = ""
            for emotion in emotions:
                #determining whether the emotions have the value for a feature assigned, that is represented in the frame
                if frame[key] in emotions[emotion][key]:
                    emotion_list = emotion_list + emotion
            # add the dict for the specific Basismas to the array of Basismasse
            specific_m[emotion_list] = specific_m.pop('emotions')
            m_vals['masse'].append(specific_m)
    return m_vals

"""
This function takes two basismasse (m1 and m2) and accumulates them based on the Dempster-Shafer-Theory
"""
def ds_accum(m1, m2):
    # extract the frame discernment
    sets = set(m1.keys()).union(set(m2.keys()))
    result_m = {}
    # Combination process
    for i in m1.keys():
        #initialize error to zero
        k = 0
        for j in m2.keys():
            intersect = ''.join(set(str(i)).intersection(set(str(j))))
            #check for intersection
            if not set(str(i)).isdisjoint(set(str(j))):
                #if an intersection exists (meaning that there ist no conflict) we can simply multiply the Basismasse
                if intersect in result_m:
                    result_m[intersect] += m1[i] * m2[j]
                else:
                    result_m[intersect] = m1[i] * m2[j]
            #if there ist a conflict we need to check whether it is a 'real' conflict or a conflict with O (omega)
            elif i == 'O' or j == 'O':
                #if i is omega then the multiplied values are the new value for j
                if i == 'O' and j != "O":
                    if j in result_m:
                        result_m[j] += m1[i] * m2[j]
                    else:
                        result_m[j] = m1[i] * m2[j]
                #if j is omega then the multiplied values are the new value for i
                elif i != 'O' and j == 'O':
                    if i in result_m:
                        result_m[i] += m1[i] * m2[j]
                    else:
                        result_m[i] = m1[i] * m2[j]
            #the only possibility left is a 'real' conflict where none of the potenzmengen is omega
            else:
                # add the product of the basismasse to the conflict
                k += m1[i] * m2[j]
        if k > 0:
            if(k != 1):
                for x in result_m:
                    result_m[x] /= (1-k)
            else:
                print("Error: K = 1")
    return result_m


"""
This function takes an array of Basismass values (calculated by calc_m) and accumulates all of them 
"""
def iterate_ds_accum(dict_masses):
    #get length of array
    l = len(dict_masses['masse'])
    #iterate over array with index
    for x in range(len((dict_masses['masse']))):
        #check that there is still a 'next element'
        if(x < l-1):
            #accumulate this and the next basismass
            m1 = ds_accum(dict_masses['masse'][x], dict_masses['masse'][x + 1])
            #update the next basismass with the new value, so that the next iterations accumulates the next basismas with the result
            dict_masses['masse'][x+1].update(m1)
        else:
            return dict_masses['masse'][x]


def calc_plaus(mass):
    plausibility = {}
    for emo in emotions:
        plausibility.update({emo: 0})
        for val in mass:
            if emo in val:
                plausibility[emo] += mass[val]
    return plausibility


def check_max_plaus(plausibility):
    return max(plausibility.items(), key=operator.itemgetter(1))[0]


def check_frames(frames):
    result = {}
    for frame in frames:
        initial_m = calc_m(frame)
        final_m = iterate_ds_accum(initial_m)
        plausibility = calc_plaus(final_m)
        emotion = check_max_plaus(plausibility)
        result[frame['sec']] = emotion
    return result

# Main Entry for the application
frames = import_csv("data/emo_muster_1_1.csv")
frames = evaluate_features(frames)
print(json.dumps(check_frames(frames), indent=4))




