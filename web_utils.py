from flask import render_template


def wrap(content, title="Job Search", desciption="Upload resume, find jobs"):
    return render_template('_shell.html', content=content)