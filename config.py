import os

from dotenv import dotenv_values

_env = dotenv_values('.env')

DB_URI = _env['DB_URI']
ENV_TYPE = _env['ENV_TYPE']
FLASK_SECRET = _env['FLASK_SECRET']
GOOGLE_CX = _env.get('GOOGLE_CX')
GOOGLE_CX_API_KEY = _env.get('GOOGLE_CX_API_KEY')
JWT_SECRET = _env['JWT_SECRET']
OPENROUTER_API_KEY = _env['OPENROUTER_API_KEY']
LLM_API_KEY = _env['LLM_API_KEY']
LLM_API_MODEL = _env['LLM_API_MODEL']
LLM_API_URL = _env['LLM_API_URL']
S3_ACCESS_KEY = _env['S3_ACCESS_KEY']
S3_BUCKET = _env['S3_BUCKET']
S3_ENDPOINT = _env['S3_ENDPOINT']
S3_SECRET_KEY = _env['S3_SECRET_KEY']

if ENV_TYPE == 'dev':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
