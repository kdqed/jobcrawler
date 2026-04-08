from flask import render_template, request
from idli import VNN

from db import Job, UserResume
from web_utils import wrap


def handler():
    if not request.user:
        return wrap(render_template('home.html'))
  
    resume = UserResume.select(id=request.user.id).one()
    print(resume.match_vec, type(resume.match_vec))
    vec = resume.match_vec.tolist()
    if resume:
        jobs = Job.select().order_by(VNN.cos('match_vec', vec))[:50]
        return wrap(render_template('home.html', jobs=jobs, customized=True))
    else:
        jobs = Job.select().order_by('-date_posted')[:50]
        return wrap(render_template('home.html', jobs=jobs, customized=False))