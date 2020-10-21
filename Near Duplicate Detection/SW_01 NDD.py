
# coding: utf-8


import csv
import string
from collections import defaultdict
import time

###################################################################
# (1) import lyrics and title songs and store them into dictonary #
###################################################################
start = round(time.time(),1)
print('Start importing songs...')

SONGS_DOCUMENT = "./dataset/250K_lyrics_from_MetroLyrics.csv" # pick the file
in_file = open(SONGS_DOCUMENT, "r", encoding='latin1') # open it
csv_reader = csv.reader(in_file, delimiter=',') # read it
csv_reader.__next__() # to skip the header: first line containing the name of each field.

dictionary_song = dict()
for record in csv_reader:# pick every row

    song = 'song_'+record[0] # pick the ID
    
    lyric = record[-1].lower() # pick the lyric and lowercase evantual uppercase words 
    lyric_splitted = lyric.replace("'"," ").translate(str.maketrans('', '', string.punctuation)).split() # clean the lyric from punctuation and split.
    
    dictionary_song[song] = lyric_splitted # add the list of words into the dictionary_song

print('All songs imported!','\n')

##########################################################################    
# (2) decompose the lyric into shingles and create the Universe shingles #
##########################################################################
print('Start shingling...')

universe_shingles = dict()  # universe of all shingles where key is the shingle and value is the unique number identifier
universe_songs_hash = defaultdict(list)  # dictionary where the key is the song title and the value is the list of unique shingle identifiers
hash_number = 0  # number used to hash an unique shingle
num_shingled_songs = 0  # counter used to show the work in progress

for song,lyrics in dictionary_song.items():
    
    begin = 0  # shingle starting point
    end = 3  # shingle end point

    lyric_shingle_list = set()  # set that will contain the unique shingles for a specific song
    while end <= len(lyrics):  # start while loop to produce the shingles

        # using shingles
        shingle = tuple(lyrics[begin:end])  # get the shingle
        lyric_shingle_list.add(shingle)  # add the shingle to the lyric_shingle_list set of the song

        if shingle not in universe_shingles.keys():  # if shingle not in the Universe
            universe_shingles[shingle] = hash_number  # add the shingle to the universe associating it with a unique number
            universe_songs_hash[song].append(hash_number)  # add the identifier to the universe_songs_hash
            hash_number += 1
        else:  # if shingle in the Universe
            universe_songs_hash[song].append(universe_shingles[shingle])  # add the identifier to the universe_songs_hash

        begin += 1  # increase the shingle strating point
        end += 1  # increasing the shingle ending point

    num_shingled_songs += 1
    if (num_shingled_songs % 10000 == 0):
        print("Number of shingled songs so far: " + str(num_shingled_songs))


print('Done, all songs shingled!','\n')

#########################
# (3) store into a .tsv #
#########################
print('Storing shigles sets...')

with open("./dataset/lyrics_shingles_sets.tsv", 'w', newline='') as out_file:
    tsv_writer = csv.writer(out_file, delimiter='\t')
    tsv_writer.writerow(['song_id','set_as_list_of_elements_id']) #write header
    for k,v in universe_songs_hash.items():
        tsv_writer.writerow([k,v]) #write key value into .tsv file

end = time.time()  
total_time = round((end-start)/60,)
print('Shigles sets stored into "./dataset" directory!','\n')
print('Total time: '+str(total_time)+' minutes') 

