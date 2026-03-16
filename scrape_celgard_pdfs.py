"""
Part 1a (continued): Scraping Celgard PDF Datasheets

We already scraped the product page for PDF links. Now we download
each PDF and extract the separator specs (porosity, thickness,
Gurley number, tensile strength, puncture strength).
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import pdfplumber
import time
import os
import io

# Load the product list we already scraped
df_celgard = pd.read_csv("data/celgard_products.csv")
print(f"Found {len(df_celgard)} products to download PDFs for\n")

# Create a directory to store downloaded PDFs
os.makedirs("data/celgard_pdfs", exist_ok=True)

# Download each PDF and extract text/tables
all_specs = []

for _, row in df_celgard.iterrows():
    name = row["name"]
    pdf_url = row["pdf_url"]
    category = row["category"]

    print(f"Downloading: {name}...")

    # Download the PDF
    response = requests.get(pdf_url)
    if response.status_code != 200:
        print(f"  FAILED (status {response.status_code})")
        continue

    # Save locally
    filename = pdf_url.split("/")[-1]
    filepath = f"data/celgard_pdfs/{filename}"
    with open(filepath, "wb") as f:
        f.write(response.content)

    # Parse the PDF with pdfplumber
    pdf = pdfplumber.open(io.BytesIO(response.content))

    # Extract tables from all pages
    tables_found = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            tables_found.extend(table)

    # Also extract raw text for fallback
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"

    # Parse the table rows into a dict
    # Each PDF table has 3 columns: [Property, Unit, Value]
    # Skip the header row (first row contains column names)
    specs = {"name": name, "category": category, "pdf_file": filename}
    for table_row in tables_found:
        if table_row and len(table_row) >= 3:
            key = str(table_row[0]).strip() if table_row[0] else ""
            unit = str(table_row[1]).strip() if table_row[1] else ""
            val = str(table_row[2]).strip() if table_row[2] else ""
            # Skip header row and empty rows
            if key and val and key != "Basic Film Properties":
                specs[key] = val
                specs[key + " (unit)"] = unit

    all_specs.append(specs)
    pdf.close()

    # Be polite - stagger requests
    time.sleep(0.2)

# Convert to DataFrame
df_specs = pd.DataFrame(all_specs)

print(f"\n=== Extracted specs for {len(df_specs)} products ===")
print(f"Columns found: {list(df_specs.columns)}")
print(df_specs)

# Save
df_specs.to_csv("data/celgard_specs.csv", index=False)
print("\nSaved to data/celgard_specs.csv")
