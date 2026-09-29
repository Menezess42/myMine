import os
import select
import sqlite3
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

db_path = Path(__file__).parent.parent / "dataBase" / "arielxandria.db"

NOTION_VERSION = "2026-03-11"

notion_token = os.getenv("NOTION_BEE_CONNECTION")
data_source_id = os.getenv("DATA_SOURCE_ID")

headers = {
    "Authorization": f"Bearer {notion_token}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
SELECT
    path,
    title,
    normalized_title,
    extension
FROM pending_upload
ORDER BY title
""")

books = cursor.fetchall()

print(f"{len(books)} livros pendentes.\n")

for path, title, normalized_title, extension in books:

    print("-" * 80)
    print(f"Título: {normalized_title}")
    print("Adicionar ao Notion? [Y/n/q] (10s, padrão: Y): ", end="", flush=True)

    ready, _, _ = select.select([sys.stdin], [], [], 10)

    if ready:
        answer = sys.stdin.readline().strip().lower()
    else:
        answer = "y"
        print()

    if answer == "q":
        print("\nAbortado.")
        break

    if answer == "n":
        continue

    cursor.execute(
        """
        SELECT 1
        FROM notion_books
        WHERE normalized_title = ?
        """,
        (normalized_title,),
    )

    if cursor.fetchone():
        print(f"\nUpload Negado!\nLivro Já Catalogado!\n")
        continue

    payload = {
        "parent": {"data_source_id": data_source_id},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Status": {"select": {"name": "Ready to Start"}},
        },
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=payload,
    )

    if response.status_code not in (200, 201):
        print(f"\nErro {response.status_code}")
        print(response.text)
        break

    page = response.json()
    page_id = page["id"]

    cursor.execute(
        """
        INSERT INTO notion_books
        (page_id, title, normalized_title, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            page_id,
            title,
            normalized_title,
            "Ready to Start",
        ),
    )

    cursor.execute(
        """
        DELETE FROM pending_upload
        WHERE normalized_title = ?
        """,
        (normalized_title,),
    )

    conn.commit()

    print("✓ Adicionado ao Notion.")

conn.close()
