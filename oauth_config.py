from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from okta_jwt.jwt import validate_token

from config import OKTA_ISSUER, OKTA_AUDIENCE, CLIENT_ID

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(OAUTH2_SCHEME)):
    try:
        claims = validate_token(token, OKTA_ISSUER, OKTA_AUDIENCE, [CLIENT_ID])
        username = claims.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))