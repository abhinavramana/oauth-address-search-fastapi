from bootup import ZIP_CODE_DATA, perform_bootup, TRIE, ZIP_CODE_TO_CITY_MAP
from typing import List
import logging
from rapidfuzz import process, fuzz
from config import ZIP_CSV_FILE, NUM_CITY_MATCHES
from logging_configuration import add_json_config_to_logger
from models import SortedCityMatch, ZipCodeData
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from okta_jwt.jwt import validate_token
from okta_jwt.jwt import generate_token


app = FastAPI()

logger = logging.getLogger("uvicorn")
add_json_config_to_logger(logger)

logger.info("API ready to serve requests...")


@app.on_event("startup")
async def startup_event():
    logger.info("Performing bootup...")
    await perform_bootup(ZIP_CSV_FILE)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

OKTA_ISSUER = "https://dev-hqlhngnge6hgtx5t.us.auth0.com/oauth2/default"  # Replace with your Okta domain
OKTA_AUDIENCE = "https://dev-hqlhngnge6hgtx5t.us.auth0.com/api/v2/" # api://default"  # Replace with your Okta audience if different
CLIENT_ID = "DpV7Bgqblt7B3ahwMWZWlsbqr5ashQ8N"
CLIENT_SECRET = "jevIA2CHAZrFv1jnD1jnhAjsq2BmFgpjeXl0cOzIgMxBDvBuz4DJeeABGIZ4ogSE"
AUDIENCE = "https://dev-hqlhngnge6hgtx5t.us.auth0.com/api/v2/"


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        claims = validate_token(token, OKTA_ISSUER, OKTA_AUDIENCE, [CLIENT_ID])
        username = claims.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))



@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        token = generate_token(OKTA_ISSUER, CLIENT_ID, CLIENT_SECRET,
            form_data.username,
            form_data.password,
        )
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    if "authorization" in request.headers:
        token = request.headers["authorization"].split(" ")[1]
        try:
            claims = jwt.decode(token, options={"verify_signature": False})
            username = claims.get("sub")
            email = claims.get("email")
            log_data = {
                "message": f"Request: {request.method} {request.url}",
                "level": "INFO",
                "username": username,
                "email": email,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code
            }
            logger.info(log_data)
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
    else:
        log_data = {
            "message": f"Request: {request.method} {request.url}",
            "level": "INFO",
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code
        }
        logger.info(log_data)
    return response

@app.get("/zip/{zip_code}")
async def get_zip_code_data(zip_code: str, current_user: str = Depends(get_current_user)):
    if zip_code in ZIP_CODE_DATA:
        return ZIP_CODE_DATA[zip_code]
    else:
        return {"message": "Zip code not found"}


@app.post("/match", response_model=List[ZipCodeData])
async def match_city(sorted_city: SortedCityMatch):
    # Perform fuzzy search on city names
    results = process.extract(sorted_city.city, ZIP_CODE_TO_CITY_MAP, scorer=fuzz.WRatio, limit=NUM_CITY_MATCHES)
    matched_zips = []
    # Map results back to zip codes and retrieve full data
    for city, score, zip_code in results:
        full_city = ZIP_CODE_DATA[zip_code]
        temp_dict_to_not_modify_original = full_city.dict()
        temp_dict_to_not_modify_original["score"] = score
        matched_zips.append(ZipCodeData(**temp_dict_to_not_modify_original))
    return matched_zips
