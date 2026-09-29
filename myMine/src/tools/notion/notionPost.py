from pathlib import Path
import os

import requests
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

notion_bee_connection = os.getenv("NOTION_BEE_CONNECTION")
data_source_id = os.getenv("DATA_SOURCE_ID")

NOTION_VERSION = "2026-03-11"

url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"

headers = {
    "Authorization": f"Bearer {notion_bee_connection}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

payload = {}

response = requests.post(url, headers=headers, json=payload)

print(response.status_code)
print(response.text)
