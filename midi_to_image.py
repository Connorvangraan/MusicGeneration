
from music21 import converter, note, chord


midipath = r"C:\Users\Connor\PycharmProjects\MusicGeneration\TrainingData\Music(old)\Nas\If_I_Ruled_the_World.mid"
# lowest_note =
# highest_note =
# bar_len =

def get_note(note):
    return int(note.pitch.ps)

def get_duration(element):
    return element.duration.quarterLength

def get_notes(elements_to_parse,verbose=False):
    durations = []
    notes = []
    start = []

    # the constituent elements of the score
    # We need:
    # - Notes
    # - chords
    for element in elements_to_parse:
        if verbose:
            print(element)
        if isinstance(element, note.Note):
            print(element)


    """
    for element in notes_to_parse:
        if isinstance(element, note.Note):
            if element.isRest:
                print("beep")
                continue

            start.append(element.offset)
            notes.append(get_note(element))
            durations.append(get_duration(element))

        elif isinstance(element, chord.Chord):
            if element.isRest:
                print("boop")
                continue
            for chord_note in element.notes:
                start.append(element.offset)
                notes.append(get_note(chord_note))
                durations.append(get_duration(element))
    """
    return {"start": start, "pitch": notes, "dur": durations}




def find_music_qualities():
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
        notes = get_notes(part.recurse(),i==0)
        i+=1
        #part.show()




find_music_qualities()