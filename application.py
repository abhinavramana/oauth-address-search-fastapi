from bootup import ZIP_CODE_DATA, perform_bootup, ZIP_CODE_TO_CITY_MAP
from typing import List
import logging
from rapidfuzz import process, fuzz
from config import ZIP_CSV_FILE, NUM_CITY_MATCHES, AUTH0_DOMAIN, AUTH0_AUDIENCE, CLIENT_SECRET, CLIENT_ID
from logging_configuration import add_json_config_to_logger
from models import SortedCityMatch, ZipCodeData, LoginData
from jose import jwt
from fastapi import FastAPI, Depends, HTTPException
import requests
from oauth_config import get_current_user

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
async def login(form_data: LoginData):
    try:
        token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
        payload = {
            "grant_type": "password",
            "username": form_data.username,
            "password": form_data.password,
            "audience": AUTH0_AUDIENCE,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = requests.post(token_url, data=payload, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data["access_token"]
        return {"access_token": access_token, "token_type": "bearer"}
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error generating token: {str(e)}", exc_info=True)
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


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


@app.get("/")
async def homepage():
    return {"docs": "https://budidamatrixinc.ngrok-free.app/docs"}
