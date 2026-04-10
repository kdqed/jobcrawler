from datetime import datetime
from pathlib import Path

from flask import abort, request, redirect
from markitdown import MarkItDown
from werkzeug.utils import secure_filename

from db import UserResume
import ml_utils

METHODS = ['POST']

resume_dir = Path('workdir') / 'resumes'

def handler():
    if not request.user:
        return abort(401)
    
    resume_file = request.files.get('resume')
    if not resume_file:
        return abort(500)
    
    resume = UserResume.select(id=request.user.id).one()
    if resume:
        Path(resume_dir / resume.filename).unlink(missing_ok=True)
    else:
        resume = UserResume(id=request.user.id)
        
    sanitized_filename = secure_filename(resume_file.filename).replace('/', '_')
    resume.filename = f'{request.user.id}-{sanitized_filename}'
    resume_file.save(resume_dir / resume.filename)
    
    md = MarkItDown(enable_plugins=True)
    resume_text = md.convert(resume_dir / resume.filename).text_content
    resume.pplx_vec = ml_utils.vectorize(resume_text)
    resume.updated = datetime.now()
    
    resume.save()
        
    return redirect('/profile')
    