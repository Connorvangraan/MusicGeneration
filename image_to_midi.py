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

def image2midi(image_path):
    with Image.open(image_path) as image:
        im_arr = np.frombuffer(image.tobytes(), dtype=np.uint8)
        try:
            im_arr = im_arr.reshape((image.size[1], image.size[0]))
        except:
            im_arr = im_arr.reshape((image.size[1], image.size[0],3))
            im_arr = np.dot(im_arr, [0.33, 0.33, 0.33])

    """ convert the output from the prediction to notes and create a midi file
        from the notes """
    offset = 0
    output_notes = []

    # create note and chord objects based on the values generated by the model

    prev_notes = updateNotes(im_arr.T[0,:],{})
    for column in im_arr.T[1:,:]:
        notes = column2notes(column)
        # pattern is a chord
        notes_in_chord = notes
        old_notes = prev_notes.keys()
        for old_note in old_notes:
            if not old_note in notes_in_chord:
                new_note = note.Note(old_note,quarterLength=prev_notes[old_note])
                new_note.storedInstrument = instrument.Piano()
                if offset - prev_notes[old_note] >= 0:
                    new_note.offset = offset - prev_notes[old_note]
                    output_notes.append(new_note)
                elif offset == 0:
                    new_note.offset = offset
                    output_notes.append(new_note)
                else:
                    print(offset,prev_notes[old_note],old_note)

        prev_notes = updateNotes(notes_in_chord,prev_notes)

        # increase offset each iteration so that notes do not stack
        offset += resolution

    for old_note in prev_notes.keys():
        new_note = note.Note(old_note,quarterLength=prev_notes[old_note])
        new_note.storedInstrument = instrument.Piano()
        new_note.offset = offset - prev_notes[old_note]

        output_notes.append(new_note)

    prev_notes = updateNotes(notes_in_chord,prev_notes)

    midi_stream = stream.Stream(output_notes)

    midi_stream.write('midi', fp=image_path.split("/")[-1].replace(".png",".mid"))


def image_to_midi(path,image_res,upper=127,lower=8):
    instrument_name = path.split("\\")[-1].replace(".png","")
    print("Scoring:",instrument_name)
    score = {}

    pitches = []
    amplitudes = []
    durations = []
    starts = []
    print()
    with Image.open(path) as image:
        pixels = np.frombuffer(image.tobytes(), dtype=np.uint8)
        pixels = pixels.reshape((image.size[1], image.size[0]))
    print(pixels.shape)
    x = 0

    for col in range(pixels.shape[1]):
        for pixel in range(len(pixels[:,col])):
            if pixels[pixel,col] > 0:
                # print(pixels[:,col])
                # print(pixels[pixel,col])
                starts.append(col/image_res)
                amplitudes.append(pixels[pixel,col]/255)
                pitches.append(pixel)
                if x == 0:
                    print("px:",pixels[:,col])
                    print("s:",col/image_res)
                    print("a:",pixels[pixel,col]/255)
                    print("d?:",pixels[pixel,col:col+10])
                    print("cur:",pixels[pixel,col])
                    print("nex:",pixels[pixel,col+1])
                    x+=1
                d=1
                finding_dur = True
                while finding_dur:
                    try:
                        if pixels[pixel, col + 1] == pixels[pixel, col]:
                            print("beep")
                            pixels[pixel, col + 1] = 0
                            d+=1
                            print("adding d",pixels[pixel, col: col+ 10])
                        else:
                            print("boop")
                            finding_dur=False
                    except:
                        finding_dur=False
                durations.append(d/image_res)

    score["pitch"] = pitches
    score["amps"] = amplitudes
    score["dur"] = durations
    score["start"] = starts
    print("p", pitches)
    print("a", amplitudes)
    print("d", durations)
    print("s", starts)
    # p [40, 45, 38, 45, 45, 45, 40, 40, 55, 52, 50, 47, 47, 57, 45, 55, 43, 40, 45]
    # a [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    # d [1.0, 0.25, 0.25, 1.0, 0.25, 0.25, 0.25, 1.0, 0.25, Fraction(1, 3), 0.25, Fraction(1, 3), Fraction(1, 3)]
    # s [4.0, 5.5, 5.75, 6.0, 7.5, 7.5, 7.75, 8.0, 10.25, 10.5, 10.75, 11.0, 11.25, 11.5, 11.5, 11.75, 11.75, 12.0]

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
    midi_stream.write('midi', fp=path.split("/")[-1].replace(".png", ".mid"))
    return score


def image_to_song(path,image_res=1):
    data = {}
    for image_path in glob.glob(path+"/*.png"):
        instrument_name = image_path.split("\\")[-1].replace(".png", "")
        if instrument_name == "Electric Guitar0":
            print(image_path)
            data[instrument_name] = image_to_midi(image_path,image_res)
            break


path = r"C:\Users\Connor\PycharmProjects\MusicGeneration\TrainingData\Music(old)\AC_DC\Back_In_Black.1.mid"
# path = r"ACDCTest/Electric Guitar0.mid"
#midi_to_image.midi_to_image(path,image_res=4)
folder_path = r"ACDCTest/"
image_to_song(folder_path,4)