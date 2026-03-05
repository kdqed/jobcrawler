from dotenv import dotenv_values

_ENV = dotenv_values('.env')

DB_URI = _ENV['DB_URI']
