from pathlib import Path

from flask import request, send_file

from db import UserResume

resume_dir = Path('workdir') / 'resumes'

def handler():
    if not request.user:
        return "No user logged in", 401
    
    resume = UserResume.select(id=request.user.id).one()
    if not resume:
        return "User resume not found", 404
    
    return send_file(resume_dir / resume.filename)