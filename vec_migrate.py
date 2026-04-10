from db import Job
import ml_utils


print(Job.count())
i = 0
for job in Job.select():
    job.pplx_vec = ml_utils.vectorize(job.title, job.description)
    job.save()
    i += 1
    print(i)    