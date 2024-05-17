from pydantic import BaseModel


class LoginData(BaseModel):
    username: str
    password: str


class ZipCodeData(BaseModel):
    zip_code: int
    city: str
    state: str
    state_code: str
    county: str
    latitude: float
    longitude: float
    score: float = 0.0  # Default score for the exact match case


class SortedCityMatch(BaseModel):
    city: str
