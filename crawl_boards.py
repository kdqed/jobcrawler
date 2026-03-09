from datetime import datetime
import logging
import sys
import time

import niquests

from db import Board, JobUrl
from parsers import parsers


logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workdir/log_boards.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)


while True:
    board = Board.select(src=sys.argv[1]).order_by('last_crawled').one()
    
    logging.info(f'Crawling {board.url}')
    response = niquests.get(board.url, headers={'User-Agent': 'googlebot'})
    
    if board.url == response.url:
        job_urls = parsers[board.src].parse_board(board.url, response.content)
        logging.info(f'Got {len(job_urls)} Job URLs')
        
        for job_url in job_urls:
            JobUrl.add(job_url, board.src)
    else:
        board.redirect_url = response.url
        logging.info(f'Redirected to {response.url}')
        
    board.last_crawled = datetime.now()
    board.save()
    time.sleep(1)
    
    
