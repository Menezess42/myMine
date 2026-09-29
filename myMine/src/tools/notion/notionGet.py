# import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

######## BASIC NOTION CONNECTION WORK IT############
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)
# geting keys

notion_patoken = os.getenv("NOTION_PATOKEN")
notion_bee_connection = os.getenv("NOTION_BEE_CONNECTION")
notion_arielxandria = os.getenv("NOTION_ARIELXANDRIA")

# Notion
NOTION_VERSION = "2026-03-11"
NOTION_API_URL = "https://api.notion.com/v1/"
flags = {"users": "users"}


url = f"https://api.notion.com/v1/databases/{notion_arielxandria}"

headers = {
    "Notion-Version": f"{NOTION_VERSION}",
    "Authorization": f"Bearer {notion_bee_connection}",
}

response = requests.get(url, headers=headers)
print(response.text)
######################################################
