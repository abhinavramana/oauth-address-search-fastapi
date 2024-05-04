from bootup import ZIP_CODE_DATA, perform_bootup, TRIE
from fastapi import FastAPI
from typing import List
import logging

from config import ZIP_CSV_FILE, NUM_CITY_MATCHES
from models import MatchedZipCode, SortedCityMatch
from trie_node import search_trie

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


@app.post("/match", response_model=List[MatchedZipCode])
async def match_city(sorted_city: SortedCityMatch):
    matched_zip_codes = search_trie(TRIE, sorted_city.city)
    matched_zip_codes.sort(key=lambda x: x.score)
    return matched_zip_codes[:NUM_CITY_MATCHES]
