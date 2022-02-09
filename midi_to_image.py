import numpy as np
from music21 import converter, note, chord, instrument
from imageio import imwrite

midipath = r"C:\Users\Connor\PycharmProjects\MusicGeneration\TrainingData\Music(old)\2_the_Core\Have_a_Nice_Day.mid"
# lowest_note =
# highest_note =
# bar_len =

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



def midi_to_image(path):
    resolution = 0.25
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
                            pixels[pitch-lowerBoundNote, j - i*bar_length] = 255 * amp

            if not np.all((pixels == 0)): #if matrix contains no noteS (only 0) don't save it
                imwrite(midipath.split("/")[-1].replace(".mid",f"_{inst}_{i}.png"),pixels.astype(np.uint8))
                i+=1
            else:
                break


def midi2image(midi_path, max_repetitions = float("inf"), resolution = 0.25, lowerBoundNote = 21, upperBoundNote = 127, bar_length = 100):
    mid = converter.parse(midi_path)

    instruments = instrument.partitionByInstrument(mid)

    data = {}

    try:
        i=0
        for instrument_i in instruments.parts:
            notes_to_parse = instrument_i.recurse()

            notes_data = get_note_details(notes_to_parse)
            if len(notes_data["start"]) == 0:
                continue

            if instrument_i.partName is None:
                data["instrument_{}".format(i)] = notes_data
                i+=1
            else:
                data[instrument_i.partName] = notes_data

    except:
        notes_to_parse = mid.flat.notes
        data["instrument_0"] = get_note_details(notes_to_parse)

    for instrument_name, values in data.items():
        # https://en.wikipedia.org/wiki/Scientific_pitch_notation#Similar_systems
        print(instrument_name)

        pitches = values["pitch"]
        durs = values["dur"]
        starts = values["start"]

        index = 0
        while index < max_repetitions:
            matrix = np.zeros((upperBoundNote-lowerBoundNote,bar_length))


            for dur, start, pitch, amp in zip(durs, starts, pitches, amp):
                dur = int(dur/resolution)
                start = int(start/resolution)

                if not start > index*(bar_length+1) or not dur+start < index*bar_length:
                    for j in range(start,start+dur):
                        if j - index*bar_length >= 0 and j - index*bar_length < bar_length:
                            matrix[pitch-lowerBoundNote,j - index*bar_length] = 255 * amp

            if matrix.any(): # If matrix contains no notes (only zeros) don't save it
                imwrite(midi_path.split("/")[-1].replace(".mid",f"_{instrument_name}_{index}.png"),matrix.astype(np.uint8))
                index += 1
            else:
                break

def find_music_qualities(midipath):
    """
    parse returns a score based on the midi data given, that can then be analysed

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


find_music_qualities(midipath)
midi_to_image(midipath)