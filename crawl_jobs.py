from datetime import datetime
import logging
import sys
import time
import traceback

import niquests

from db import JobUrl, Job
import ml_utils
from parsers import parsers


logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workdir/log_jobs.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)


while True:
    job_url = JobUrl.select(crawled_at=None).order_by('discovered_at').one()
    logging.info(f'Crawling {job_url.url}')

    error = None
    for i in range(1):
        try:
            time.sleep(1)
            response = niquests.get(job_url.url, headers={'User-Agent': 'googlebot'})
    
            if job_url.url == response.url:
                result = parsers[job_url.src].parse_job(job_url.url, response.content)
                result['match_vec'] = ml_utils.vectorize(result['title'], result['description'])
                Job.add(
                    url = job_url.url,
                    src = job_url.src,
                    details = result,
                )
            else:
                logging.info("redirected: " + response.url)
            break
        except Exception as e:
            error = str(e)
            logging.error(traceback.format_exc())
    if error:
        job_url.crawl_error = error

    job_url.crawled_at = datetime.now()
    job_url.save()
    
    
    
