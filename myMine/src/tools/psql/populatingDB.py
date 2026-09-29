import os
import re
import sqlite3
import unicodedata
from pathlib import Path

import requests
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

database_dir = Path(__file__).parent.parent / "dataBase"
database_dir.mkdir(exist_ok=True)

db_path = database_dir / "arielxandria.db"

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
CREATE TABLE IF NOT EXISTS notion_books (
    page_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL UNIQUE,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS local_books (
    path TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL,
    extension TEXT
)
""")

conn.commit()

cursor.execute("DELETE FROM notion_books")
conn.commit()

url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"

next_cursor = None


def normalize_title(title: str) -> str:
    """
    Normaliza um título para comparação.

    Exemplos:
        "The_Programmers_Brain"   -> "the programmers brain"
        "  The   Programmers Brain " -> "the programmers brain"
        "Thé Programmer's Brain"  -> "the programmers brain"
    """

    title = title.replace("_", " ")
    title = unicodedata.normalize("NFKD", title)
    title = "".join(c for c in title if not unicodedata.combining(c))
    title = title.replace("'", "")
    title = re.sub(r"\s+", " ", title)

    return title.strip().lower()


flag = True
while True:

    payload = {}

    if next_cursor is not None:
        payload["start_cursor"] = next_cursor

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()

    for page in data["results"]:

        properties = page["properties"]

        title_list = properties["Name"]["title"]

        title = ""

        if title_list:
            title = title_list[0]["plain_text"]

        if not title.strip():
            continue

        status = None
        if properties["Status"]["select"] is not None:
            status = properties["Status"]["select"]["name"]

        normalized = normalize_title(title)

        try:
            cursor.execute(
                """
                INSERT INTO notion_books
                (page_id, title, normalized_title, status)
                VALUES (?, ?, ?, ?)
                """,
                (
                    page["id"],
                    title,
                    normalized,
                    status,
                ),
            )
        except sqlite3.IntegrityError:
            print(f"⚠️  Livro duplicado ignorado (Verificar no Notion): '{title}'")
            continue

    conn.commit()

    if not data["has_more"]:
        break

    next_cursor = data["next_cursor"]

print("Notion sincronizado com sucesso.")

print("Sincronizando biblioteca local...")

library_path = Path("/mnt/hdmenezess42/TomeHold")
ignored_dirs = {"2bSorted", "Papers"}

for file in library_path.rglob("*"):

    if not file.is_file():
        continue

    if any(part in ignored_dirs for part in file.parts):
        continue

    filename = file.stem
    parts = filename.split(" - ")

    parts = re.split(r"\s*-\s*", filename)

    if len(parts) < 3:
        print(f"⚠️  Nome fora do padrão: {file}")
        continue

    title = parts[2].strip()

    if not title:
        continue

    normalized = normalize_title(title)

    try:
        cursor.execute(
            """
            INSERT INTO local_books
            (path, title, normalized_title, extension)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(file),
                title,
                normalized,
                file.suffix.lower(),
            ),
        )

    except sqlite3.IntegrityError:
        print(f"⚠️  Livro duplicado ignorado (Local): '{title}'")
        continue

conn.commit()

print("Biblioteca local sincronizada com sucesso.")

cursor.execute("SELECT COUNT(*) FROM notion_books")
print(f"{cursor.fetchone()[0]} livros encontrados NOTION.")

cursor.execute("SELECT COUNT(*) FROM local_books")
print(f"{cursor.fetchone()[0]} livros encontrados LOCAL.")


conn.close()
