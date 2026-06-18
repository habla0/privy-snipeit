"""
Step 1:
    GET all asset information into program for cross-reference

Step 2:
    Read CSV file with asset information

Step 3:
    Check if asset exists in snipe-it

Step 4:
    Check if model exists in snipe-it
    If not, create model and add to snipe-it

Step 5:
    Create the asset and add to snipe-it
"""
import os, csv, requests, json
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataPath = os.path.join(BASE_DIR, "data", "Dummy data.csv")

load_dotenv() # Load environment variables from .env file

token = os.getenv("API_KEY")

# API calls to get existing data for cross-referencing
r1 = requests.get(
    "http://localhost:8000/api/v1/models",
    headers = {"Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
            }
    )
models = r1.json()
r2 = requests.get(
    "http://localhost:8000/api/v1/manufacturers",
    headers = {"Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
            }            )
manufacturers = r2.json()
r3 = requests.get(
    "http://localhost:8000/api/v1/categories",
    headers = {"Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
            }            )
categories = r3.json()


with open(dataPath, 'r') as datafile:
    csvreader = csv.reader(datafile)
    header = next(csvreader) # Skip header row
    
    for row in csvreader:
        if row[1] not in [model['name'] for model in models['rows']]: # Check if model exists in model data

            # Cross-reference manufacturer and model category ID with asset data
            row[3] = next((manufacturer['id'] for manufacturer in manufacturers['rows'] if manufacturer['name'] == row[3]), None) # Get manufacturer ID from name in CSV
            row[2] = next((category['id'] for category in categories['rows'] if category['name'] == row[2]), None) # Get category ID from name in CSV

            # Create model in Snipe-IT
            newModelData = {
                "name": row[1],
                "manufacturer_id": row[3],
                "category_id": row[2],
            }
            r4 = requests.post(
                "http://localhost:8000/api/v1/models",
                headers = {"Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                        },
                data = json.dumps(newModelData)
            )

            print(f"Created model: {row[1]} with status code {r4.status_code}")
        print(row)


