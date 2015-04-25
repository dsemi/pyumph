#!/usr/bin/python3

import requests
from docopt import docopt
from queue import Queue
from threading import Thread

class fdict(dict):
    def __missing__(self, key):
        return '{%s}' % key

MAX_RESULT_LIMIT = 50

playlist_url = 'https://gdata.youtube.com/feeds/api/playlists/{id}?v=2&alt=json&start-index={start_index}&max-results={max_results}&strict=true'
upload_url   = 'https://gdata.youtube.com/feeds/api/users/{username}/uploads?v=2&alt=json&start-index={start_index}&max-results={max_results}&strict=true'

__doc__ = """
Usage: umph [-a|-m <num>] [-t <type>] [-s <num>] <id>
       umph -h | --help

Options:
 -h, --help                           Print help and exit
 -t, --type=TYPE                      Set the type of feed to retrieve [default: p]
 -s, --start-index=START              Index of first matching result [default: 1]
 -m, --max-results=MAX                Max number of results included [default: 50]
 -a, --all                            Get the entire feed

"""

def download_page(url):
    return requests.get(url).json()

def print_links(page):
    for entry in page['feed']['entry']:
        print(entry['link'][0]['href'])

class Downloader(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url = self.queue.get()
            print_links(download_page(url))
            self.queue.task_done()

def main():
    args = docopt(__doc__)

    start_index = int(args['--start-index'])
    m = min(MAX_RESULT_LIMIT, int(args['--max-results']))

    if args['--type'] == 'p':
        feed_url = playlist_url.format(**fdict(id=args['<id>']))
    elif args['--type'] == 'u':
        feed_url = upload_url.format(**fdict(username=args['<id>']))

    url = feed_url.format(**fdict(start_index=start_index, max_results=m))
    page = download_page(url)
    print_links(page)
    total_results = page['feed']['openSearch$totalResults']['$t']
    if not args['--all']:
        total_results = min(total_results, int(args['--max-results']))
    start_index += m

    if start_index <= total_results:
        queue = Queue()

        for _ in range(4):
            worker = Downloader(queue)
            worker.daemon = True
            worker.start()

        for i in range(start_index, total_results+1, m):
            queue.put(feed_url.format(**fdict(start_index=i, max_results=min(total_results-i+1, m))))

        queue.join()

if __name__ == '__main__':
    main()