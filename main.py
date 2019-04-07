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
    "neutral": create_emotion_object('s', 'm', 'm', 'm', 'm', 's', 's', 's', 's', None),
    "sadness": create_emotion_object('h', ['s', 'm'], ['s', 'm'], 'm', 'm', 'm', None, ['s', 'm'], ['s', 'm'], None),
    "fear": create_emotion_object('l', 'l', 'l', 'l', 'l', 'l', None, None, None, 'l'),
    "happiness": create_emotion_object('m', 'l', 'l', 'l', 'l', 's', None, ['m', 'l'], ['m', 'l'], None),
    "disgust": create_emotion_object('s', 's', 's', 's', 's', ['s', 'm', 'l'], None, 'm', 'm', None)
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


# Main Entry for the application
result = import_csv("data/emo_muster_1_1.csv")
result = evaluate_frames(result)

print(result)


