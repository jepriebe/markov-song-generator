"""
TODO:
- add choices for max line length and max word count of generated songs
- add options to choose a different website or band without restarting program
"""

import fetch_data
from markov_python.cc_markov import MarkovChain
import lyricize
from os.path import isfile, isdir
from os import makedirs
import directories
import re


def main():
    while True:
        band_name = fetch_data.set_band()

        if band_name:
            filepath = ''.join((filefolder, '/', band_name[0], 'lyrics.txt'))

            if not isfile(filepath):
                print('File does not exist. Fetching lyrics from web.\n')

                while True:
                    print('Website codes:\nCODE\tWEBSITE\naz\tazlyrics.com\ndl\tdarklyrics.com\nlf\tlyricsfreak.com\n')
                    website_code = input('Enter code for website you want to retrieve lyrics from: ')
                    print()

                    if website_code:
                        website_code = re.sub('[^a-zA-Z0-9.]+', '', website_code).lower()

                        if website_code in ('az', 'dl', 'lf'):
                            break
                        elif 'azlyrics' in website_code:
                            website_code = 'az'
                            break
                        elif 'darklyrics' in website_code:
                            website_code = 'dl'
                            break
                        elif 'lyricsfreak' in website_code:
                            website_code = 'lf'
                            break
                        else:
                            print('Unrecognized website code\n')
                            continue
                    else:
                        continue

                if website_code == 'lf':
                    url = fetch_data.build_url(website_code, band_name[1])
                else:
                    url = fetch_data.build_url(website_code, band_name[0])

                if website_code == 'az':  # azlyrics.com blocks HEAD requests
                    try:
                        lyrics_links = fetch_data.get_links(website_code, url)
                        fetch_data.get_lyrics(website_code, lyrics_links, band_name)
                        break
                    except IOError:
                        print('Could not connect to url. Make sure band name entered properly, \
    or that the band has a page on the website selected.\n')
                        continue
                else:
                    if fetch_data.url_check(url):
                        lyrics_links = fetch_data.get_links(website_code, url)
                        fetch_data.get_lyrics(website_code, lyrics_links, band_name)
                        break
                    else:
                        continue
            else:
                break
        else:
            continue

    lyrics_markov = MarkovChain()
    lyrics_markov.add_file(filepath)

    max_song_length, min_line_length, max_line_length = lyricize.set_length_parameters()

    while True:
        markov_song = lyrics_markov.generate_text(max_song_length)
        markov_song = lyricize.lyricize(markov_song, min_line_length, max_line_length)

        print(markov_song)

        while True:
            print('\n(S = Save, X = Exit, R = Reset, A = Adjust maximum line and song length; \
Pressing Enter continues without saving)\nSX, SR, and SA are valid combinations')
            option = input('Select an option: ')
            print()

            option = re.sub('[ ]', '', option).lower()

            if option in ('s', 'sx', 'xs', 'sr', 'rs', 'sa', 'as'):
                lyricize.save_song(curr_dir, band_name, markov_song)

            if option in ('', 's'):
                break

            if option in ('a', 'sa', 'as'):
                max_song_length, min_line_length, max_line_length = lyricize.set_length_parameters()
                break

            if option in ('r', 'sr', 'rs'):
                return True

            if option in ('x', 'sx', 'xs'):
                return False

            if option not in ('', 'x', 'r', 'a', 's', 'sx', 'xs', 'sr', 'rs', 'sa', 'as'):
                print('Unrecognized input')
                continue


curr_dir = directories.get_script_path()
filefolder = ''.join((curr_dir, '/original_lyrics'))
if not isdir(filefolder):
    makedirs(filefolder)

run_main = True
while run_main:
    run_main = main()
