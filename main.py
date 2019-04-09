# -------------Abbreviations --------------
# features:
# fob = furrowing of brow
# lea = left eye aperture
# rea = right eye departure
# lbd = left brow distance
# rbd = right brow distance
# hnc = horizontal nose crinkles
# vnc = vertical nose crinkles
# lcw = left cheek wrinkle
# rcw = right cheek wrinkle
# ma = mouth aperture
# ----------------------------------------
# emotions:
# neu = neutral
# sad = sadness
# fea = fear
# hap = happiness
# dis = disgust
# -----------------------------------------

# Package Definition
import csv
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


def evaluate_frames(frames):
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


# Function for calculation of the Basismass for a given frame (picture)
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


def DSCombination(Dic1, Dic2):
    # extract the frame discernment
    sets = set(Dic1.keys()).union(set(Dic2.keys()))
    Result = {}
    # Combination process
    for i in Dic1.keys():
        for j in Dic2.keys():
            intersect = ''.join(set(str(i)).intersection(set(str(j))))
            #check for intersection
            if not set(str(i)).isdisjoint(set(str(j))):
                #if an intersection exists (meaning that there ist no conflict) we can simply multiply the Basismasse
                if intersect in Result:
                    Result[intersect] += Dic1[i] * Dic2[j]
                else:
                    Result[intersect] = Dic1[i] * Dic2[j]
            #if there ist a conflict we need to check whether it is a 'real' conflict or a conflict with O (omega)
            elif i == 'O' or j == 'O':
                #if i is omega then the multiplied values are the new value for j
                if i == 'O' and j != "O":
                    if j in Result:
                        Result[j] += Dic1[i] * Dic2[j]
                    else:
                        Result[j] = Dic1[i] * Dic2[j]
                #if j is omega then the multiplied values are the new value for i
                elif i != 'O' and j == 'O':
                    if i in Result:
                        Result[i] += Dic1[i] * Dic2[j]
                    else:
                        Result[i] = Dic1[i] * Dic2[j]
                #the only possibility left is a 'real' conflict where none of the potenzmengen is omega
            else:
                k = Dic1[i] * Dic2[j]
                if k != 1:
                    for x in Result:
                        Result[x] /= (1-k)
                else:
                    print("Error: K = 1")
    # normalize the results
    #f = sum(list(Result.values()))
    #print(f)
    print(Result)
    return Result


def iterate_d_s(dict_masses):
    print(dict_masses)
    l = len(dict_masses['masse'])
    for x in range(len((dict_masses['masse']))):
        if(x < l-1):
            m1 = DSCombination(dict_masses['masse'][x], dict_masses['masse'][x + 1])
            dict_masses['masse'][x+1].update(m1)
    print(dict_masses)


# Main Entry for the application
result = import_csv("data/emo_muster_1_1.csv")
result = evaluate_frames(result)
m = calc_m(result[0])
iterate_d_s(m)




