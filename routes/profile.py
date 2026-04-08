from flask import abort, render_template, request

from db import UserResume
from web_utils import wrap


def handler():
    if not request.user:
        return abort(401)
    
    user_resume = UserResume.select(id=request.user.id).one()
    
    return wrap(render_template('profile.html', resume=user_resume))
    