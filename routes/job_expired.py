from flask import abort, redirect, render_template, request
from idli import VNN
import numpy as np

from db import Job
from web_utils import wrap

def handler(job_id):
    if not request.user:
        return redirect('/')
    
    job = Job.select(id=job_id).one()
    if not job:
        abort(404)
    
    similar_jobs = job.get_similar_jobs()
    return wrap(render_template('job_expired.html', job=job, similar_jobs=similar_jobs))