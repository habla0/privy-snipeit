import os, csv, requests, json
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataPath = os.path.join(BASE_DIR, "data", "Dummy data.csv")

load_dotenv() # Load environment variables from .env file

token = os.getenv("API_KEY")

# API calls to get existing data for cross-referencing
# models, hardware, manufacturers, categories, locations
def getData(endpoint):
    r = requests.get(
        f"http://localhost:8000/api/v1/{endpoint}",
        headers = {"Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
                }
    )

    return r

# POST data to API
def postData(endpoint, data):
    p = requests.post(
        f"http://localhost:8000/api/v1/{endpoint}",
        headers = {"Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
                },
        data = json.dumps(data)
    )

    if p.raise_for_status() != None or p.json().get('status') == 'error':
        print(f"[FAIL]: Failed to create object {row[3]} with status {p.status_code}.")
        print(p.json())
    else:
        print(f"[OK]: Created object {row[3]} with status {p.status_code}.")

    return p

# Open CSV
with open(dataPath, 'r') as datafile:
    csvreader = csv.reader(datafile)
    header = next(csvreader) # Skip header row
    
    # Check for new models
    for row in csvreader:
        print(f"Checking Asset {row[0]}")

        # Check if manufacturer exists in Snipe-IT, if not create it
        if row[3] not in [manufacturer['name'] for manufacturer in getData('manufacturers').json()['rows']]: # Check if manufacturer exists in manufacturer data
            print(f"Manufacturer {row[3]} not in Snipe-IT, creating manufacturer.")
            # Create manufacturer in Snipe-IT
            newManufacturerData = {
                "name": row[3]
            }
            postData('manufacturers', newManufacturerData)

        # Check if model exists in Snipe-IT, if not create it
        if row[1] not in [model['name'] for model in getData('models').json()['rows']] and row[2] == "License": # Check if model exists in model data
            print("License not in Snipe-IT, creating model.")

            newLicenseData = {
                "name": row[1],
                "seats": row[4],
                "category_id": next((category['id'] for category in getData('categories').json()['rows'] if category['name'] == row[2]), None), # Get category ID from name in CSV
                "company_id": next((company['id'] for company in getData('companies').json()['rows'] if company['name'] == row[15]), None), # Get company ID from name in CSV
            }
            postData('licenses', newLicenseData)
            continue

        elif row[1] not in [model['name'] for model in getData('models').json()['rows']] and row[2] != "Laptop" and row[2] != "Phone":
            print("Accessory not in Snipe-IT, creating model.")

            newAccessoryData = {
                "name": row[1],
                "qty": 1,
                "purchase_cost": row[13],
                "purchase_date": row[12],
                "category_id": next((category['id'] for category in getData('categories').json()['rows'] if category['name'] == row[2]), None),
                "company_id": 1, # Default to Privy, this is a PRIVY asset management after all
                "location_id": next((location['id'] for location in getData('locations').json()['rows'] if location['name'] == row[14]), None),
                "manufacturer_id": next((manufacturer['id'] for manufacturer in getData('manufacturers').json()['rows'] if manufacturer['name'] == row[3]), None),
            }
            postData('accessories', newAccessoryData)
            continue

        elif row[1] not in [model['name'] for model in getData('models').json()['rows']]: # Check if model exists in model data
            # Create model in Snipe-IT
            newModelData = {
                "name": row[1],
                "manufacturer_id": next((manufacturer['id'] for manufacturer in getData('manufacturers').json()['rows'] if manufacturer['name'] == row[3])), # Get manufacturer ID from name in CSV
                "category_id": next((category['id'] for category in getData('categories').json()['rows'] if category['name'] == row[2])), # Get category ID from name in CSV
                "fieldset_id": 0 # Fieldset ID for Specifications
            }
            postData('models', newModelData)

        else:
            print(f"{row[1]} already exists in Snipe-IT, skipping model creation.")
        
        # Add final asset from CSV 
        newAssetData = {
            "asset_tag": row[0],
            "model_id": next((model['id'] for model in getData('models').json()['rows'] if model['name'] == row[1])), # Get model ID from name in CSV
            "name": next((model['name'] for model in getData('models').json()['rows'] if model['name'] == row[1])), # Get model name from name in CSV
            #"manufacturer_id": next((manufacturer['name'] for manufacturer in getData('manufacturers').json()['rows'] if manufacturer['name'] == row[3]), None), # Get manufacturer ID from name in CSV
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
            "rtd_location_id": next((location['id'] for location in getData('locations').json()['rows'] if location['name'] == row[14]), None), # Get location ID from name in CSV
        }

        print(newAssetData)

        p2 = postData('hardware', newAssetData)
