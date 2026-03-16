"""
Part 1c: Scraping Separator Data from Published Review Articles

We scrape open-access PMC review articles for their comparison tables
containing separator polymer properties (porosity, thermal stability,
tensile strength, ionic conductivity, etc.).
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- Articles to scrape ---
articles = [
    {"id": "PMC10534950", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10534950/",
     "title": "Engineering Polymer Separator Membranes",
     "target_table": 7},
    {"id": "PMC11241740", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11241740/",
     "title": "Cellulose-Based Separators",
     "target_table": 1},
    {"id": "PMC11511470", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11511470/",
     "title": "Electrospun PVDF Separators",
     "target_table": 1},
    {"id": "PMC6161240", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6161240/",
     "title": "PVDF and Copolymers for Separators",
     "target_table": 1},
    {"id": "PMC12073824", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12073824/",
     "title": "PPS Separators",
     "target_table": 0},
    {"id": "PMC7831081", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7831081/",
     "title": "Li-Ion Battery Separator Safety",
     "target_table": 0},
    {"id": "PMC7603034", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7603034/",
     "title": "Functional Separators for Li Metal Battery",
     "target_table": 0},
]

all_tables = {}

for article in articles:
    print(f"\n{'='*60}")
    print(f"Scraping: {article['title']}")
    print(f"URL: {article['url']}")

    response = requests.get(article["url"])
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print("  SKIPPED - could not access")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all tables on the page
    tables = soup.find_all("table")
    print(f"Found {len(tables)} tables")

    # Extract each table into a list of rows
    for t_idx, table in enumerate(tables):
        rows = table.find_all("tr")
        if len(rows) < 3:
            continue

        # Extract headers
        headers = []
        header_row = rows[0]
        for th in header_row.find_all(["th", "td"]):
            headers.append(th.get_text().strip())

        if len(headers) < 3:
            continue

        # Extract data rows
        data_rows = []
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            row_data = [cell.get_text().strip() for cell in cells]
            if len(row_data) >= 2:
                data_rows.append(row_data)

        if len(data_rows) < 2:
            continue

        print(f"\n  Table {t_idx}: {len(data_rows)} rows, {len(headers)} cols")
        print(f"  Headers: {headers[:6]}...")

        # Store the table
        table_key = f"{article['id']}_table{t_idx}"
        all_tables[table_key] = {
            "article": article["title"],
            "article_id": article["id"],
            "table_index": t_idx,
            "headers": headers,
            "data": data_rows,
            "n_rows": len(data_rows)
        }

    # Be polite to PMC servers
    time.sleep(0.5)

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY: Extracted {len(all_tables)} tables total")
print(f"{'='*60}")

total_rows = 0
for key, table in all_tables.items():
    print(f"  {key}: {table['n_rows']} rows - {table['article']}")
    total_rows += table["n_rows"]
print(f"\nTotal data rows across all tables: {total_rows}")

# --- Save the richest tables as CSVs ---
# PMC10534950 Table 7 - multi-polymer comparison (best table)
for key, table in all_tables.items():
    # Save tables with 5+ rows
    if table["n_rows"] >= 5:
        # Pad rows to match header length
        max_cols = max(len(table["headers"]), max(len(r) for r in table["data"]))
        headers = table["headers"] + [f"col_{i}" for i in range(max_cols - len(table["headers"]))]

        padded_data = []
        for row in table["data"]:
            padded_data.append(row + [""] * (max_cols - len(row)))

        df = pd.DataFrame(padded_data, columns=headers[:max_cols])
        filename = f"data/literature_{key}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved {filename} ({table['n_rows']} rows)")
