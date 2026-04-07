from flask import render_template

from web_utils import wrap


def handler():
    return wrap(render_template('home.html'))