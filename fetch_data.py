"""This program fetches html from the Blind Guardian lyrics
pages on darklyrics.com, parses out the text of the lyrics,
and provides a list of lines for a Markhov Chain lyric generator"""

import random
from sys import stdout
import re
import urllib.request as urlreq
from requests import head
from bs4 import BeautifulSoup as soup, SoupStrainer as strain
from numpy.random import choice
from time import sleep
from os.path import dirname


def set_band():
    """Takes band name as user input and returns tuple containing lowercase
    first letter, alphanumeric-only name, and same with whitespace replaced
    by '+' for lyricsfreak.com urls"""

    band_name = input("Enter the name of the band: ")

    if band_name:
        band_name = band_name.strip()
        lf_band_name = re.sub('[ ]+', '+', band_name).lower()
        band_name = re.sub('[\\W]+', '', band_name).lower()

        return band_name[0], band_name, lf_band_name
    else:
        return ''


def build_url(band_name):
    """Builds and returns url string using band_name tuple returned from
    set_band()"""

    url = ''.join(['http://www.lyricsfreak.com/', band_name[0], '/', band_name[2], '/'])

    return url


def url_check(url):
    """Checks to make sure site exists;
    Returns True if status code < 400, False otherwise"""

    site_ping = head(url)
    if site_ping.status_code < 400:
        return True
    else:
        print('Could not find file or connect to url. Make sure band name entered properly, \
or that the band has a lyricsfreak.com page.\n')
        return False


def get_links(url):
    """Opens artist page on lyricsfreak.com for band specified, parses html,
    and returns a list of urls for all individual album pages containing lyrics"""
    user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    raw_site = urlreq.urlopen(urlreq.Request(url, headers=user_agent))
    only_song_table = strain('table', {'name': 'song'})
    song_table = soup(raw_site, 'html.parser', from_encoding='utf-8', parse_only=only_song_table)

    album_a = song_table.find('tbody').find_all('a')

    album_links = []
    for a in album_a:
        a = ''.join(('http://www.lyricsfreak.com', a['href']))
        album_links.append(a)

    album_links = choice(album_links, len(album_links), replace=False)

    return album_links


def __clean_html(html):
    """Removes undesired tags and associated contents, leaving only
    the text of the lyrics"""

    for br in html.find_all('br'):
        br.replace_with(' ')


def __read_text(site):
    """Takes cleaned up html text in a BeautifulSoup object, appends
    lines to a list, removes any empty strings, and returns a string
    containing all lyrics"""

    lyric_list = []

    for word in site.get_text().split():
        lyric_list.append(word)

    lyric_list[:] = [x for x in lyric_list if x != '']
    lyrics_string = ' '.join(lyric_list)

    return lyrics_string


def __write_lyrics(lyrics, band_name):
    """Write lyrics to band_namelyrics.txt in the original_lyrics folder"""

    curr_dir = dirname(__file__)
    filename = ''.join((curr_dir, '/original_lyrics/', band_name, 'lyrics.txt'))
    lyrics_string = ' '.join(lyrics)

    with open(filename, 'w', encoding='utf-8') as lf:
        if lyrics:
            lf.writelines(lyrics_string)
        else:
            print("Lyrics string is empty")


def get_lyrics(links, band_name):
    """Iterates through a randomized list of links (provided by get_links),
    opens each url in sequence, and saves a cleaned string of the lyrics
    to a text file"""

    print('There is a delay between url requests to reduce risk of IP being blocked.\
This process may take several minutes, depending on the number of songs being retrieved.')

    user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    lyrics = []

    stdout.write('Progress: %d%%   %s' % (0, '\r'))
    stdout.flush()

    for index, link in enumerate(links):
        raw_site = urlreq.urlopen(urlreq.Request(link, headers=user_agent))
        only_id_content_h = strain('div', {'id': 'content_h'})
        site = soup(raw_site, 'html.parser', parse_only=only_id_content_h)

        __clean_html(site)

        lyrics.append(__read_text(site))

        done = int((index+1)/len(links)*100)
        stdout.write('Progress: %d%%   %s' % (done, '\r'))
        stdout.flush()
        sleep(random.uniform(3.0, 5.0))

    __write_lyrics(lyrics, band_name)


# code for scraping darklyrics.com
'''def build_url(band_name):
    """Builds and returns url string using band_name tuple returned from
    set_band()"""

    url = ''.join(['http://www.darklyrics.com/', band_name[0], '/', band_name[1], '.html'])

    return url


def url_check(url):
    """Checks to make sure site exists;
    Returns True if status code < 400, False otherwise"""

    site_ping = head(url)
    if site_ping.status_code < 400:
        return True
    else:
        print('Could not find file or connect to url. Make sure band name entered properly, \
or that the band has a darklyrics.com page.\n')
        return False


def get_links(url):
    """Opens artist page on darklyrics.com for band specified, parses html,
    and returns a list of urls for all individual album pages containing lyrics"""

    raw_site = urlreq.urlopen(url)
    only_class_album = strain('div', {'class': 'album'})
    link_divs = soup(raw_site, 'html.parser', from_encoding='utf-8', parse_only=only_class_album)

    album_a = [div.a for div in link_divs]

    album_links = []
    for a in album_a:
        album_links.append(a['href'].replace('..', 'http://darklyrics.com'))

    return album_links


def __clean_html(html):
    """Removes undesired tags and associated contents, leaving only
    the text of the lyrics"""

    for h3 in html('h3'):
        h3.decompose()

    for i in html('i'):
        i.decompose()

    for br in html.find_all('br'):
        br.replace_with('')

    if html.find('div', {'class': 'thanks'}):
        html.find('div', {'class': 'thanks'}).decompose()
    if html.find('div', {'class': 'note'}):
        html.find('div', {'class': 'note'}).decompose()
    if html.find('a'):
        html.a.decompose()


def __read_text(site):
    """Takes cleaned up html text in a BeautifulSoup object, appends
    lines to a list, removes any empty strings, and returns a string
    containing all lyrics"""

    lyric_list = []

    for word in site.get_text():
        lyric_list.append(word)

    lyric_list[:] = [x for x in lyric_list if x != '']
    lyrics_string = '\n'.join(lyric_list)

    return lyrics_string'''
