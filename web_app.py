import importlib

from flask import Flask, request
from flask_wtf.csrf import CSRFProtect

from clients import client_map
import config
from db import ClientUser

app = Flask(__name__)
app.config['SECRET_KEY'] = config.FLASK_SECRET

CSRFProtect(app)

@app.before_request
def before_request():
    request.client = client_map[request.host]
    request.user = ClientUser.get_by_jwt(
        request.cookies.get('auth'),
        request.client.code,
    )

ROUTE_MAP = {
    '/': 'home',
    '/login': 'login',
    '/google-login-start': 'google_login_start',
    '/google-login-callback': 'google_login_callback',
    '/profile': 'profile',
    '/logout': 'logout',
    '/upload-resume': 'upload_resume',
}

for path, module_name in ROUTE_MAP.items():
    route_module = importlib.import_module(f"routes.{module_name}")
    app.add_url_rule(
        path,
        endpoint = module_name,
        view_func = route_module.handler, 
        methods = getattr(route_module, 'METHODS', ['GET']),
    )

    
if __name__ == "__main__":
    app.run(debug=True, port=4071)