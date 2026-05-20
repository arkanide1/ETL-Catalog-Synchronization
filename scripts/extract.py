import xml.etree.ElementTree as ET
import os

SOURCE_FILE = os.path.join(
    os.path.dirname(__file__),
    '..',
    'data',
    'source_catalog.xml'
)

def extract_data():

    # Lire le XML comme texte
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Corriger le caractère XML invalide &
    content = content.replace("&", "&amp;")

    # Parser le contenu XML
    root = ET.fromstring(content)

    products = []

    for product in root.findall("product"):

        products.append({
            "id": product.findtext("id"),
            "name": product.findtext("name"),
            "price": product.findtext("price"),
            "date": product.findtext("date"),
            "category": product.findtext("category")
        })

    return products
