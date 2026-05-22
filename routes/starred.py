from flask import abort, redirect, render_template, request

from db import Job, UserJob
from web_utils import wrap
  

def handler():
    if not request.user:
        return redirect('/')
    
    jobs = []   
    return wrap(render_template('starred.html', 
        jobs = jobs, 
    ))