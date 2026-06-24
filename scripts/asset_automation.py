'''
This does everything except for licences
Please run the other script, thanks!

- Xavier Xu @ Privy
'''
import os, csv
import request_helper as rq
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataPath = os.path.join(BASE_DIR, "data", "Dummy data.csv")

# Open CSV
with open(dataPath, 'r') as datafile:
    csvreader = csv.reader(datafile)
    header = next(csvreader)  # Skip header row

    # Loop through CSV data
    for row in csvreader:
        print(f"{chr(27)}[34mChecking Asset {row[0]}{chr(27)}[0m")

        manufacturers = rq.getData('manufacturers').json().get('rows', [])
        models = rq.getData('models').json().get('rows', [])
        categories = rq.getData('categories').json().get('rows', [])
        locations = rq.getData('locations').json().get('rows', [])
        accessories = rq.getData('accessories').json().get('rows', [])
        hardware = rq.getData('hardware').json().get('rows', [])

        # Check if manufacturer exists in Snipe-IT, if not create it
        if row[3] not in [manufacturer['name'] for manufacturer in manufacturers]:
            print(f"Manufacturer {row[3]} not in Snipe-IT, creating manufacturer.")
            newManufacturerData = {"name": row[3]}
            rq.postData('manufacturers', newManufacturerData, invalidateAfter=['manufacturers'])
            manufacturers = rq.getData('manufacturers', forceRefresh=True).json().get('rows', [])

        # Check if category is accessory or asset model
        # Is accessory
        if row[2] not in {"Laptop", "Phone", "Desktop"}:
            accessory = next((item for item in accessories if item.get('name') == row[1]), None)

            if accessory is None:
                print("Accessory not in Snipe-IT, creating model.")

                newAccessoryData = {
                    "name": row[1],
                    "qty": 1,
                    "purchase_cost": row[13],
                    "purchase_date": row[12],
                    "category_id": next((category['id'] for category in categories if category['name'] == row[2]), None),
                    "company_id": 1,  # Default to Privy, this is PRIVY asset management after all
                    "location_id": next((location['id'] for location in locations if location['name'] == row[14]), None),
                    "manufacturer_id": next((manufacturer['id'] for manufacturer in manufacturers if manufacturer['name'] == row[3]), None),
                }
                rq.postData('accessories', newAccessoryData, invalidateAfter=['accessories', 'models'])

                continue
            else:  # Update accessory quantities
                print("Accessory found in Snipe-IT, updating data.")
                newQty = int(accessory.get('qty', 0)) + 1
                newAccessoryData = {"qty": newQty}
                rq.patchData("accessories", accessory['id'], newAccessoryData, invalidateAfter=['accessories'])

            continue

        # Is model
        elif row[1] not in [model['name'] for model in models]:
            # Create model in Snipe-IT
            print(f"Model {row[1]} not in Snipe-IT, creating model.")
            newModelData = {
                "name": row[1],
                "manufacturer_id": next((manufacturer['id'] for manufacturer in manufacturers if manufacturer['name'] == row[3])),  # Get manufacturer ID from name in CSV
                "category_id": next((category['id'] for category in categories if category['name'] == row[2])),  # Get category ID from name in CSV
                "fieldset_id": 2,  # Fieldset ID for Specifications
            }
            rq.postData('models', newModelData, invalidateAfter=['models'])
            models = rq.getData('models', forceRefresh=True).json().get('rows', [])
        else:
            print(f"{row[1]} already exists in Snipe-IT, skipping model creation.\n")

        # Check if asset already exists
        if row[0] not in [asset['asset_tag'] for asset in hardware]:
            print(f"Asset {row[0]} does not exist, creating new asset.")
            newAssetData = {
                "asset_tag": row[0],
                "model_id": next((model['id'] for model in models if model['name'] == row[1])),  # Get model ID from name in CSV
                "name": next((model['name'] for model in models if model['name'] == row[1])),  # Get model name from name in CSV
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
                "rtd_location_id": next((location['id'] for location in locations if location['name'] == row[14]), None),  # Get location ID from name in CSV
            }
            rq.postData('hardware', newAssetData, invalidateAfter=['hardware'])
            continue
        else:
            print(f"Asset {row[0]} already exists in Snipe-IT, skipping asset {row[0]}.\n")

