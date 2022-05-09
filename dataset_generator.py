import midi_to_image
import re
import os
from zipfile import ZipFile
from pathlib import Path

def remove_folder(path):
    """
    Deletes the folder at path
    :param path: string path of directory to delete
    :return:
    """
    folders = []
    for subdir, dirs, files in os.walk(path):
        folders.extend(dirs)
    for i in range(len(folders),0,-1):
        folder_path = path + "/" + "/".join([folders[j] for j in range(i)])
        os.rmdir(folder_path)

def create_drum_images(path, dp):
    # for subdir, dirs, files in os.walk(path):
    #     for file in files:
    #         print(os.path.join(subdir, file))

    midis = []
    failed = []
    count = 0
    for subdir, dirs, files in os.walk(path):
        for file in files:
            os.path.join(subdir, file)
            #print(subdir,file)
            m1 = midi_to_image.midi_to_image(file,dest_path=dp,image_res=2,specific_inst="Drum",count=count)
            m2 = midi_to_image.midi_to_image(file, dest_path=dp,image_res=2, specific_inst="Drums",count=count)
            m3 = midi_to_image.midi_to_image(file, dest_path=dp,image_res=2, specific_inst="Percussion",count=count)
            if m1:
                count+=1
            if m2:
                count+=1
            if m3:
                count+=1
            if not (m1 and m2 and m3):
                failed.append(subdir+"/"+file)

            midis.append(file)
            # count+=1
        if count%10==0:
            print("Progress:",count)
    print("Finished count:",count)

    file = open("drums_processed.txt","w")
    file.write(",".join(midis))
    file.close()

    file = open("midis_failed.txt","w")
    file.write(",".join(failed))
    file.close()

def create_drum_images_zipped(path, dest):
    # Create a ZipFile Object and load sample.zip in it
    count = 0
    total_count = 0
    with ZipFile(path, 'r') as zipObj:
        # Get list of files names in zip
        listOfiles = zipObj.namelist()

        # Iterate over the list of file names in given list & print them
        for elem in listOfiles:
            if elem.endswith(".mid"):
                total_count+=1
                zp = zipObj.extract(elem, dest)
                name = zp.split("\\")[-1]
                Path(zp).rename(dest+"/" + name)
                remove_folder(dest)
                m1 = midi_to_image.midi_to_image("DrumTracksBig/"+name, dest_path=dest, image_res=2, silence_warning=True, count=count)
                if m1:
                    count+=1
                os.remove("DrumTracksBig/"+name)
                if total_count%100 == 0:
                    print(total_count,"encountered")

    print(count,"files processed out of",total_count)



def create_images(path, dest,instruments=[]):
    midis = []
    failed = []
    folder_count = 0
    folder_total = len(os.listdir(path))

    print(len(os.listdir(dest)))
    index = 0
    for file in os.listdir(dest):
        n = int(re.findall("[0-9]+", file)[0])
        if n > index:
            index = n
    count=index+1
    print(count)

    for subdir, dirs, files in os.walk(path):
        dirs.reverse()

        if len(subdir.split("\\")) == 3:
            folder_count+=1
            print(f"{folder_count}/{folder_total} folders processed")

        for file in files:
            os.path.join(subdir, file)
            # print(subdir,file)
            #midi_to_image.find_music_qualities(subdir + "/" + file)
            for inst in instruments:
                #print(inst)
                m = midi_to_image.midi_to_image(subdir + "/" + file, dest_path=dest, image_res=2, specific_inst=inst, count=count)
                if m:
                    count += 1
                else:
                    #print("Midi did not work")
                    failed.append(subdir + "/" + file)
            break
            midis.append(file)
            # count+=1
        if count+1 % 10 == 0:
            print("Progress:", count)
    print("Finished count:", count)

    file = open(f"{instruments[0]}_processed.txt", "w")
    file.write(",".join(midis))
    file.close()

    file = open(f"{instruments[0]}_midis_failed.txt", "w")
    file.write(",".join(failed))
    file.close()


def create_image_dataset(path, dest, zipname, instruments):
    create_images(path, dest, instruments)
    dest += "/"+zipname
    print()
    count = 0
    total_count = 0
    with ZipFile(path, 'r') as zipObj:
        # Get list of files names in zip
        listOfiles = zipObj.namelist()

        # Iterate over the list of file names in given list & print them
        for elem in listOfiles:
            if elem.endswith(".mid"):
                total_count += 1
                zp = zipObj.extract(elem, dest)
                name = zp.split("\\")[-1]
                Path(zp).rename(dest + "/" + name)
                remove_folder(dest)
                m1 = midi_to_image.midi_to_image(dest + name, dest_path=dest, image_res=2,
                                                 silence_warning=True, count=count)
                if m1:
                    count += 1
                os.remove(dest + name)
                if total_count % 100 == 0:
                    print(total_count, "encountered")


def create_image_dataset(path, dest, zipname, instruments):
    print(f"__Making {zipname}__")
    create_images(path, dest, instruments)
    zipObj = ZipFile("TrainingData/"+zipname, 'w')
    # Add multiple files to the zip
    for image in os.listdir(dest):
        zipObj.write(dest+"/"+image)
    # close the Zip File
    zipObj.close()

#path = "TrainingData/Music(old)"
# dest = "DrumTracksBig"
# path = 'TrainingData/800000_Drum_Percussion_MIDI_Archive[6_19_15].zip'
# create_drum_images_zipped(path, dest)

def generate_dataset(t):
    path = r"D:\MusicGenTrainingData\lmd_matched"
    if t == "bass":
        dest = "BassTracks"
        instruments = ["bass"]
        create_image_dataset(path, dest, "basstracks.zip", instruments)
        print("Images generated:",len(os.listdir(dest)))


    if t == "guitar":
        path = r"D:\MusicGenTrainingData\lmd_matched"
        instruments = ["guitar","strings"]
        create_image_dataset(path, dest, "guitartracks.zip", instruments)
        print("Images generated:", len(os.listdir(dest)))


    if t == "synth":
        dest = "SynthTracks"
        instruments = ["synth","keyboard", "piano"]
        create_image_dataset(path, dest, "synthtracks.zip", instruments)
        print("Images generated:", len(os.listdir(dest)))

generate_dataset(input("Dataset type to generate: "))