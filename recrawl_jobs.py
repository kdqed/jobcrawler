import sys

import niquests

from db import Job
from parsers import parsers

src = sys.argv[1]
parse_job = parsers[src].parse_job


for job in Job.select(src=src):
    print(job.url)
    response = niquests.get(job.url, headers={'User-Agent': 'xwbot'})
    if response.status_code == 200:
        print("Exists")
        result = parse_job(job.url, response.content)
        job.loc_json = result['loc_json']
        job.save()
    elif response.status_code == 404:
        print("404")
        job.archive()
    else:
        raise Excaption("Status " + str(response.status_code))
    print()
    