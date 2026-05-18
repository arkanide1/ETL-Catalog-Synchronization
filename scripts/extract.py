import xml.etree.ElementTree as ET

SOURCE_FILE = "../data/source_catalog.xml"

def extract_data():

    tree = ET.parse(SOURCE_FILE)
    root = tree.getroot()

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

