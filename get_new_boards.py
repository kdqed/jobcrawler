# WIP
# Use Browser Extension For Now

from datetime import datetime, timedelta
import sys
import time

import niquests

import config
from db import Board


def google_search(q, start=1):
    print(start, q)
    response = niquests.get(
        'https://www.googleapis.com/customsearch/v1',
        params = dict(
            q = q,
            key = config.GOOGLE_CX_API_KEY,
            cx = config.GOOGLE_CX,
            start = start
        )
    )
    
    print(response.text, response.status_code)
    
    results = response.json()
    urls = [i['url'] for i in results.get('items', [])]
    return urls

src = sys.argv[1]
before = datetime(*map(int, sys.argv[2].split('-')))
after = before - timedelta(days=1)
before, after = before.strftime("%Y-%m-%d"), after.strftime("%Y-%m-%d")
query = ''

if src == 'lever':
    query = f'site:jobs.lever.co after:{after} before:{before} -site:jobs.lever.co/jobgether'

results = google_search(query)
for url in results:
    print(url)


