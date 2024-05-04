
import csv
import logging
from models import ZipCodeData

ZIP_CODE_DATA = {}

logger = logging.getLogger(__name__)


def process_record(row):
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


async def perform_bootup(filename:str):
    with open(filename, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            # NOTE: the last row in the CSV file is invalid and just has 1 column, which is invalid
            try:
                process_record(row)
            except Exception as e:
                logger.error(f"Ignoring processing invalid row {row} due to {e}", exc_info=True)


