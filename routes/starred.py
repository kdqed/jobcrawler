from flask import abort, redirect, render_template, request

from db import Job, UserJob
from web_utils import wrap
  

def handler():
    if not request.user:
        return redirect('/')
    
    jobs = Job.select(__by_join = [
        (UserJob, 'job_id', 'id', dict(
            user_id = request.user.id,
            starred_at__neq = None,
        ))
    ]).only(
        'id', 'title', 'org_logo', 'org_name', 'loc_locality', 'date_posted'
    )[:50]

    return wrap(render_template('starred.html', 
        jobs = jobs,
    ))