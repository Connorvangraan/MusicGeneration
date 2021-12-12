import os
import csv
import h5py
import glob
import tables

class GenreFinderOld:
    def __init__(self):
        self.missingSongs = []

        self.source = "C:/Users/Connor/PycharmProjects/MusicGeneration/"
        genrelist = open("msd_tagtraum_cd1.cls", "r", encoding="UTF-8")
        genrelist2 = open("msd_tagtraum_cd2c.cls", "r", encoding="UTF-8")
        tracklist = open("unique_tracks.txt", "r", encoding="UTF-8")


        """
        Song_genre contains a list of songs their genre
        This checks if the song_genre database exists. If it does not then it is made, and all of the songs and their genres are written in
         
        """
        if not os.path.isfile('song_genres.csv'):
            songids = open("song_genres.csv","a",encoding="UTF-8", newline='')
            writer = csv.writer(songids)
            genres = {}
            for line in genrelist.readlines():
                listed_line = line.split("\t")
                try:
                    genres[listed_line[0]] = listed_line[1].replace("\n","")
                except:
                    pass

            for line in genrelist2.readlines():
                listed_line = line.split("\t")
                try:
                    genres[listed_line[0]] = listed_line[1].replace("\n","")
                except:
                    pass

            match = 0
            no_match = 0
            for line in tracklist.readlines():
                listed_line = line.split("<SEP>")
                try:
                    writer.writerow([listed_line[3].replace("\n", ""), genres[listed_line[0]]])
                    match+=1
                except:
                    no_match+=1

            print(str(match)+" songs have been matched")
            print(str(no_match)+" songs could not be matched")
            songids.close()

        """
        Opens the song_genre database and saves all of the values to a dictionary use for look up later 
        """
        songs_genres = open("song_genres.csv","r", encoding="UTF-8")
        self.genres = {}
        sg = songs_genres.readlines()
        for song_genre in sg:
            sg_split = song_genre.split(",")
            self.genres[sg_split[0]] = sg_split[1].replace("\n","")
        # print(self.genres)


    def findSongID(self,song):
        try:
            print(self.genres[song])
        except:
            print("Song not found")
            self.missingSongs.append(song)

    def findMostCommonGenre(self,source):
        self.songs = {}
        self.genre_count = {}

        lim = False
        i = 50

        missing = 0
        found = 0
        for filename in os.listdir(source):

            if lim:
                if i == 0:
                    break
                i -= 1

            if filename != ".DS_Store" and filename != ".gitattributes" and filename != "LICENSE" and filename != "rEADME.md":
                print("Artist: " + filename)
                for file in os.listdir(source + "/" + filename):
                    songname = file.replace(".mid","")
                    try:
                        g = self.genres[songname]
                        if not g in self.genre_count:
                            self.genre_count[g] = 1
                        else:
                            self.genre_count[g] += 1
                        found += 1
                    except:
                        missing += 1

        print(self.genre_count)
        print("Found",found)
        print("Missing",missing)
        return self.songs


    def getLabels(self):
        msd_source = self.source+"TrainingData/Labels/lmd_matched_h5"
        for filename in os.listdir(msd_source):
            inner_source = msd_source+"/"+filename
            for inner_filename in os.listdir(inner_source):
                print(inner_filename)
                for f in os.listdir():
                    inner_source = msd_source + "/" + filename
            print(filename)
            break


    def getLabels(self,source):
        i = 0
        for filename in os.listdir(source):
            if not filename.endswith(".h5"):
                file = source+"/" + filename
                print(file)
                i+=self.getLabels(file)
            else:
                print("filename:",filename)
                f = h5py.File(source+"/"+filename,'r')
                print(list(f.keys()))
                i+=1
        return i


class H5_reader:
    @staticmethod
    def get_title(h5,songidx=0):
        """
        Gets song title
        :param h5: file labels
        :param songidx:
        :return: string of title
        """
        return h5.root.metadata.songs.cols.title[songidx].decode('UTF-8')

    @staticmethod
    def get_artist_name(h5):
        """
        Gets artist name
        :param h5: The song labels
        :return: String of the artist name
        """
        return h5.root.metadata.songs.cols.artist_name[0].decode('UTF-8')

    @staticmethod
    def get_track_id(h5,songidx=0):
        """
        Gets time signature of the track
        :param h5: The song labels
        :param songidx:
        :return:
        """
        return h5.root.analysis.songs.cols.track_id[songidx].decode('UTF-8')

    @staticmethod
    def get_tempo(h5,songidx=0):
        """
        Gets track tempo
        :param h5: The song labels
        :param songidx:
        :return: the tempo of the song
        """
        return int(h5.root.analysis.songs.cols.tempo[songidx])

    @staticmethod
    def get_time_signature(h5,songidx=0):
        """
        Gets time signature of the track
        :param h5: The song labels
        :param songidx:
        :return:
        """
        return h5.root.analysis.songs.cols.time_signature[songidx]

    @staticmethod
    def get_key(h5,songidx=0):
        """
        Gets key
        :param h5: The song labels
        :param songidx:
        :return: returns the key
        """
        return h5.root.analysis.songs.cols.key[songidx]

    @staticmethod
    def get_song_features(h5):
        """
        :param h5:
        :return: [ARTIST, TITLE, KEY, TEMPO, TIME SIG]
        """
        features = [H5_reader.get_track_id(h5), H5_reader.get_artist_name(h5), H5_reader.get_title(h5), H5_reader.get_key(h5), H5_reader.get_tempo(h5), H5_reader.get_time_signature(h5)]
        return features


class GenreFinder:
    def __init__(self):
        self.track_genres = {}
        if not os.path.isfile('genres.csv'):
            self.get_genre_data("D:\MusicGenTrainingData\msd_tagtraum_cd1.cls")
            self.get_genre_data("D:\MusicGenTrainingData\msd_tagtraum_cd2.cls")
            self.get_genre_data("D:\MusicGenTrainingData\msd_tagtraum_cd2c.cls")
        else:
            genre_file = open("genres.csv","r")
            csvreader = csv.reader(genre_file, delimiter=',')
            for row in csvreader:
                self.track_genres[row[0]] = row[1]
            print("Track genres read")


    def get_genre_data(self,path):
        file = open(path, "r")
        track_genres_file = file.readlines()[7:]

        # Opens the genre file that stores the track ids and their genre
        genre_file = open("genres.csv", "w", newline='')
        writer = csv.writer(genre_file)

        # Iterates through the lines in the track/genre list
        # Adds track id as key and genre as value
        for i in range(len(track_genres_file)):
            t_g = track_genres_file[i].replace("\n", "").split("\t")

            # removes the second genre from songs with 2
            if len(t_g) == 3:
                t_g.pop(-1)

            self.track_genres[t_g[0]] = t_g[1]
            writer.writerow(t_g)
        # print("Track genres recorded: ",len(self.track_genres))

        file.close()

    def get_genre(self,song_id):
        """
        retrieves the genre of the song
        :param song_id: song id for the genre
        :return: the genre in a string
        """
        try:
            return self.track_genres[song_id]
        except:
            print("Could not be found")

    def find_most_commmon_genre(self,track_ids):
        genre_count = {}
        missing=0
        for id in track_ids:
            #print("Genre:",self.track_genres[id])
            try:
                genre = self.track_genres[id]
                try:
                    genre_count[genre]+=1
                except:
                    genre_count[genre]=1

            except:
                missing+=1

        genre_count={k: v for k, v in sorted(genre_count.items(), key=lambda item: item[1], reverse=True)}
        print(genre_count)
        print(missing,"tracks without genre")


class File_handler:
    @staticmethod
    def get_all_ids(basedir, ext='.h5'):
        """
        Collects all song titles and stores them in the titles file
        Takes a long time to run so
        :param ext:
        :return:
        """
        ids = []
        if not os.path.isfile("track_ids.csv"):
            count = 0
            titles_file = open("track_ids.csv", "w", newline='')
            writer = csv.writer(titles_file, delimiter=",")
            for root, dirs, files in os.walk(basedir):
                # writer = csv.writer(titles_file, delimiter=",")
                files = glob.glob(os.path.join(root, '*' + ext))
                for f in files:
                    h5 = tables.open_file(f, mode='r')
                    ids.append(H5_reader.get_track_id(h5))
                    #writer.writerow(H5_reader.get_track_id(h5))
                    #titles_file.write(H5_reader.get_track_id(h5))
                    h5.close()
                    if count % 10000 == 0:
                        print(f"{count} file ids collected")
                    count += 1

            writer.writerow(ids)
            titles_file.close()
        else:
            # opens the track ids file which contains a list of track ids
            title_file = open("track_ids.csv","r")
            # gets the trackids from the file and puts them into a list
            ids = title_file.readlines()[0].split(',')
            # removes the \n from the end of the last item in the list
            ids[-1]=ids[-1].replace("\n","")

        return ids



    @staticmethod
    def count_all_files(basedir,ext='.h5'):
        """
        What do you think it does
        :param basedir:
        :param ext:
        :return: int number of files
        """
        cnt = 0
        for root, dirs, files in os.walk(basedir):
            files = glob.glob(os.path.join(root,'*'+ext))
            cnt += len(files)
        print("Files counted:",cnt)
        return cnt




def demo():
    path = "D:\MusicGenTrainingData\lmd_matched_h5\A\A\A\TRAAAGR128F425B14B.h5"
    h5_labels = tables.open_file(path, mode='r')
    song_features = H5_reader.get_song_features(h5_labels)
    print(song_features)
    h5_labels.close()
    genreFinder = GenreFinder()
    genreFinder.get_genre(song_features[0])


genreFinder = GenreFinder()
File_handler.count_all_files("D:\MusicGenTrainingData\lmd_matched_h5")
track_ids=File_handler.get_all_ids("D:\MusicGenTrainingData\lmd_matched_h5")
genreFinder.find_most_commmon_genre(track_ids)
