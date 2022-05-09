from PIL import Image
from music21 import *
import midi_to_image
import cv2
import random
import os
import numpy as np
import glob

lowerBoundNote = 21


def column2notes(column):
    notes = []
    for i in range(len(column)):
        if column[i] > 255 / 2:
            notes.append(i + lowerBoundNote)
    return notes


resolution = 0.25


def updateNotes(newNotes, prevNotes):
    res = {}
    for note in newNotes:
        if note in prevNotes:
            res[note] = prevNotes[note] + resolution
        else:
            res[note] = resolution
    return res


def prep_image(pixels, threshold=1):
    print(pixels.shape)
    for i in range(pixels.shape[0]):
        for j in range(pixels.shape[1]):
            if pixels[i][j] < threshold:
                pixels[i][j] = 0
    return pixels


def image_to_midi(paths, image_res=1, filename="midi", upper=127, lower=8, midi=None, verbose=False):
    if isinstance(paths, str):
        paths = [paths]
        print(paths)

    midi_stream = stream.Score()
    notes = []
    print(paths)
    for p_i, path in enumerate(paths):
        scale = 4
        instrument_name = path.split("\\")[-1].replace(".png", "")
        if verbose:
            print("Scoring_____")
            print("Instrument piece:", instrument_name)

        score = {}
        pitches = []
        amplitudes = []
        durations = []
        starts = []

        with Image.open(path) as image:
            pixels = np.frombuffer(image.tobytes(), dtype=np.uint8)
            pixels = pixels.reshape((image.size[1], image.size[0]))

        # for col in pixels:
        #     print(col)
        print(pixels.shape)
        # pixels = prep_image(pixels)
        x = 0
        col = 0
        while col < pixels.shape[1]:
            pixel = 0
            while pixel < len(pixels[:, col]):
                if pixels[pixel, col] > 0:
                    starts.append(col / image_res / scale)
                    amplitudes.append(pixels[pixel, col] / 255)

                    # downscales the pitch back down using the image resolution
                    pitch = (pixel + image_res / 2) / image_res
                    pitches.append(pitch)

                    # if x == 0:
                    #     print("px:",pixels[:,col])
                    #     print("s:",col/image_res/scale)
                    #     print("a:",pixels[pixel,col]/255)
                    #     print("d?:",pixels[pixel,col:col+10])
                    #     print("cur:",pixels[pixel,col])
                    #     print("nex:",pixels[pixel,col+1])
                    #     x+=1

                    d = 1
                    finding_dur = True
                    while finding_dur:
                        try:
                            #print("ya")
                            if pixels[pixel, col + 1] == pixels[pixel, col]:
                                #print("slg")
                                pixels[pixel, col + 1] = 0
                                d += 1
                            else:
                                #print("bee")
                                finding_dur = False
                                pixels[pixel, col: col + image_res] = 0
                        except:
                            finding_dur = False
                    durations.append(d)

                    # moves pixel pointer past the current note
                    pixel += image_res
                pixel += 1
            col += image_res

        score["pitch"] = pitches
        score["amps"] = amplitudes
        score["dur"] = durations
        score["start"] = starts
        # print("p", pitches)
        # print("a", amplitudes)
        # print("d", durations)
        # print("s", starts)

        # return notes
        i = 0

        part = stream.Part()
        print(path)
        if "piano" in path.lower() or "synth" in path.lower() or "strings" in path.lower():
            part.insert(instrument.Piano())
        if "drums" in path.lower() or "drum" in path.lower() or "percussion" in path.lower():
            part.insert(instrument.BassDrum())
        if "bass" in path.lower():
            part.insert(instrument.ElectricBass())
        if "guitar" in path.lower():
            part.insert(instrument.ElectricGuitar())

        print(pitches)
        print(durations)
        dur2 = []
        for dur in durations:
            r = random.randint(0,5)
            if r < 2:
                dur2.append(0.25)
            elif r < 4:
                dur2.append(0.5)
            else:
                dur2.append(dur)
        durations=dur2
        for pit in pitches:
            n = note.Note(int(pit))  # ,quarterLength=durations[i]) # ,channel=9
            # n.duration.type = 'quarter'
            n.duration.quarterLength = durations[i]
            part.append(n)

            n.offset = starts[i]  # /2
            notes.append(n)
            i += 1

        m = random.randint(50, 150)
        print("m",m)
        part.insert(tempo.MetronomeMark(m))
        midi_stream.insert(0, part)

    if verbose:
        print("Writing midi...")

    if not filename.endswith(".mid"):
        filename += ".mid"
    foldername = "GeneratedMusic/"
    print(foldername + filename)
    midi_stream.write('midi', fp=foldername + filename)
    if verbose:
        print("midi written")
    return score


def image_to_song(path, image_res=1, verbose=False):
    data = {}
    for image_path in glob.glob(path + "/*.png"):
        instrument_name = image_path.split("\\")[-1].replace(".png", "")
        print("Instrument:", instrument_name)
        data[instrument_name] = image_to_midi(image_path, image_res, verbose=verbose)


def run_test(artist="AC_DC", song="Back_In_Black.1", ir=2):
    print("_____Running Conversion Test_____")
    print(f"Converting: {song} by {artist}")
    print("Image resolution:", ir)
    filename = artist + "\\" + song + ".mid"
    path = "C:\\Users\\Connor\\PycharmProjects\\MusicGeneration\\TrainingData\\Music(old)\\" + filename
    midi_to_image.midi_to_image(path, image_res=ir, verbose=False,
                                dest_path=r'C:\Users\Connor\PycharmProjects\MusicGeneration\ACDCTest',
                                specific_inst="Electric Guitar")
    folder_path = r"ACDCTest/"
    # image_to_song(folder_path,image_res=ir,verbose=True)
    images = [folder_path + im for im in os.listdir("ACDCTest") if ".png" in im]
    print(images)
    image_to_midi(images, filename="BIB", verbose=True)
    print("_____End of test_____")


# run_test()


def generate_random_track(threshhold=73):
    instrument_paths = ["GeneratedImages/Bass/", "GeneratedImages/Drums/", "GeneratedImages/Guitar/",
                        "GeneratedImages/Synth/"]
    generated_paths = []
    for path in instrument_paths:
        print(path)
        filename = random.choice(os.listdir((path)))
        path += filename
        pixels = np.asarray(Image.open(path))
        pixels = np.delete(pixels, 1, 2)
        pixels = np.delete(pixels, 1, 2)
        # print(pixels.shape)
        pixels = pixels.reshape((50, 50))  # /255

        for i in range(pixels.shape[0]):
            for j in range(pixels[i].shape[0]):
                if pixels[i][j] < threshhold:
                    pixels[i][j] = 0

        # for row in pixels:
        #     print(row)
        img2 = Image.fromarray(pixels)
        # img2.show()

        shift_row = np.zeros((38, pixels.shape[1]))
        pixels = np.vstack([shift_row, pixels])

        loop = 5
        for i in range(loop):
            pixels = np.c_[pixels, pixels]

        print("p", pixels.shape)
        pathname = path.split("/")[-1]
        f = f"GeneratedMusic/Images/{pathname}"
        status = cv2.imwrite(f, pixels)
        generated_paths.append(f)

    image_to_midi(generated_paths)


def load_generated_images(paths, threshold=73):
    generated_paths = []

    for path in paths:
        print(path)
        pixels = np.asarray(Image.open(path))
        # print(pixels.shape)
        pixels = np.delete(pixels, 1, 2)
        pixels = np.delete(pixels, 1, 2)
        # print(pixels.shape)
        pixels = pixels.reshape((50, 50))  # /255

        for i in range(pixels.shape[0]):
            for j in range(pixels[i].shape[0]):
                if pixels[i][j] < threshold:
                    pixels[i][j] = 0

        # for row in pixels:
        #     print(row)
        img2 = Image.fromarray(pixels)
        # img2.show()

        r = random.randint(10,50)
        shift_row = np.zeros((r, pixels.shape[1]))
        pixels = np.vstack([shift_row, pixels])

        loop = 5
        for i in range(loop):
            pixels = np.c_[pixels, pixels]

        print("p", pixels.shape)
        pathname = path.split("/")[-1]
        f = f"GeneratedMusic/{pathname}"
        status = cv2.imwrite(f, pixels)
        generated_paths.append(f)

    image_to_midi(generated_paths)


path = ["GeneratedImages/Drums/drums0.bmp", "GeneratedImages/Bass/bass1.bmp", "GeneratedImages/Synth/piano2.bmp",
        "GeneratedImages/Guitar/guitar3.bmp"]
# load_generated_images(path)
generate_random_track()
