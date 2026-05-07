from flask import abort, redirect, render_template, request
from idli import VNN
import numpy as np

from db import Job, UserResume
from web_utils import wrap


def pg_cosine_distance(v1, v2):
    # 1. Force 32-bit precision to match Postgres 'real' type
    a = np.asarray(v1, dtype=np.float32)
    b = np.asarray(v2, dtype=np.float32)

    # 2. Calculate dot product and norms separately
    # This mirrors pgvector's internal C implementation
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    # 3. Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 1.0 # Or NaN, depending on your Postgres version's behavior

    # 4. Result is exactly 1 - similarity
    similarity = dot / (norm_a * norm_b)
    
    # Clip to avoid float precision overflow (e.g., 1.0000001)
    return np.float32(1.0) - np.clip(similarity, -1.0, 1.0)
  

def handler(job_id):
    if not request.user:
        return redirect('/')
    
    job = Job.select(id=job_id).one()
    if not job:
        abort(404)
    
    resume = UserResume.select(id=request.user.id).one()
    if resume:
        cos_sim = pg_cosine_distance(job.pplx_vec, resume.pplx_vec)
        user_score = (cos_sim/2) ** 2
        job.match_score = round(100*(1-user_score))
    return wrap(render_template('job_page.html', job=job, similar_jobs=[]))