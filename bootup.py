
import csv
import logging

from models import ZipCodeData

zip_code_data = {}


async def perform_bootup():
    logging.info("Performing bootup...")
    with open("zips (copy).csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            zip_code = row[0]
            city = row[1]
            state = row[2]
            state_code = row[3]
            county = row[4]
            latitude = float(row[5])
            longitude = float(row[6])
            zip_code_data[zip_code] = ZipCodeData(
                zip_code=zip_code,
                city=city,
                state=state,
                state_code=state_code,
                county=county,
                latitude=latitude,
                longitude=longitude,
            )


