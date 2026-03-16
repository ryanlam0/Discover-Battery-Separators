"""
Part 1a: Scraping Celgard Separator Product Data

Celgard is the largest manufacturer of battery separators.
We scrape their product page to get links to all product datasheets.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Scrape the Celgard product data page
url = "https://www.celgard.com/product-data"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

print(f"Status code: {response.status_code}")

# Find all product entries on the page
products = soup.find_all("div", attrs={"class": "ds-item"})
print(f"Found {len(products)} products")

# Let's look at the structure of one product entry
print("\nFirst product entry:")
print(products[0])

# Extract product info: name, description, and PDF link
product_data = []
for product in products:
    info = {}

    # Get the product name
    title = product.find("div", attrs={"class": "ds-title"})
    info["name"] = title.string.strip() if title else None

    # Get the description
    desc = product.find("div", attrs={"class": "ds-desc"})
    if desc:
        p_tag = desc.find("p")
        info["description"] = p_tag.string.strip() if p_tag and p_tag.string else None

    # Get the PDF download link
    link = product.find("a", attrs={"class": "ds-download"})
    if link:
        info["pdf_url"] = "https://www.celgard.com" + link.attrs["href"]

    product_data.append(info)

df_celgard = pd.DataFrame(product_data)

# Extract the category each product belongs to
# All products are inside one <div class="datasheets"> container.
# Categories are <h3> tags between groups of <div class="ds-item"> entries.
# We walk through the children and track which <h3> heading we're under.
container = soup.find("div", attrs={"class": "datasheets"})

product_categories = []
current_category = None
for child in container.children:
    if child.name == "h3":
        current_category = child.get_text().strip()
    elif child.name == "div" and "ds-item" in child.get("class", []):
        title = child.find("div", attrs={"class": "ds-title"})
        if title:
            product_categories.append({
                "name": title.string.strip(),
                "category": current_category
            })

df_categories = pd.DataFrame(product_categories)
df_celgard = df_celgard.merge(df_categories, on="name", how="left")

print(f"\nScraped {len(df_celgard)} Celgard products:")
print(df_celgard)

# Save to CSV
df_celgard.to_csv("data/celgard_products.csv", index=False)
print("\nSaved to data/celgard_products.csv")
