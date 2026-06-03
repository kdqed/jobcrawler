from flask import request

import loc_utils


def handler():
    tag = request.args.get('tag', '')
    return loc_utils.autocomplete(tag)