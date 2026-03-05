import argparse

from idli import VNN

from db import Job
import ml_utils


parser = argparse.ArgumentParser()
parser.add_argument('-t', '--text')

args = parser.parse_args()

text = args.text
text_vector = ml_utils.vectorize(text)

jobs = Job.select().order_by(VNN.cos('match_vec', text_vector))[:10]
for job in jobs:
    print(job.title, job.url)
