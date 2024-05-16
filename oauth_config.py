from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from authlib.jose import JsonWebToken
from authlib.jose.errors import JoseError
import httpx

from config import OKTA_JWKS_URI, OKTA_ISSUER, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN

TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"


class CurrentUser(BaseModel):
    username: str
    email: str


security = HTTPBearer()


async def get_okta_public_keys():
    async with httpx.AsyncClient() as client:
        response = await client.get(OKTA_JWKS_URI)
        response.raise_for_status()
        jwks = response.json()
        return jwks


async def decode_jwt(token: str) -> Dict[str, Any]:
    """Decode the JWT token and validate it"""
    keys = await get_okta_public_keys()
    jwt = JsonWebToken(["RS256"])
    try:
        claims = jwt.decode(token, keys)
        jwt.validate_claims(claims, {
            'iss': OKTA_ISSUER,
            'aud': AUTH0_CLIENT_ID,
        })
    except JoseError as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")
    return claims


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> CurrentUser:
    token = credentials.credentials
    claims = await decode_jwt(token)
    return CurrentUser(username=claims.get("sub"), email=claims.get("email"))


async def get_token(username: str, password: str) -> str:
    """Get a bearer token from Okta using username and password."""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'scope': 'openid profile email'  # Specify the scopes you need
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()["access_token"]
