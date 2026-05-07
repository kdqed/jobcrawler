from flask import render_template, request
from idli import VNN

from db import Job, UserResume
from web_utils import wrap


def handler():
    if not request.user:
        return wrap(render_template('home.html'))
  
    resume = UserResume.select(id=request.user.id).one()
    if resume:
        vec = resume.pplx_vec.tolist()
        jobs = list(Job.select().order_by(VNN.cos('pplx_vec', vec))[:50])
        for job in jobs:
            user_score = (job.pplx_vec__vd__cos/2) ** 2
            job.match_score = round(100*(1-user_score))
        return wrap(render_template('home.html', jobs=jobs, customized=True))
    else:
        jobs = Job.select().order_by('-date_posted')[:50]
        return wrap(render_template('home.html', jobs=jobs, customized=False))