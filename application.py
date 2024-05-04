from bootup import ZIP_CODE_DATA, perform_bootup, TRIE, ZIP_CODE_TO_CITY_MAP
from fastapi import FastAPI
from typing import List
import logging
from rapidfuzz import process, fuzz
from config import ZIP_CSV_FILE, NUM_CITY_MATCHES
from models import SortedCityMatch, ZipCodeData


app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

logger.info("API ready to serve requests...")


@app.on_event("startup")
async def startup_event():
    logger.info("Performing bootup...")
    await perform_bootup(ZIP_CSV_FILE)


@app.get("/zip/{zip_code}")
async def get_zip_code_data(zip_code: str):
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
