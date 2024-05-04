from bootup import zip_code_data # Ensures bootup is the first thing to happen
from fastapi import FastAPI
from typing import List
import logging

from models import MatchedZipCode

logging.info("Starting FastAPI...")
app = FastAPI()
logging.info("API ready to serve requests...")

@app.get("/zip/{zip_code}")
async def get_zip_code_data(zip_code: str):
    if zip_code in zip_code_data:
        return zip_code_data[zip_code]
    else:
        return {"message": "Zip code not found"}


@app.post("/match", response_model=List[MatchedZipCode])
async def match_city(city: str):
    return []