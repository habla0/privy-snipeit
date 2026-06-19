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
            }            
)
manufacturers = r2.json()
r3 = requests.get(
    "http://localhost:8000/api/v1/categories",
    headers = {"Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
            }            
)
categories = r3.json()
r4 = requests.get(
    "http://localhost:8000/api/v1/locations",
    headers = {"Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
            }            
)
locations = r4.json()
r5 = requests.get(
    "http://localhost:8000/api/v1/users",
    headers = {"Authorization   ": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
            }
)
users = r5.json()

# Open CSV
with open(dataPath, 'r') as datafile:
    csvreader = csv.reader(datafile)
    header = next(csvreader) # Skip header row
    
    for row in csvreader:
        if row[1] not in [model['name'] for model in models['rows']]: # Check if model exists in model data

            # Create model in Snipe-IT
            newModelData = {
                "name": row[1],
                "manufacturer_id": next((manufacturer['id'] for manufacturer in manufacturers['rows'] if manufacturer['name'] == row[3]), None), # Get manufacturer ID from name in CSV
                "category_id": next((category['id'] for category in categories['rows'] if category['name'] == row[2]), None) # Get category ID from name in CSV
            }
            p = requests.post(
                "http://localhost:8000/api/v1/models",
                headers = {"Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                        },
                data = json.dumps(newModelData)
            )
            print(f"Created model: {row[1]} with status code {p.status_code}")
        else:
            print(f"Model {row[1]} already exists in Snipe-IT, skipping model creation.")

        # Add assets from CSV
        newAssetData = {
            "asset_tag": row[0],
            "model_id": next((model['id'] for model in models['rows'] if model['name'] == row[1]), None), # Get model ID from name in CSV
            "category_id": next((category['id'] for category in categories['rows'] if category['name'] == row[2]), None), # Get category ID from name in CSV
            "manufacturer_id": next((manufacturer['id'] for manufacturer in manufacturers['rows'] if manufacturer['name'] == row[3]), None), # Get manufacturer ID from name in CSV
            "status_id": row[4],
            "serial": row[5],
            "_snipeit_mac_address_1": row[6],
            "_snipeit_cpu_2": row[7],
            "_snipeit_ram_3": row[8],
            "_snipeit_storage_4": row[9],
            "_snipeit_operating_system_5": row[10],
            "_snipeit_graphics_6": row[11],
            "purchase_date": row[12],
            "purchase_cost": row[13],
            "rtd_location_id": next((location['id'] for location in locations['rows'] if location['name'] == row[14]), None), # Get location ID from name in CSV
        }

        p2 = requests.post(
            "http://localhost:8000/api/v1/hardware",
            headers = {"Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                    },
            data = json.dumps(newAssetData)
        )

        print("All assets loaded into Snipe-IT!")


            


