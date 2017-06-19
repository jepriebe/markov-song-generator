"""TODO: shift prepositions and articles and such onto next line,
or pull from next line, remove extra newlines, delete hanging preps
and articles from last line"""

from scipy.stats import truncnorm
from math import floor
from collections import deque
from os.path import isdir, exists, dirname
from os import makedirs


def __get_truncated_normal(mean=0.0, sd=1, low=1, upp=8):
    """Re-parameterize the truncnorm function in scipy.stats"""
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


def __fix_lines(lyrics, max_words):
    """There some words you just don't put at the end of a line in a song.
    Uses user-defined list in non-terminal-words.txt to move these words
    from the end of one line to the start of the next, or remove them if
    it is the last line. Returns a list of strings."""

    word_file = ''.join([dirname(__file__), '/non_terminal_words.txt'])
    non_terminal_words = []
    try:
        with open(word_file, 'r') as wf:
            non_terminal_words = [line[1:] for line in wf.read().splitlines() if line and line[0] == '#']

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
    """randomly selects current line length based on given range and
    probability distribution. Create line by popping left specified
    number of words from raw lyrics and appending them to line deque,
    then append line to list. Create new lines until no words left,
    then __fix_lines. Returns a string."""

    clean_lyrics = []
    words_left = len(raw_lyrics)

    try:
        while words_left > 0:
            curr_line_length = floor(__get_truncated_normal(0.7*max_words, 1, min_words, max_words+1).rvs(1))

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

    clean_lyrics = __fix_lines(clean_lyrics, max_words)

    return '\n'.join(clean_lyrics)


def save_song(dir, artist, song):
    """Saves current lyrics as text file inside a user_songs folder"""

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
