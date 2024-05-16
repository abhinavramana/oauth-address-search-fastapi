from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from config import CLIENT_SECRET, AUTH0_AUDIENCE, AUTH0_ISSUER

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(OAUTH2_SCHEME)):
    try:
        claims = jwt.decode(token, CLIENT_SECRET, audience=AUTH0_AUDIENCE, issuer=AUTH0_ISSUER)
        username = claims.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
