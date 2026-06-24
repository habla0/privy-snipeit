import os, csv
import request_helper as rq
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataPath = os.path.join(BASE_DIR, "data", "Dummy data_license.csv")

with open(dataPath, 'r') as datafile:
    csvreader = csv.reader(datafile)
    header = next(csvreader)

    for row in csvreader:
        licenses = rq.getData('licenses').json().get('rows', [])
        if row[1] not in [li['name'] for li in licenses]:
            print("License not in Snipe-IT, creating model.")

            newLicenseData = {
                "name": row[0],
                "seats": row[1],
                "category_id": row[3]
            }
            rq.postData('licenses', newLicenseData, invalidate_after=['licenses'])

        else:
            print("License in Snipe-IT, skipping.")
            continue

