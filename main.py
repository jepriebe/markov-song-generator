"""
TODO:
- add choices for max line length and max word count of generated songs
- add options to choose a different website or band without restarting program
"""

import fetch_data
from markov_python.cc_markov import MarkovChain
import lyricize
from os.path import isfile, isdir, dirname
from os import makedirs
import directories
import re


curr_dir = directories.get_script_path()

print('\nWebsite codes:\nCODE\tWEBSITE\ndl\tdarklyrics.com\nlf\tlyricsfreak.com\n')

while True:
    website_code = input('Enter code for website you want to retrieve lyrics from: ')
    print()

    if website_code:
        website_code = re.sub('[^a-zA-Z0-9.]+', '', website_code).lower()

        if website_code == 'dl' or\
                website_code == 'darklyrics' or\
                website_code == 'darklyrics.com':
            website_code = 'dl'
            break
        elif website_code == 'lf' or\
                website_code == 'lyricsfreak' or\
                website_code == 'lyricsfreak.com':
            website_code = 'lf'
            break
        else:
            print('Unrecognized website code\n')


while True:
    band_name = fetch_data.set_band(website_code)
    if band_name:
        url = fetch_data.build_url(website_code, band_name)
        if fetch_data.url_check(url):
            break
    else:
        continue

filefolder = ''.join((curr_dir, '/original_lyrics'))
if not isdir(filefolder):
    makedirs(filefolder)

band_name = re.sub('[^a-zA-Z0-9]', '', band_name)
filepath = ''.join((filefolder, '/', band_name, 'lyrics.txt'))
if not isfile(filepath):
    print(filefolder)
    print(filepath)
    print('File does not exist. Fetching lyrics from web.\n')
    lyrics_links = fetch_data.get_links(website_code, url)
    lyrics = fetch_data.get_lyrics(website_code, lyrics_links, band_name)

lyrics_markov = MarkovChain()
lyrics_markov.add_file(filepath)

while True:
    markov_song = lyrics_markov.generate_text()
    markov_song = lyricize.lyricize(markov_song)

    print(markov_song)

    option = input('\nEnter S to save and continue, X to exit program, SX to save and exit, \
or press Enter to continue without saving: ')
    print()

    if 's' in option.lower():
        lyricize.save_song(curr_dir, band_name, markov_song)

    if 'x' in option.lower():
        break
