from music21 import converter, note, chord, instrument, tempo

midipath = r"C:\Users\Connor\PycharmProjects\MusicGeneration\TrainingData\Music(old)\Nas\If_I_Ruled_the_World.mid"
midi = converter.parse(midipath)
instruments = instrument.partitionByInstrument(midi)
for inst in instruments:
    inst_notes = inst.recurse()
    print("pr:",inst_notes.partName)
    #print("in:",inst_notes.instrumentName)
    for n in inst_notes:
        if isinstance(n, instrument.Instrument):
            print("is a",n.instrumentName)
        if isinstance(n, tempo.MetronomeMark):
            print(n.getQuarterBPM())
        if isinstance(n,note.Note):
            pass
            #print(n.volume.velocityScalar)


x = None

if x is not None:
    print("boop")