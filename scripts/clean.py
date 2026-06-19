import re
import os
import xml.etree.ElementTree as ET

from xml.dom import minidom
from datetime import datetime

from extract import extract_data


  
# DATE FORMATS


DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%m-%d-%Y"
]



# CLEAN NAME
  

def clean_name(name: str) -> str | None:

    # vide ou None
    if not name or not name.strip():
        return None

    # supprimer espaces autour
    cleaned = name.strip()

    # supprimer caractères spéciaux
    cleaned = re.sub(r"[^\w\s\-]", "", cleaned)

    # séparer noms collés
    cleaned = re.sub(r"([a-z])([A-Z])", r"\1 \2", cleaned)

    # supprimer doubles espaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Title Case
    return cleaned.title()


  
# CLEAN PRICE


def clean_price(price: str) -> float | None:

    # vide ou N/A
    if not price or price.strip().upper() == "N/A":
        return None

    try:
        value = float(price.strip())

    except ValueError:
        return None

    # prix négatif
    if value < 0:
        return None

    return value



# CLEAN DATE
  

def clean_date(date: str) -> str | None:

    # vide
    if not date or not date.strip():
        return None

    # tester tous les formats
    for fmt in DATE_FORMATS:

        try:
            parsed = datetime.strptime(date.strip(), fmt)

            # format standard
            return parsed.strftime("%Y-%m-%d")

        except ValueError:
            continue

    return None



# CLEAN CATEGORY
  

def clean_category(category: str) -> str:

    # vide
    if not category or not category.strip():
        return "Unknown"

    # remplacer &
    cleaned = category.strip().replace("&", "and")

    # catégorie invalide
    if re.search(r"^\d", cleaned):
        return "Unknown"

    return cleaned.title()



# CLEAN DATA
 

def clean_data(products: list) -> list:

    cleaned_products = []

    for p in products:

        cleaned_products.append({

            "id": p.get("id"),

            "name": clean_name(
                p.get("name") or ""
            ),

            "price": clean_price(
                p.get("price") or ""
            ),

            "date": clean_date(
                p.get("date") or ""
            ),

            "category": clean_category(
                p.get("category") or ""
            )
        })

    return cleaned_products


 
# GENERATE CLEAN XML


def generate_clean_xml(
    products: list,
    output_path: str
):

    # racine XML
    root = ET.Element("catalogue")

    # ajouter produits
    for p in products:

        product = ET.SubElement(root, "product")

        ET.SubElement(
            product,
            "id"
        ).text = str(p["id"])

        ET.SubElement(
            product,
            "name"
        ).text = (
            str(p["name"])
            if p["name"] is not None
            else ""
        )

        ET.SubElement(
            product,
            "price"
        ).text = (
            str(p["price"])
            if p["price"] is not None
            else ""
        )

        ET.SubElement(
            product,
            "date"
        ).text = (
            str(p["date"])
            if p["date"] is not None
            else ""
        )

        ET.SubElement(
            product,
            "category"
        ).text = str(p["category"])

    # formatter XML
    xml_str = minidom.parseString(
        ET.tostring(root, encoding="unicode")
    ).toprettyxml(indent="    ")

    # écrire fichier
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

    print(f"[✓] catalogue_clean.xml généré → {output_path}")



# MAIN


if __name__ == "__main__":

    # EXTRACTION
    raw_products = extract_data()

    # CLEANING
    cleaned_products = clean_data(raw_products)

    # PATH XML propre
    output = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data',
        'catalogue_clean.xml'
    )

    # GENERATE CLEAN XML
    generate_clean_xml(
        cleaned_products,
        output_path=output
    )

    # DISPLAY
    print(f"\n[✓] {len(cleaned_products)} produits nettoyés\n")

    print("=== APERCU PRODUITS NETTOYES ===\n")

    for p in cleaned_products[:5]:
        print(p)