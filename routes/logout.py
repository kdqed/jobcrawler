from flask import make_response, redirect


def handler():
    response = make_response(redirect('/'))
    response.set_cookie("auth", value = '', httponly = True)
    return response