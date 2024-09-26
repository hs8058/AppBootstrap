import requests
from flask import redirect, session, url_for, request, abort
from functools import wraps
from dotenv import load_dotenv
from jose import jwt  # PyJWT for decoding tokens
from cognitojwt import jwt_sync

import os

load_dotenv()





USER_POOL_NAME= os.getenv("USER_POOL_NAME")
COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
USER_POOL_ID=os.getenv("USER_POOL_ID")
COGNITO_REGION=os.getenv("COGNITO_REGION")
POST_LOGOUT_REDIRECT_URI=os.getenv("POST_LOGOUT_REDIRECT_URI")
TOKEN_URL = f"https://{COGNITO_DOMAIN}/oauth2/token"
AUTHORIZE_URL = f'https://{COGNITO_DOMAIN}/oauth2/authorize'
JWKS_URL = f'https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json'


    
def verify_jwt(token):
    payload=  jwt_sync.decode(token, COGNITO_REGION,USER_POOL_ID,CLIENT_ID)
    return payload
   
def oidc_logout():
    EndSessionUrl=f'https://{USER_POOL_NAME}.auth.{COGNITO_REGION}.amazoncognito.com/logout?client_id={CLIENT_ID}&logout_uri={POST_LOGOUT_REDIRECT_URI}&redirect_uri={POST_LOGOUT_REDIRECT_URI}&response_type=code';
    return redirect(EndSessionUrl)


def oidc_login():
    return redirect(f'{AUTHORIZE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}')

# Route to handle OIDC callback
def oidc_callback():
    code = request.args.get('code')
    if not code:
        abort(400)

    # Exchange the authorization code for tokens
    token_response = requests.post(TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }).json()

    id_token = token_response.get('id_token')
    if not id_token:
        abort(400, 'ID Token not provided')

    # Unpack and verify the ID token
    try:
        decoded_token = verify_jwt(id_token)
        # Store user info in the session
        session['user'] = {
            'name': decoded_token.get('cognito:username'),
            'email': decoded_token.get('email'),
            'sub': decoded_token.get('sub'),
             'phone_number': decoded_token.get('phone_number'),
        }
        return redirect(url_for('profile'))
    except Exception as e:
        abort(400, f'Error verifying token: {e}')


def check_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def decode_token(token):
    return jwt.decode(token,CLIENT_SECRET)  # Add verification using Cognito JWKS