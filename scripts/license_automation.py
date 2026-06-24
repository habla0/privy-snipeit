import os, csv
import request_helper as rq
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataPath = os.path.join(BASE_DIR, "data", "Dummy data_license.csv")


def _normaliseName(value):
    return str(value or "").strip().lower()


with open(dataPath, 'r') as datafile:
    csvreader = csv.reader(datafile)
    header = next(csvreader)

    for row in csvreader:
        licenses = rq.getData('licenses', forceRefresh=True).json().get('rows', [])
        existing_names = {_normaliseName(license.get('name')) for license in licenses if license.get('name')}
        target_name = _normaliseName(row[0])

        if target_name not in existing_names:
            print(f"License {row[0]} not in Snipe-IT, creating model.")

            newLicenseData = {
                "name": row[0].strip(),
                "seats": row[1],
                "category_id": row[2]
            }
            rq.postData('licenses', newLicenseData, invalidateAfter=['licenses'])
            
            licenses = rq.getData('licenses', forceRefresh=True).json().get('rows', [])
            existing_names = {_normaliseName(license.get('name')) for license in licenses if license.get('name')}
        else:
            print(f"License {row[0]} in Snipe-IT, skipping. Please update in Snipe-IT.\n")

            continue

