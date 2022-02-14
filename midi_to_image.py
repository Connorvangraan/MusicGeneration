import numpy as np
from music21 import *
from imageio import imwrite
import cv2
import os


def get_note(note):
    return int(note.pitch.ps)

def get_duration(element):
    return element.duration.quarterLength

def get_note_details(elements_to_parse,verbose=False):
    durations = []
    notes = []
    start = []
    amplitudes = []

    # the constituent elements of the score
    # We need:
    # - Notes
    # - chords
    for element in elements_to_parse:
        if verbose:
            print(element)
        if isinstance(element, note.Note):
            if not element.isRest:
                # offset is the position of the note in the song (offset from beginning)
                start.append(element.offset)
                # the note is identified using ps, which is found by combining the note name, octave, and accidental (sharp # or flat -)
                # this note value is recorded as a number
                notes.append(int(element.pitch.ps))
                # duration is measured in quarter notes and is given as a float. 0.5 quarter notes are eight notes
                durations.append(element.duration.quarterLength)
                # amplitude is recorded using velocityscalar, a value between 0 and 1 which scales to a value between 0 and 127 when used in the midi file
                amplitudes.append(element.volume.velocityScalar)

        # basically the same as with note but we get the notes that constitute the chord instead
        if isinstance(element, chord.Chord):
            if not element.isRest:
                for chord_note in element.notes:
                    start.append(element.offset)
                    notes.append(int(chord_note.pitch.ps))
                    durations.append(element.duration.quarterLength)
                    amplitudes.append(element.volume.velocityScalar)

    return {"pitch": notes, "amps" : amplitudes, "start": start, "dur": durations}

def midi_to_image3(path):
    resolution = 1
    lowerBoundNote = 21
    upperBoundNote = 127

    reps = float("inf")
    midi = converter.parse(midipath)
    data = {}

    # This whole try and except section involves saving each instrument into a dictionary. Each instrument is given a key "instrument_i" wherein i is count
    # the value of the dictionary are the notes of that instrument
    try:
        i = 0
        for instrument_part in instrument.partitionByInstrument(midi):
            instrument_notes = instrument_part.recurse()
            note_data = get_note_details(instrument_notes)
            print(note_data)

            if len(note_data["start"]) > 0:
                if instrument_part.partName is None:
                    if instrument_part.instrumentName is not None:
                        data[instrument_part.instrumentName] = note_data
                        print(instrument_part.instrumentName)
                    else:
                        data[f"instrument_{i}"] = note_data
                        i+=1
                else:
                    # saves the notes of that instrument to a dictionary value, the key of which is the name of the instrument
                    data[instrument_part.partName] = note_data
                    print(instrument_part.partName)
    except:
        instrument_notes = midi.flat.notes
        data["instrument_0"] = get_note_details(instrument_notes)


    for inst, score in data.items():
        pitches = score["pitch"]
        amplitudes = score["amps"]
        durations = score["dur"]
        starts = score["start"]

        bar_length=100
        i = 0
        while i < reps:
            # pixels here is a matrix that will represent our midi track. Firstly set to 0 (black pixels)
            pixels = np.zeros((upperBoundNote-lowerBoundNote, bar_length))

            for pitch ,amp, dur, start in zip(pitches, amplitudes, durations, starts):
                dur = int(dur/resolution)
                start = int(start/resolution)

                if not start > i * (bar_length+1) or not dur+start < i*bar_length:
                    for j in range(start,start+dur):
                        if j- i*bar_length >= 0 and j - i*bar_length < bar_length:
                            print(pitch)
                            pixels[pitch-lowerBoundNote, j - i*bar_length] = 255 * amp
                            #print(pixels)

            if not np.all((pixels == 0)): #if matrix contains no noteS (only 0) don't save it
                imwrite(midipath.split("/")[-1].replace(".mid",f"_{inst}_{i}.png"),pixels.astype(np.uint8))
                i+=1
            else:
                break

def midi_to_image4(path,upper=127,lower=8):
    # The following declares the current midi and establishes the tempo and time sig
    midi = converter.parse(path)
    tempo = get_tempo(midi)
    timesig = get_time_sig(midi)
    image_res = 4
    print(f"Midi tempo:{tempo} timesig:{timesig}")

    # Calculate bar length for the image size
    bar_length = 60/tempo * int(timesig[0])
    print(bar_length)
    image_length = bar_length*4

    data = {}
    try:
        i = 0
        for instrument_part in instrument.partitionByInstrument(midi):
            instrument_notes = instrument_part.recurse()
            note_data = get_note_details(instrument_notes)
            #print(note_data)

            if len(note_data["start"]) > 0:
                if instrument_part.partName is None:
                    if instrument_part.instrumentName is not None:
                        data[instrument_part.instrumentName] = note_data
                        print(instrument_part.instrumentName)
                    else:
                        data[f"instrument_{i}"] = note_data
                        i+=1
                else:
                    # saves the notes of that instrument to a dictionary value, the key of which is the name of the instrument
                    data[instrument_part.partName] = note_data
                    print(instrument_part.partName)
    except:
        instrument_notes = midi.flat.notes
        data["instrument_0"] = get_note_details(instrument_notes)

    for inst, score in data.items():
        pitches = score["pitch"]
        amplitudes = score["amps"]
        durations = score["dur"]
        starts = score["start"]
        # print(pitches)
        # print(len(pitches))
        # print(len(amplitudes))
        print(len(durations))
        print(durations)
        print(starts)
        print(image_length)

        # holds our sets of pixels
        images = []

        # The size of our image is based on the length of 4 bars and the range of notes included
        # We first make an array of 0s which represent black pixels
        pixels = np.zeros(( upper - lower, int(image_length)*image_res))
        print("f",pixels[0][:])
        pixels[0][:]=1
        print(pixels[0][:])
        print(len(pixels[:][0]))
        print(pixels)
        print("notes to write:",len(pitches))
        i = 0
        # Currently does one bar without duration
        while len(pitches)>0:
            pitch = pitches.pop(0)
            dur = durations.pop(0)*image_res
            i= int(starts.pop(0))*image_res
            # print("i",i)
            # print("dur",dur)
            # print("pitch",pitch)
            images.append(pixels) #remove

            if i < image_length*image_res:
                # print(pixels)
                # print(pixels[:,0])
                # print(pixels[0])
                #print("beep")

                # print("dur",int(dur))
                pixels[pitch][:]=255#amplitudes.pop(0)-
            else:
                #print("boop")
                images.append(pixels)
                pixels = np.zeros((upper - lower,int(image_length)))
                i=0
                #print(pixels)
                pixels[pitch][:] = 255#amplitudes.pop(0)*255

        break
    print("im",len(images))
    print("image1 \n",images[0])

    print(images[0].shape)
    print(images[0].dtype)
    print(images[0][0])
    imwrite("testimage.png", images[0].astype(np.uint8))
    # pyplot.imshow(images[0])
    # pyplot.show()



def get_tempo(midi):
    for instrument_part in instrument.partitionByInstrument(midi):
        instrument_notes = instrument_part.recurse()
        for n in instrument_notes:
            if isinstance(n, tempo.MetronomeMark):
                print("bpm",n.getQuarterBPM())
                return n.getQuarterBPM()

def get_time_sig(midi):
    for instrument_part in instrument.partitionByInstrument(midi):
        instrument_notes = instrument_part.recurse()
        for n in instrument_notes:
            if isinstance(n, meter.TimeSignature):
                return n.ratioString


def midi_to_image(path,upper=127,lower=8,verbose=True):

    # The following declares the current midi and establishes the tempo and time sig
    print(path)
    #path = r"C:\Users\Connor\PycharmProjects\MusicGeneration\TrainingData\Music(old)\AC_DC\Back_In_Black.1.mid"
    midi = converter.parse(path)
    tempo = get_tempo(midi)
    timesig = get_time_sig(midi)
    image_res = 4


    # Calculate bar length for the image size
    bar_length = 60/tempo * int(timesig[0])

    print(f"Midi tempo:{tempo} timesig:{timesig} bar_length:{bar_length}")
    print()
    image_length = bar_length*image_res
    image_height = (upper - lower) * image_res

    data = {}
    try:
        i = 0
        for instrument_part in instrument.partitionByInstrument(midi):
            instrument_notes = instrument_part.recurse()
            note_data = get_note_details(instrument_notes)
            #print(note_data)

            if len(note_data["start"]) > 0:
                if instrument_part.partName is None:
                    if instrument_part.instrumentName is not None:
                        data[instrument_part.instrumentName] = note_data
                        # print(instrument_part.instrumentName)
                    else:
                        data[f"instrument_{i}"] = note_data
                        i+=1
                else:
                    # saves the notes of that instrument to a dictionary value, the key of which is the name of the instrument
                    data[instrument_part.partName] = note_data
                    #print(instrument_part.partName)
    except:
        instrument_notes = midi.flat.notes
        data["instrument_0"] = get_note_details(instrument_notes)

    #print("im len", image_length)

    x = 0

    count=0
    for inst, score in data.items():

        if verbose:
            print("Drawing:",inst)
        pitches = score["pitch"]
        amplitudes = score["amps"]
        durations = score["dur"]
        starts = score["start"]

        print("p",pitches)
        print("a",amplitudes)
        print("d",durations)
        print("s",sorted(starts,reverse=False))
        # print("end",starts[-1])
        # print("dur",durations[-1])

        pixels = np.zeros((image_height, int(image_length)))

        #print(starts[100:110])


        for i in range(len(pitches)):
            # print("i",i)
            # print(starts[i])
            # print(durations[i])

            # converting to an int here may prove a problem on fractions. Will have to figure that out later

            if x == 0:
                print(starts[i]*image_res)
                x+=1
            start = int(starts[i]*image_res)
            dur = int(durations[i]*image_res)
            pitch = int(pitches[i])

            # print("start",start)
            # print("dur",dur)
            #print("sts:",starts[100:105])

            new_bar_count=0
            for j in range(start,start+dur):
                #print(j)
                try:
                    pixels[pitch-int(image_res/2):pitch+int(image_res/2),j] = amplitudes[i] *255
                except IndexError:
                    while True:
                        try:
                            new_bar = np.zeros((image_height, int(image_length)))
                            pixels = np.append(pixels,new_bar,axis=1)
                            pixels[pitch-int(image_res/2):pitch+int(image_res/2),j] = amplitudes[i] *255
                            new_bar_count=0
                            break
                        except:
                            new_bar = np.zeros((image_height, int(image_length)))
                            pixels = np.append(pixels, new_bar, axis=1)
                            new_bar_count+=1
                            # if new_bar_count>3:
                            #     print("HERE")
                if x <3:
                    print(pitch)
                    print(pixels[:].shape)
                    print(pixels[:,j].shape)
                    x+=1

        #print("p:",pixels)
        path = r'C:\Users\Connor\PycharmProjects\MusicGeneration\ACDCTest'
        cv2.imwrite(os.path.join(path , f"{inst}{count}.png"), pixels)
        count+=1
        if inst == "Electric Guitar":
            print("broke")
            break


def find_music_qualities(midipath):
    """
    parse returns a music score based on the midi data given, that can then be analysed
    :return:
    """

    # score contains
    score = converter.parse(midipath)
    print(score)
    print(len(score.pitches), "notes in the song")
    print(len(score.parts), "instruments in the song")

    # This breaks down the track into instrumental parts
    i = 0
    for part in score.parts:
        print("Stream:",part)
        print("Name:",part.partName)
        print("RecursiveIterator:",part.recurse())
        print(f"Getting elements of: {part.partName}")
        notes = get_note_details(part.recurse())
        i+=1
        #part.show()


# midipath = r"TrainingData/Music(old)/AC_DC/Back_In_Black.1.mid"

#find_music_qualities(midipath)
#midi_to_image(midipath)
