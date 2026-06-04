from datetime import datetime
import logging
import sys
import time
import traceback

import niquests

from db import JobUrl, Job, JobLoc
import loc_utils
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
    job_url = JobUrl.select(
        crawled_at = None, 
        src = sys.argv[1]
    ).order_by('discovered_at').one()

    if not job_url:
        logging.info('Nothing to crawl, sleeping')
        time.sleep(3600)
    logging.info(f'Crawling {job_url.url}')

    error = None
    for i in range(1):
        try:
            time.sleep(1)
            response = niquests.get(job_url.url, headers={'User-Agent': 'xwbot'})
    
            if job_url.url == response.url:
                result = parsers[job_url.src].parse_job(job_url.url, response.content)
                result['pplx_vec'] = ml_utils.vectorize(result['title'], result['description'])
                Job.add(
                    url = job_url.url,
                    src = job_url.src,
                    details = result,
                )
                job = Job.select(url = job_url.url).one()
                loc_tags = loc_utils.get_location_tags(job.loc_json)
                for loc_tag in loc_tags:
                    JobLoc.add_tag(job.id, loc_tag)
                
                job.upload_org_logo_to_cdn()
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
    
    if '--one' in sys.argv:
        break
  
    
