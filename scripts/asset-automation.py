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

import os, csv, requests
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

token = os.getenv("API_KEY")


with open("~/Documents/GitHub/privy-snipeit/data/Dummy data_new.csv", 'r') as datafile:
    csvreader = csv.reader(datafile)
    header = next(csvreader) # Skip header row
    
    for row in csvreader:
        print(row)


