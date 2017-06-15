"""This program fetches html from the Blind Guardian lyrics
pages on darklyrics.com, parses out the text of the lyrics,
and provides a list of lines for a Markhov Chain lyric generator"""

import re
import urllib.request as urlreq
from requests import head
from bs4 import BeautifulSoup as soup, SoupStrainer as strain


def set_band():
    """Takes band name as user input and returns tuple containing lowercase
    first letter and alphanumeric-only name"""

    band_name = input("Enter the name of the band: ")

    if band_name:
        band_name = re.sub('[^\\w]+', '', band_name)
        band_name = band_name.lower()

        return band_name[0], band_name
    else:
        return ''


def build_url(band_name):
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

    return lyrics_string


def get_lyrics(links):
    """Iterates through a list of links (provided by get_links),
    opens each url in sequence, and saves a cleaned string
     of the lyrics to a text file"""

    lyrics = ''

    for link in links[1]:
        raw_site = urlreq.urlopen(link)
        only_class_lyrics = strain('div', {'class': 'lyrics'})
        site = soup(raw_site, 'html.parser', parse_only=only_class_lyrics)

        __clean_html(site)

        lyrics = __read_text(site)

    filename = ''.join((links[0][1], 'lyrics.txt'))

    with open(filename, 'w') as lf:
        if lyrics:
            lf.writelines(lyrics)
        else:
            print("Lyrics string is empty")
