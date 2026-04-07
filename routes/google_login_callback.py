from datetime import datetime, timedelta

from flask import abort, make_response, redirect, request, session
from googleapiclient.discovery import build as google_build
from google.auth.transport import requests as google_requests
import google.oauth2.credentials
import google_auth_oauthlib.flow

from db import ClientUser
import config


def handler():
    state = request.args.get("state", "")
    if state != session["state"]:
        return abort(401)
        
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'google_oauth_client.json',
        scopes = None,
        state = state,
    )
    flow.code_verifier = session.get("code_verifier")
    flow.redirect_uri = request.host_url + "google-login-callback"
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    user_info_service = google_build("oauth2", "v2", credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()
    
    user = ClientUser.get_by_email(user_info['email'], request.client.code)
    if not user:
        return "User Not Found", 404
    
    resp = make_response(redirect(session.get("page", "/")))
    resp.set_cookie(
        "auth",
        value = user.generate_jwt(),
        httponly = True,
        expires=datetime.now() + timedelta(days=14),
    )
    return resp