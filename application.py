import httpx

from bootup import ZIP_CODE_DATA, perform_bootup, ZIP_CODE_TO_CITY_MAP
from typing import List
import logging
from rapidfuzz import process, fuzz
from config import ZIP_CSV_FILE, NUM_CITY_MATCHES, AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET
from logging_configuration import add_json_config_to_logger
from models import SortedCityMatch, ZipCodeData, LoginData
from jose import jwt
from fastapi import FastAPI, Depends, HTTPException
import requests
from oauth_config import get_current_user, get_token, CurrentUser

app = FastAPI()

logger = logging.getLogger("uvicorn")
add_json_config_to_logger(logger)

logger.info("API ready to serve requests...")


@app.on_event("startup")
async def startup_event():
    logger.info("Performing bootup...")
    await perform_bootup(ZIP_CSV_FILE)


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


@app.post("/token")
async def login(form_data: LoginData) -> str:
    try:
        token = await get_token(form_data.username, form_data.password)
    except httpx.HTTPStatusError as e:
        logger.error(f"Error getting token: {e.response.text}", exc_info=True)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json().get("error_description", e.response.text)
        )
    return token





@app.get("/zip/{zip_code}")
async def get_zip_code_data(zip_code: int, current_user: CurrentUser = Depends(get_current_user)):
    logger.info(f"User {current_user.username} with email: {current_user.email} requested data for zip code {zip_code}")
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


@app.get("/")
async def homepage():
    return {"docs": "https://budidamatrixinc.ngrok-free.app/docs"}
