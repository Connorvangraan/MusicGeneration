from PIL import Image
import numpy as np
import glob
from music21 import *
import midi_to_image

lowerBoundNote = 21
def column2notes(column):
    notes = []
    for i in range(len(column)):
        if column[i] > 255/2:
            notes.append(i+lowerBoundNote)
    return notes

resolution = 0.25
def updateNotes(newNotes,prevNotes):
    res = {}
    for note in newNotes:
        if note in prevNotes:
            res[note] = prevNotes[note] + resolution
        else:
            res[note] = resolution
    return res


def image_to_midi(path,image_res=4,upper=127,lower=8,verbose=False):
    scale = 4
    instrument_name = path.split("\\")[-1].replace(".png","")
    print("Scoring_____")
    print("Instrument piece:",instrument_name)

    score = {}
    pitches = []
    amplitudes = []
    durations = []
    starts = []
    with Image.open(path) as image:
        pixels = np.frombuffer(image.tobytes(), dtype=np.uint8)
        pixels = pixels.reshape((image.size[1], image.size[0]))


    x = 0
    col = 0
    while col < pixels.shape[1]:
        pixel = 0
        while pixel < len(pixels[:,col]):
            if pixels[pixel,col] > 0:
                starts.append(col/image_res/scale)
                amplitudes.append(pixels[pixel,col]/255)

                # downscales the pitch back down using the image resolution
                pitch = (pixel+image_res/2)/image_res
                pitches.append(pitch)

                # if x == 0:
                #     print("px:",pixels[:,col])
                #     print("s:",col/image_res/scale)
                #     print("a:",pixels[pixel,col]/255)
                #     print("d?:",pixels[pixel,col:col+10])
                #     print("cur:",pixels[pixel,col])
                #     print("nex:",pixels[pixel,col+1])
                #     x+=1

                d=1
                finding_dur = True
                while finding_dur:
                    try:
                        if pixels[pixel, col + 1] == pixels[pixel, col]:
                            pixels[pixel, col + 1] = 0
                            d+=1
                        else:
                            finding_dur=False
                            pixels[pixel, col: col + image_res] = 0
                    except:
                        finding_dur=False
                durations.append(d)

                # moves pixel pointer past the current note
                pixel += image_res
            pixel+=1
        col += image_res

    score["pitch"] = pitches
    score["amps"] = amplitudes
    score["dur"] = durations
    score["start"] = starts
    # print("p", pitches)
    # print("a", amplitudes)
    # print("d", durations)
    # print("s", starts)

    notes = []
    i = 0
    for pitch in pitches:
        n = note.Note(pitch,quarterLength=durations[i])
        n.storedInstrument = instrument.Piano()
        n.offset = starts[i]
        notes.append(n)
        i+=1

    midi_stream = stream.Stream(notes)
    # tem = tempo.MetronomeMark(95)
    # tem.setQuarterBPM(95)
    # midi_stream.append(tem)
    # midi_stream.append(meter.TimeSignature())
    #
    # print(midi_stream.timeSignature)
    # midi_stream.quarterLength = 95 #tempo.MetronomeMark(95)
    # print(midi_stream.quarterLength)
    print("Writing midi...")
    midi_stream.write('midi', fp=path.split("/")[-1].replace(".png", ".mid"))
    print("midi written")
    return score


def image_to_song(path,image_res=1,verbose=False):
    data = {}
    for image_path in glob.glob(path+"/*.png"):
        instrument_name = image_path.split("\\")[-1].replace(".png", "")
        print("Instrument:",instrument_name)
        data[instrument_name] = image_to_midi(image_path, image_res,verbose=verbose)


def run_test(artist="AC_DC", song="Back_In_Black.1",ir=2):
    print("_____Running Conversion Test_____")
    print(f"Converting: {song} by {artist}")
    print("Image resolution:",ir)
    filename = artist+"\\"+song+".mid"
    path = "C:\\Users\\Connor\\PycharmProjects\\MusicGeneration\\TrainingData\\Music(old)\\"+filename
    midi_to_image.midi_to_image(path,image_res=ir,verbose=True,dest_path= r'C:\Users\Connor\PycharmProjects\MusicGeneration\ACDCTest',specific_inst="Electric Guitar")
    folder_path = r"ACDCTest/"
    image_to_song(folder_path,image_res=ir,verbose=True)
    print("_____End of test_____")

