"""
Step 1:
    GET all asset information into program for cross-reference

Step 2:
    Read CSV file with asset information

Step 3:
    Check if model exists in snipe-it
    If not, create model and add to snipe it
Step 4:Then create the asset and add to snipe it
"""

import os, csv, requests
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

token = os.getenv("APP_KEY")


