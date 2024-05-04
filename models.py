from pydantic import BaseModel


class ZipCodeData(BaseModel):
    zip_code: str
    city: str
    state: str
    state_code: str
    county: str
    latitude: float
    longitude: float


class MatchedZipCode(ZipCodeData):
    score: int
