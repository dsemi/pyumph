#!/usr/bin/python3

import os
import requests
from docopt import docopt
from queue import Queue
from threading import Thread

class fdict(dict):
    def __missing__(self, key):
        return '{%s}' % key

MAX_RESULT_LIMIT = 50
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']

playlist_url = 'https://www.googleapis.com/youtube/v3/playlistItems?key={api_key}&part=contentDetails&playlistId={id}&maxResults={max_results}'.format(**fdict(api_key=YOUTUBE_API_KEY))
upload_url   = 'https://www.googleapis.com/youtube/v3/channels?key={api_key}&part=contentDetails&forUsername={username}&maxResults={max_results}'.format(**fdict(api_key=YOUTUBE_API_KEY))
video_url    = 'https://www.youtube.com/watch?v={}'

__doc__ = """
Usage: umph [-a|-m <num>] [-t <type>] <id>
       umph -h | --help

Options:
 -h, --help                           Print help and exit
 -t, --type=TYPE                      Set the type of feed to retrieve [default: p]
 -m, --max-results=MAX                Max number of results included [default: 50]
 -a, --all                            Get the entire feed

"""

def download_page(url):
    return requests.get(url).json()

def print_links(page):
    for entry in page['items']:
        print(video_url.format(entry['contentDetails']['videoId']))

def run_playlists(playlist_id, max_results, get_all):
    url = playlist_url.format(**fdict(id=playlist_id, max_results=max_results))
    page = download_page(url)
    print_links(page)
    next_page = page.get('nextPageToken')

    if get_all:
        while next_page:
            page = download_page(url + '&pageToken={}'.format(next_page))
            print_links(page)
            next_page = page.get('nextPageToken')

def run_username(username, max_results, get_all):
    url = upload_url.format(**fdict(username=username, max_results=max_results))
    page = download_page(url)
    items = page.get('items')
    assert len(items) == 1
    run_playlists(items[0]['contentDetails']['relatedPlaylists']['uploads'], max_results, get_all)
    
def main():
    args = docopt(__doc__)

    m = min(MAX_RESULT_LIMIT, int(args['--max-results']))

    if args['--type'] == 'p':
        run_playlists(args['<id>'], m, args['--all'])
    elif args['--type'] == 'u':
        run_username(args['<id>'], m, args['--all'])

if __name__ == '__main__':
    main()