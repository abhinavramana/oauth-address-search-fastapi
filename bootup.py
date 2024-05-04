
import csv
import logging

from models import ZipCodeData

ZIP_CODE_DATA = {}


async def perform_bootup():
    with open("zips.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            zip_code = row[0]
            city = row[1]
            state = row[2]
            state_code = row[3]
            county = row[4]
            latitude = float(row[5])
            longitude = float(row[6])
            ZIP_CODE_DATA[zip_code] = ZipCodeData(
                zip_code=zip_code,
                city=city,
                state=state,
                state_code=state_code,
                county=county,
                latitude=latitude,
                longitude=longitude,
            )


