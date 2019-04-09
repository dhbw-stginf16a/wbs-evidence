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
# n = neutral
# s = sadness
# f = fear
# h = happiness
# d = disgust
# -----------------------------------------

# Package Definition
import csv
import operator
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
        @file: path of the csv file that should be read

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
    """
    Maps all the values to 'small', 'medium' or 'large' by getting the range of the column and dividing it up
    into three equally sized number ranges.

    Parameters:
        @frames: list of all frames
    Return:
        list of all frames containing the mapped values, rather than numbers
    """
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
    """
    Determines the range of a given column in a list of frames

    Parameters:
        @frames: list of all frames
        @column_name: the name of the column
    Return:
        Object containt the min-value, max-value and the size of each of the three chunks (step_size)
    """
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


def calc_m(frame):
    """
    This function takes the information that is given on a frame (values for the features) and based on this calculates
    the "mass"(Basismaß) of the emotions

    Parameters:
        @frame: list of all frames
    Return:
        A dictionary containing all the mass-values
    """
    m_vals = {
        'sec': frame['sec'],
    }
    m_vals['masse'] = []
    # iterating over the features
    for key in frame:
        # check that the key is not the number of seconds since this is just our frame id and does not help with
        # determining the Basismass
        if key != "sec":
            # creating a model for a single Basismass
            specific_m = {
                'emotions': 0.8,
                'O': 0.2
            }
            # iterating over the emotions
            emotion_list = ""
            for emotion in emotions:
                # determining whether the emotions have the value for a feature assigned,
                # that is represented in the frame
                if frame[key] in emotions[emotion][key]:
                    emotion_list = emotion_list + emotion
            # add the dict for the specific Basismas to the array of Basismasse
            specific_m[emotion_list] = specific_m.pop('emotions')
            m_vals['masse'].append(specific_m)
    return m_vals


def ds_combination(m1, m2):
    """
    This function takes two masses (m1 and m2) and accumulates them based on the Dempster-Shafer-Theory#

    Parameters:
        @m1: power set of mass 1
        @m2: power set of mass 2
    Return:
        A dictionary containing the accumulated masses of m1 and m2
    """
    result = {}
    # Combination process
    for i in m1.keys():
        # set error to zero
        k = 0
        for j in m2.keys():
            intersect = ''.join(set(str(i)).intersection(set(str(j))))
            # check for intersection
            if not set(str(i)).isdisjoint(set(str(j))):
                # if an intersection exists (meaning that there ist no conflict) we can simply multiply the Basismasse
                if intersect in result:
                    result[intersect] += m1[i] * m2[j]
                else:
                    result[intersect] = m1[i] * m2[j]
            # if there ist a conflict we need to check whether it is a 'real' conflict or a conflict with O (omega)
            elif i == 'O' or j == 'O':
                # if i is omega then the multiplied values are the new value for j
                if i == 'O' and j != "O":
                    if j in result:
                        result[j] += m1[i] * m2[j]
                    else:
                        result[j] = m1[i] * m2[j]
                # if j is omega then the multiplied values are the new value for i
                elif i != 'O' and j == 'O':
                    if i in result:
                        result[i] += m1[i] * m2[j]
                    else:
                        result[i] = m1[i] * m2[j]
            # the only possibility left is a 'real' conflict where none of the potenzmengen is omega
            else:
                # add the product of the basismasse to the conflict
                k += m1[i] * m2[j]
        if k > 0:
            if k != 1:
                for x in result:
                    result[x] /= (1-k)
            else:
                print("Error: K = 1")
    return result


def iterate_ds(dict_masses):
    """
    This function takes an array of mass values (calculated by calc_m) and accumulates all of them

    Parameters:
        @dict_masses: dictionary containing all masses
    Return:
        Last calculated mass, final result
    """
    # get length of array
    l = len(dict_masses['masse'])
    # iterate over array with index
    for x in range(len((dict_masses['masse']))):
        # check that there is still a 'next element'
        if x < l-1:
            # accumulate this and the next basismass
            m1 = ds_combination(dict_masses['masse'][x], dict_masses['masse'][x + 1])
            # update the next basismass with the new value,
            # so that the next iterations accumulates the next basismas with the result
            dict_masses['masse'][x+1].update(m1)
        else:
            return dict_masses['masse'][x]


def calc_plaus(mass):
    """
    Calculates the plausibility

    Parameters:
        @mass: list of mass values
    Return:
        dictionary containing the calculated plausibility of an emotion
    """
    plaus = {}
    for emo in emotions:
        plaus.update({emo: 0})
        for val in mass:
            if emo in val:
                plaus[emo] += mass[val]
    return plaus


def check_plaus(plausibility):
    """
    Gets the highest plausibility

    Parameters:
        @plausibility: dictionary containing the plausibility
    Return:
        Emotion with the highest plausibility
    """
    return max(plausibility.items(), key=operator.itemgetter(1))[0]


def map_plausibility(frames):
    """
    maps an emotion to each frame

    Parameters:
        frames: set of emotion frames, where the facial expression values are mapped to
        'small', 'medium' or 'large' values
    Return:
        dictionary containing the determined emotion for each frame
    """
    result = {}
    for frame in frames:
        initial_m = calc_m(frame)
        final_m = iterate_ds(initial_m)
        plaus = calc_plaus(final_m)
        emotion = check_plaus(plaus)
        # Use second as key and set the calculated plausibility
        result[frame['sec']] = emotion
    return result


# Main Entry for the application
emotion_frames = import_csv("data/emo_muster_1_1.csv")
emotion_frames = evaluate_frames(emotion_frames)
plausibility = map_plausibility(emotion_frames)

print(json.dumps(plausibility, indent=4))



