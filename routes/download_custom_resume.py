from datetime import datetime
from pathlib import Path

from flask import redirect, render_template, request
import plutoprint

from db import UserJob
import storage_utils


def generate_pdf(html_content, output_file):
    book = plutoprint.Book(plutoprint.PAGE_SIZE_A4)
    book.load_html(html_content)
    book.write_to_pdf(output_file)


def handler(job_id):
    if not request.user:
        return "User not logged in", 403
    
    user_job = UserJob.get_for_pair(request.user.id, job_id)
    if not user_job:
        return "Custom resume not found"
    if not user_job.cr_markdown_content:
        return "Custom resume not found"

    should_generate_pdf = False
    
    pdf_path = Path('workdir') / 'custom-resumes' / f'{user_job.id}.pdf'
    pdf_exists = storage_utils.key_exists(user_job.cr_pdf_key)
    if pdf_exists:
        pdf_last_mod = storage_utils.get_last_mod(user_job.cr_pdf_key)
        print(user_job.cr_generated_at, pdf_last_mod)
        if user_job.cr_generated_at > pdf_last_mod:
            should_generate_pdf = True
    else:
        should_generate_pdf = True
    
    if should_generate_pdf:
        generate_pdf(
            render_template(
                'resume_pdf.html', 
                html_content = user_job.cr_html_content
            ),
            pdf_path
        )
        storage_utils.upload_custom_resume(pdf_path, f'{user_job.id}.pdf')
        pdf_path.unlink()

    return redirect(storage_utils.get_temp_access_url(user_job.cr_pdf_key))