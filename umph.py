#!/usr/bin/python3

import bs4
import requests
from docopt import docopt

class fdict(dict):
    def __missing__(self, key):
        return '{%s}' % key

MAX_RESULT_LIMIT = 50

playlist_url = 'https://gdata.youtube.com/feeds/api/playlists/{id}?v=2&start-index={start_index}&strict=true'
upload_url   = 'https://gdata.youtube.com/feeds/api/users/{username}/uploads?v=2&start-index={start_index}&strict=true'

__doc__ = """
Usage: umph [-a|-m <num>] [-t <type>] [-s <num>] <id>
       umph -h | --help

Options:
 -h, --help                           Print help and exit
 -t, --type=TYPE                      Get feed type [default: p]
 -s, --start-index=START              Index of first matching result [default: 1]
 -m, --max-results=MAX                Max number of results included [default: 25]
 -a, --all                            Get the entire feed

"""
                
def main():
    args = docopt(__doc__)

    if args['--type'] == 'p':
        feed_url = playlist_url.format(**fdict(id=args['<id>']))
    elif args['--type'] == 'u':
        feed_url = upload_url.format(**fdict(username=args['<id>']))
        
    m = int(MAX_RESULT_LIMIT if args['--all'] else args['--max-results'])
    feed_url += '&max-results=%d' % m
    si = int(args['--start-index'])

    results = []
    while True:
        url = feed_url.format(**fdict(start_index=si))
        r = requests.get(url)
        x = bs4.BeautifulSoup(r.text)
        entries = x.find_all('entry')
        for entry in entries:
            results.append(entry.find('link').get('href'))
        if not entries or not args['--all']:
            break
        si += m

    print('\n'.join(results))

if __name__ == '__main__':
    main()