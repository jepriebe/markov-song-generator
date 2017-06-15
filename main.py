import fetch_data
from markov_python.cc_markov import MarkovChain
import lyricize
from os.path import isfile, dirname, isdir
from os import makedirs


curr_dir = dirname(__file__)

while True:
    band_name = fetch_data.set_band()
    if band_name:
        url = fetch_data.build_url(band_name)
        if fetch_data.url_check(url):
            break
    else:
        continue

filefolder = ''.join((curr_dir, '/original_lyrics'))
if not isdir(filefolder):
    makedirs(filefolder)

filepath = ''.join((filefolder, '/', band_name[1], 'lyrics.txt'))
if not isfile(filepath):
    # links = fetch_data.get_links(url)
    # lyrics = fetch_data.get_lyrics(links)
    # print(lyrics)
    print('File does not exist')
    pass

lyrics_markov = MarkovChain()
lyrics_markov.add_file(filepath)

while True:
    markov_song = lyrics_markov.generate_text()
    markov_song = lyricize.lyricize(markov_song)

    print(markov_song)

    option = input('\nEnter S to save and continue, X to exit program, SX to save and exit, \
or press Enter to continue without saving: ')

    if 's' in option.lower():
        lyricize.save_song(curr_dir, band_name[1], markov_song)

    if 'x' in option.lower():
        break
