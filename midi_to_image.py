import music21
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


def get_tempo(midi):
    for instrument_part in instrument.partitionByInstrument(midi):
        instrument_notes = instrument_part.recurse()
        for n in instrument_notes:
            if isinstance(n, tempo.MetronomeMark):
                # print("bpm",n.getQuarterBPM())
                return n.getQuarterBPM()
    return 120

def get_time_sig(midi):
    for instrument_part in instrument.partitionByInstrument(midi):
        instrument_notes = instrument_part.recurse()
        #print("timesig:",instrument_part)
        for n in instrument_notes:
            #print(n)
            if isinstance(n, meter.TimeSignature):
                #print(n.ratioString)
                return n.ratioString
    return [4,4]

def create_image(inst, score, image_data, dest_path, count=0, verbose=False):
    scale = 4
    image_res = image_data[0]
    image_height = image_data[1]
    image_length = image_data[2]


    if verbose:
        print("Drawing:", inst)

    pitches = score["pitch"]
    amplitudes = score["amps"]
    durations = score["dur"]
    starts = score["start"]

    if verbose:
        print("p", pitches)
        print("a", amplitudes)
        print("d", durations)
        print("s", sorted(starts, reverse=False))
        # print("end",starts[-1])
        # print("dur",durations[-1])

    pixels = np.zeros((image_height, int(image_length)))

    # print(starts[100:110])

    for i in range(len(pitches)):
        # converting to an int here may prove a problem on fractions. Will have to figure that out later
        start = int(starts[i] * image_res * scale)
        dur = int(durations[i] * image_res * scale)
        pitch = int(pitches[i])

        new_bar_count = 0
        for j in range(start, start + dur):
            try:
                if image_res > 1:
                    beg = (pitch * image_res) - int(image_res / 2)
                    end = (pitch * image_res) + int(image_res / 2) + 1
                    pixels[beg:end, j] = amplitudes[i] * 255

                else:
                    pixels[pitch, j] = amplitudes[i] * 255

            except IndexError:
                while True:
                    try:
                        new_bar = np.zeros((image_height, int(image_length)))
                        pixels = np.append(pixels, new_bar, axis=1)
                        if image_res > 1:
                            beg = (pitch * image_res) - int(image_res / 2)
                            end = (pitch * image_res) + int(image_res / 2) + 1
                            pixels[beg:end, j] = amplitudes[i] * 255
                        else:
                            pixels[pitch, j] = amplitudes[i] * 255
                        new_bar_count = 0
                        break
                    except:
                        new_bar = np.zeros((image_height, int(image_length)))
                        pixels = np.append(pixels, new_bar, axis=1)
                        new_bar_count += 1

    # check if the destination directory exists, if not then make it
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    # creates the midi image at the destination
    status = cv2.imwrite(os.path.join(dest_path, f"{inst}{count}.png"), pixels)
    if verbose:
        print("Written:", inst, "image to",dest_path)
        print()
    return status

def midi_to_image(path, image_res=4, upper=127, lower=8, verbose=False, dest_path=None, specific_inst="",count=0, silence_warning=True):
    #print("___MIDI TO IMAGE___")
    if dest_path is None:
        dest_path = path
    # The following declares the current midi and establishes the tempo and time sig
    # print("Getting:",path)

    # overwrites a warning produced by some midi files about empty chords being treated as grace
    if silence_warning:
        def noop(input):
            pass
        music21.midi.translate.environLocal.warn = noop
    try:
        midi = converter.parse(path)
    except:
        return False
    if instrument.partitionByInstrument(midi) is None:
        return False
    tempo = get_tempo(midi)
    timesig = get_time_sig(midi)
    scale = 4

    # Calculate bar length for the image size
    bar_length = 60/tempo * int(timesig[0])

    if verbose:
        print("Processing midi_____")
        print(f"Midi tempo:{tempo} timesig:{timesig} bar_length:{bar_length}")

    # we multiply the bar length by 4 and the image resolution in order to scale it up
    image_length = bar_length*image_res * scale
    image_height = (upper - lower) * image_res

    # Retrieval of music scores for each instrument
    data = {}
    try:
        i = 0
        for instrument_part in instrument.partitionByInstrument(midi):
            # If a specific instrument has been stated then only an image of that is created
            if specific_inst != "" and specific_inst.lower() not in instrument_part.partName.lower():
                # print(instrument_part.partName.lower())
                # print("continuing")
                continue
            # print(specific_inst)
            # print(instrument_part.partName.lower())
            # print("match")
            # print()

            if verbose:
                print("ip",instrument_part)

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
                    if verbose:
                        print("pn", instrument_part.partName)
            else:
                if verbose:
                    print(instrument_part,"failed")
    except:
        # print("Exception")
        instrument_notes = midi.flat.notes
        data["instrument_0"] = get_note_details(instrument_notes)

    # if verbose:
    #     print("IR:",image_res)
    #     print("IL:",image_length)
    #     print("IH:",image_height)
    #     print("BL:",bar_length)

    # Writing to image section
    status = False
    for inst, score in data.items():
        # print(inst.lower())
        # print("match",specific_inst.lower() in inst.lower())
        #print(inst)
        image_data = (image_res, image_height, image_length)
        status = create_image(inst, score, image_data, dest_path, count=count,
                              verbose=verbose)  # ,score,verbose,image_res,dest_path,count=0
        count += 1
        ## This was to make sure that only the right instrument is recorded but the check was moved earlier in the function
        # if specific_inst.lower() in inst.lower():
        #     inst=specific_inst
        #
        # # If a specific instrument has been stated then only an image of that is created
        # if specific_inst != "" and specific_inst != inst:
        #     continue
        # else:

    return status


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
        #print("Stream:",part)
        print("Name:",part.partName)
        #print("RecursiveIterator:",part.recurse())
        #print(f"Getting elements of: {part.partName}")
        notes = get_note_details(part.recurse())
        i+=1
        #part.show()


midipath = r"TrainingData/Music(old)/AC_DC/Back_In_Black.1.mid"

# find_music_qualities(midipath)
#midi_to_image(midipath, dest_path="ACDCTest", verbose=True)
