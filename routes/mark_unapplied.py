from datetime import datetime

from flask import abort, redirect, render_template, request

from db import Job, UserJob
from web_utils import wrap
  
METHODS = ['POST']

def handler(job_id):
    if not request.user:
        return redirect('/')
    
    job = Job.select(id=job_id).one()
    if not job:
        return "Job Not Found", 404
    
    user_job = UserJob.get_for_pair(request.user.id, job.id)
    user_job.applied_at = None
    user_job.save()
    
    return redirect(f'/job/{job.id}')