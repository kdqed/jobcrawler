from flask import abort, redirect, render_template, request

from db import CreditUseLog
from web_utils import wrap


def handler():
    if not request.user:
        return redirect('/')
    
    use_log = CreditUseLog.select(
        user_id = request.user.id,
    ).only(
        'timestamp', 'credits', 'note',
    ).order_by(
        '-timestamp'
    )
    
    return wrap(render_template('credit_use_log.html', 
        use_log = list(use_log),
    ))