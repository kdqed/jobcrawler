import argparse

from idli import VNN
from markitdown import MarkItDown

from db import Job
import ml_utils


parser = argparse.ArgumentParser()
parser.add_argument('-t', '--text')
parser.add_argument('-f', '--filepath')

args = parser.parse_args()


text = ''
if args.text:
  text = args.text
elif args.filepath:
  md = MarkItDown(enable_plugins=True)
  text = md.convert(args.filepath).text_content
  

text_vector = ml_utils.vectorize(text)

jobs = Job.select().order_by(VNN.cos('match_vec', text_vector))[:10]
for job in jobs:
    print(job.title, job.url)
