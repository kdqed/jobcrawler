import os

from dotenv import dotenv_values

_env = dotenv_values('.env')

DB_URI = _env['DB_URI']
ENV_TYPE = _env['ENV_TYPE']
FLASK_SECRET = _env['FLASK_SECRET']
JWT_SECRET = _env['JWT_SECRET']
OPENROUTER_API_KEY = _env['OPENROUTER_API_KEY']

if ENV_TYPE == 'dev':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
