"""
Contains functions to take raw, unformatted text and format it to resemble
the lyrics of a song, as well as save the new text to a file
"""

from scipy.stats import truncnorm
from math import floor
from collections import deque
from os.path import isdir, exists, dirname
from os import makedirs


def set_length_parameters():
    """
    Returns integers for the minimum and maximum line length to use in lyricize(),
    as well as the maximum song length to be used in cc_markov.generate text
    """

    while True:
        try:
            max_song_length = int(input('Enter maximum song length in # of words: '))
            print()
        except ValueError:
            print('Input must be a positive integer')
            continue

        if max_song_length <= 0:
            print('Maximum song length must be greater than 0\n')
            continue
        else:
            break

    while True:
        try:
            min_line_length = int(input('Enter minimum line length in # of words: '))
            print()
        except ValueError:
            print('Input must be a positive integer\n')
            continue

        if min_line_length <= 0:
            print('Minimum line length must be greater than 0\n')
            continue
        else:
            break

    while True:
        try:
            max_line_length = int(input('Enter maximum line length in # of words: '))
            print()
        except ValueError:
            print('Input must be a positive integer\n')
            continue

        if max_line_length <= 0:
            print('Maximum line length must be greater than 0\n')
            continue
        elif max_line_length < min_line_length:
            print('Maximum line length must be greater than or equal to minimum\n')
            continue
        else:
            break

    return max_song_length, min_line_length, max_line_length


def _get_truncated_normal(mean=0.0, sd=1, low=1, upp=8):
    """
    Re-parameterize the truncnorm function from scipy.stats;
    return random value from normal probability curve given mean,
    standard deviation, and lower and upper bounds
    """
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


def _fix_lines(lyrics, max_words):
    """
    There some words you just don't put at the end of a line in a song.
    Uses user-defined list in non-terminal-words.txt to move these words
    from the end of one line to the start of the next, or remove them if
    it is the last line. Takes the raw lyrics text and integer for max
    number of words allowed on a line. Returns a list of strings.
    """

    word_file = ''.join([dirname(__file__), '/non_terminal_words.txt'])
    non_terminal_words = []
    try:
        with open(word_file, 'r') as wf:
            non_terminal_words = [line[1:] for line in wf.read().splitlines()
                                  if line and line[0] == '#']

    except OSError:
        print('Could not find non_terminal_words.txt\n')
        exit()

    words_to_shift = []
    new_lyrics = []
    for i in range(0, len(lyrics)):
        line = lyrics[i]

        if words_to_shift:
            for word in words_to_shift:
                line.appendleft(word)

        words_to_shift = []

        while len(line) > max_words:
            popped_word = line.pop()
            words_to_shift.append(popped_word)

        for j in range(len(list(line)) - 1, -1, -1):
            if non_terminal_words and line[j] in non_terminal_words:
                popped_word = line.pop()
                words_to_shift.append(popped_word)
            else:
                break

        line_string = ' '.join(line).capitalize()
        if line_string:
            new_lyrics.append(line_string)

    return new_lyrics


def lyricize(raw_lyrics, min_words=1, max_words=8):
    """
    Randomly selects current line length based on given range and
    probability distribution. Create line by popping left specified
    number of words from raw lyrics and appending them to line deque,
    then append line to list. Create new lines until no words left,
    then _fix_lines. Takes raw lyrics and min and max line lengths.
    Returns a string.
    """

    clean_lyrics = []
    words_left = len(raw_lyrics)

    try:
        while words_left > 0:
            curr_line_length = floor(_get_truncated_normal(0.7 * max_words, 1, min_words,
                                                           max_words + 1).rvs(1))

            if curr_line_length > words_left:
                curr_line_length = words_left

            line = deque()
            for word in range(curr_line_length):
                line.append(raw_lyrics.popleft())

            # line_string = ' '.join(line)
            # clean_lyrics.append(line_string.capitalize())
            clean_lyrics.append(line)
            words_left -= curr_line_length
    except IndexError:
        pass

    clean_lyrics = _fix_lines(clean_lyrics, max_words)

    return '\n'.join(clean_lyrics)


def save_song(dir, artist, song):
    """
    Saves current lyrics as text file inside a user_songs folder.
    Takes directory of script, and strings for artist name and song
    text to be saved.
    """

    while True:
        try:

            song_title = input('Enter a song title: ')
            print()

            filefolder = ''.join((dir, '/user_songs/', artist[0]))
            if not isdir(filefolder):
                makedirs(filefolder)

            filepath = ''.join((filefolder, '/', song_title, '.txt'))
            if exists(filepath):
                while True:
                    overwrite = input('File already exists. Would you like to overwrite this file (y/n)? ')
                    print()

                    if overwrite.lower() not in 'yn':
                        print('Invalid input\n')
                    else:
                        break

                if overwrite.lower() == 'n':
                    continue

            with open(filepath, 'w') as sf:
                sf.write(song)
                break

        except OSError:
            print('Invalid file name\n')
