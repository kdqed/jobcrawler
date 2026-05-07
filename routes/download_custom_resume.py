from datetime import datetime
from pathlib import Path

from flask import request, render_template, send_file
import plutoprint

from db import CustomizedResume

def generate_pdf(html_content, output_file):
    book = plutoprint.Book(plutoprint.PAGE_SIZE_A4)
    book.load_html(html_content)
    book.write_to_pdf(output_file)


def handler(job_id):
    if not request.user:
        return "User not logged in", 403
    
    resume = CustomizedResume.select(
        user_id = request.user.id,
        job_id = job_id,
    ).one()

    if not resume:
        return "Custom resume not found"

    pdf_path = Path('workdir') / 'custom-resumes' / f'{resume.id}.pdf'
    
    if any([
        resume.updated > resume.pdf_timestamp,
        not pdf_path.exists()
    ]):
        generate_pdf(
            render_template('resume_pdf.html', resume=resume),
            pdf_path
        )
        resume.pdf_timestamp = datetime.now()
        resume.save()

    return send_file(pdf_path)