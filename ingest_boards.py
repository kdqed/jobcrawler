import sys

from db import Board

urls = list(map(lambda x: x.strip('\n'), open(sys.argv[1]).readlines()))

initial = Board.count()

for url in urls:
    clean_url, src = None, None
    
    if url.startswith("https://jobs.lever.co"):
        clean_url = '/'.join(url.split('/')[:4]).split("?")[0]
        src = 'lever'
    elif url.startswith("https://boards.greenhouse.io"):
        clean_url = '/'.join(url.split('/')[:4]).split("?")[0].lower()
        clean_url = clean_url.replace("https://boards.", "https://job-boards.")
        src = 'greenhouse'
    elif url.startswith("https://job-boards.greenhouse.io"):
        clean_url = '/'.join(url.split('/')[:4]).split("?")[0].lower()
        src = 'greenhouse'
    elif url.startswith("https://jobs.ashbyhq.com"):
        clean_url = '/'.join(url.split('/')[:4]).split("?")[0].lower()
        src = 'ashby'

    if clean_url and src:
        print(src, clean_url)
        Board.add(url=clean_url, src=src)


print(f"{initial} -> {Board.count()}")
