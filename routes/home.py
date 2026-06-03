from datetime import datetime, timedelta

from flask import render_template, request
from idli import VNN

from db import Job, JobLoc, UserResume
import loc_utils
from web_utils import wrap


def handler():
    if not request.user:
        return wrap(render_template('home.html'))
    
    weeks = int(request.args.get('freshness', '2'))
    newer_than = datetime.now() - timedelta(days = weeks * 7)
    location_tag = request.args.get('location_tag', 'us')
    location_name = loc_utils.get_name_by_tag(location_tag)
    
    filters = dict(
        date_posted__gte = newer_than,
        __by_join = [
            (JobLoc, 'job_id', 'id', dict(loc_tag = location_tag))
        ]
    )
    
    resume = UserResume.select(id=request.user.id).one()
    if resume:
        vec = resume.pplx_vec.tolist()
        jobs = list(Job.select(**filters).only(
            'id', 'title', 'org_logo', 'org_name', 
            'loc_json', 'date_posted',
        ).order_by(VNN.cos('pplx_vec', vec))[:50])
        
        for job in jobs:
            user_score = (job.pplx_vec__vd__cos/2) ** 2
            job.match_score = round(100*(1-user_score))
        return wrap(render_template('home.html',
            jobs = jobs, 
            customized = True,
            freshness = weeks,
            location_tag = location_tag,
            location_name = location_name,
        ))
    else:
        jobs = Job.select(**filters).only(
            'id', 'title', 'org_logo', 'org_name', 'loc_json', 'date_posted'
        ).order_by('-date_posted')[:50]
        return wrap(render_template('home.html',
            jobs = jobs,
            customized = False,
            freshness = weeks,
            location_tag = location_tag,
            location_name = location_name,
        ))