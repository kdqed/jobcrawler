from flask import redirect, request, session

from googleapiclient.discovery import build as google_build
from google.auth.transport import requests as google_requests
import google.oauth2.credentials
import google_auth_oauthlib.flow

import config


def handler():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'google_oauth_client.json',
        scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
    )

    host_url = request.host_url
    flow.redirect_uri = host_url + "google-login-callback"
    authorization_url, state = flow.authorization_url(
        access_type = "offline", 
        include_granted_scoped = "true"
    )

    session["state"] = state
    session["page"] = request.args.get("page", "/")
    session["code_verifier"] = flow.code_verifier
    return redirect(authorization_url)