"""
This program fetches html songs for a band on the specified lyrics website,
parses out the text of the lyrics, and writes a txt file containing lyrics for
use in a Markov Chain lyric generator
"""

import random
from sys import stdout
import re
import urllib.request as urlreq
from requests import head
from bs4 import BeautifulSoup as soup, SoupStrainer as strain
from numpy.random import choice
from time import sleep
import directories


def set_band():
    """
    Takes band name as user input and returns tuple containing the name
    formatted for use in urls for different sites
    """

    band_name = input('Enter the name of the band: ')
    print()

    if band_name:
        band_name_nospace = re.sub('[^a-zA-Z0-9]+', '', band_name).lower()  # for azlyrics and darklyrics

        band_name_plus = re.sub('[^a-zA-Z0-9 ]+', '', band_name).strip()  # for lyricsfreak
        band_name_plus = re.sub('[ ]+', '+', band_name_plus).lower()

        return band_name_nospace, band_name_plus
    else:
        return ''


def build_url(website_code, band_name):
    """
    Builds and returns url string based on website code and
    band_name tuple returned from set_band()
    """

    url = None

    if website_code == 'az':
        url = ''.join(['http://www.azlyrics.com/', band_name[0], '/', band_name, '.html'])
    elif website_code == 'dl':
        url = ''.join(['http://www.darklyrics.com/', band_name[0], '/', band_name, '.html'])
    elif website_code == 'lf':
        url = ''.join(['http://www.lyricsfreak.com/', band_name[0], '/', band_name, '/'])

    return url


def url_check(url):
    """
    Checks to make sure site at url exists;
    Returns True if status code < 400, False otherwise
    """

    try:
        site_ping = head(url)
        if site_ping.status_code < 400:
            return True
        else:
            print('Could not connect to url. Make sure band name entered properly, \
or that the band has a page on the website selected.\n')
            return False
    except TypeError:
        print('Url is type None')


def get_links(website_code, url):
    """
    Fetches html from url given;
    Uses website_code to select appropriate _get_links_ function;
    Returns a list of links to pages containing lyrics for a band
    """
    user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    html = urlreq.urlopen(urlreq.Request(url, headers=user_agent))

    lyrics_links = None
    if website_code == 'az':
        lyrics_links = _get_links_azlyrics(html)
    elif website_code == 'dl':
        lyrics_links = _get_links_darklyrics(html)
    elif website_code == 'lf':
        lyrics_links = _get_links_lyricsfreak(html)

    try:  # Randomize order of links to avoid sequential link access
        lyrics_links = choice(lyrics_links, len(lyrics_links), replace=False)
    except TypeError:
        print('Failed to get links\n')
    else:
        return lyrics_links


def _get_links_azlyrics(html):
    """
    Parses given html from opened lyricsfreak.com page,
    and returns a list of urls for all pages containing lyrics
    """

    only_links = strain('div', attrs={'id': 'listAlbum'})
    link_soup = soup(html, 'html.parser', from_encoding='utf-8', parse_only=only_links)
    lyrics_a = link_soup.find_all('a', attrs={'id': None})

    lyrics_links = []
    for a in lyrics_a:
        lyrics_links.append(a['href'].replace('..', 'http://www.azlyrics.com'))

    return lyrics_links


def _get_links_darklyrics(html):
    """
    Parses given html from opened lyricsfreak.com page,
    and returns a list of urls for all pages containing lyrics
    """

    only_links = strain('div', {'class': 'album'})
    link_soup = soup(html, 'html.parser', from_encoding='utf-8', parse_only=only_links)
    lyrics_a = [div.a for div in link_soup]

    lyrics_links = []
    for a in lyrics_a:
        lyrics_links.append(a['href'].replace('..', 'http://www.darklyrics.com'))

    return lyrics_links


def _get_links_lyricsfreak(html):
    """
    Parses given html from opened lyricsfreak.com page,
    and returns a list of urls for all pages containing lyrics
    """

    only_links = strain('table', {'name': 'song'})
    link_soup = soup(html, 'html.parser', from_encoding='utf-8', parse_only=only_links)
    lyrics_a = link_soup.find('tbody').find_all('a')

    lyrics_links = []
    for a in lyrics_a:
        a = ''.join(('http://www.lyricsfreak.com', a['href']))
        lyrics_links.append(a)

    return lyrics_links


def get_lyrics(website_code, links, band_name):
    """
    Iterates through a randomized list of links (provided by get_links)
    to a bands lyrics pages, opens each url in sequence,
    and saves a cleaned string of the lyrics to a text file.
    Website code dictates how html is parsed.
    """

    print('There is a delay between url requests to reduce risk of IP being blocked.\n\
This process may take several minutes, depending on the number of songs being retrieved.\n')

    user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    lyrics = []

    stdout.write('Progress: %d%%   %s' % (0, '\r'))
    stdout.flush()

    for index, link in enumerate(links):
        html = urlreq.urlopen(urlreq.Request(link, headers=user_agent))

        if website_code == 'az':
            only_class_id_none = strain('div', attrs={'class': None, 'id': None})
            lyrics_soup = soup(html, 'html.parser', parse_only=only_class_id_none)
        elif website_code == 'dl':
            only_class_album = strain('div', {'class': 'album'})
            lyrics_soup = soup(html, 'html.parser', parse_only=only_class_album)
        elif website_code == 'lf':
            only_id_content_h = strain('div', {'id': 'content_h'})
            lyrics_soup = soup(html, 'html.parser', parse_only=only_id_content_h)

        _clean_html(website_code, lyrics_soup)

        lyrics.append(_read_text(lyrics_soup))

        done = int((index+1)/len(links)*100)
        stdout.write('Progress: %d%%   %s' % (done, '\r'))
        stdout.flush()
        sleep(random.uniform(3.0, 5.0))

    _write_text(lyrics, band_name[0])


def _clean_html(website_code, html):
    """
    Wrapper function that runs appropriate _clean_html_ function on
    BeautifulSoup object based on given website_code
    """

    if website_code == 'az':
        _clean_html_azlyrics(html)
    elif website_code == 'dl':
        _clean_html_darklyrics(html)
    elif website_code == 'lf':
        _clean_html_lyricsfreak(html)


def _clean_html_azlyrics(html):
    """
    Removes undesired tags and associated contents from azlyrics.com
    html, leaving only the text of the lyrics
    """

    for i in html('i'):
        i.decompose()

    for br in html.find_all('br'):
        br.replace_with('')


def _clean_html_darklyrics(html):
    """
    Removes undesired tags and associated contents from darklyrics.com
    html, leaving only the text of the lyrics
    """

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


def _clean_html_lyricsfreak(html):
    """R
    emoves undesired tags and associated contents from lyricsfreak.com
    html, leaving only the text of the lyrics
    """

    for br in html.find_all('br'):
        br.replace_with(' ')


def _read_text(html):
    """
    Takes cleaned up html text in a BeautifulSoup object, appends
    lines to a list, removes any empty strings, and returns a string
    containing all lyrics
    """

    lyric_list = []

    for word in html.get_text().split():
        lyric_list.append(word)

    lyric_list[:] = [x for x in lyric_list if x != '']
    lyrics_string = ' '.join(lyric_list)

    return lyrics_string


def _write_text(lyrics, band_name):
    """Write lyrics to band_namelyrics.txt in the original_lyrics folder"""

    curr_dir = directories.get_script_path()
    filename = ''.join((curr_dir, '/original_lyrics/', band_name, 'lyrics.txt'))
    lyrics_string = ' '.join(lyrics)

    with open(filename, 'w', encoding='utf-8') as lf:
        if lyrics:
            lf.writelines(lyrics_string)
        else:
            print("Lyrics string is empty\n")
