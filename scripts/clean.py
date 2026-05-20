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

    # mettre en Title Case
    return cleaned.title()


# CLEAN PRICE


def clean_price(price: str) -> float | None:

    # vide ou N/A
    if not price or price.strip().upper() == "N/A":
        return None

    # convertir en float
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

            # convertir vers YYYY-MM-DD
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


# DETECT ERRORS


def detect_errors(products: list) -> list:

    errors = []

    for p in products:

        pid = p.get("id", "unknown")

       
        # NAME
       

        name = p.get("name") or ""

        if not name.strip():

            errors.append({
                "product_id": pid,
                "field": "name",
                "value": name,
                "type": "missing_name"
            })

        elif re.search(r"[#@!$%^*]", name):

            errors.append({
                "product_id": pid,
                "field": "name",
                "value": name.strip(),
                "type": "special_characters"
            })

        elif re.search(r"([a-z])([A-Z])", name):

            errors.append({
                "product_id": pid,
                "field": "name",
                "value": name.strip(),
                "type": "concatenated_name"
            })

        
        # PRICE
  

        price = p.get("price") or ""

        if not price.strip() or price.strip().upper() == "N/A":

            errors.append({
                "product_id": pid,
                "field": "price",
                "value": price,
                "type": "invalid_price"
            })

        else:

            try:

                if float(price) < 0:

                    errors.append({
                        "product_id": pid,
                        "field": "price",
                        "value": price,
                        "type": "negative_price"
                    })

            except ValueError:

                errors.append({
                    "product_id": pid,
                    "field": "price",
                    "value": price,
                    "type": "non_numeric_price"
                })

     
        # DATE
    

        date = p.get("date") or ""

        if not date.strip():

            errors.append({
                "product_id": pid,
                "field": "date",
                "value": date,
                "type": "missing_date"
            })

        elif clean_date(date) is None:

            errors.append({
                "product_id": pid,
                "field": "date",
                "value": date,
                "type": "invalid_date_format"
            })


        # CATEGORY
       

        category = p.get("category") or ""

        if not category.strip():

            errors.append({
                "product_id": pid,
                "field": "category",
                "value": category,
                "type": "missing_category"
            })

        elif "&" in category:

            errors.append({
                "product_id": pid,
                "field": "category",
                "value": category,
                "type": "unescaped_ampersand"
            })

        elif re.search(r"^\d", category.strip()):

            errors.append({
                "product_id": pid,
                "field": "category",
                "value": category,
                "type": "invalid_category_name"
            })

    return errors


# GENERATE ERROR REPORT


def generate_error_report(
    errors: list,
    output_path: str
):

    # racine XML
    root = ET.Element("error_report")

    root.set(
        "total_errors",
        str(len(errors))
    )

    # ajouter erreurs
    for e in errors:

        node = ET.SubElement(root, "error")

        ET.SubElement(
            node,
            "product_id"
        ).text = str(e["product_id"])

        ET.SubElement(
            node,
            "field"
        ).text = str(e["field"])

        ET.SubElement(
            node,
            "value"
        ).text = str(e["value"])

        ET.SubElement(
            node,
            "type"
        ).text = str(e["type"])

    # formatter XML
    xml_str = minidom.parseString(
        ET.tostring(root, encoding="unicode")
    ).toprettyxml(indent="    ")

    # écrire fichier
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

    print(f"[✓] error_report.xml généré → {output_path}")


# CLEAN DATA


def clean_data(products: list) -> tuple:

    # détecter erreurs
    errors = detect_errors(products)

    cleaned = []

    # nettoyer données
    for p in products:

        cleaned.append({

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

    return cleaned, errors


# MAIN


if __name__ == "__main__":

    # EXTRACTION
    raw_products = extract_data()

    # CLEANING
    cleaned_products, errors = clean_data(raw_products)

    # PATH error_report.xml
    output = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data',
        'error_report.xml'
    )

    # GENERATE XML REPORT
    generate_error_report(
        errors,
        output_path=output
    )

    # DISPLAY
    print(f"\n[✓] {len(cleaned_products)} produits nettoyés")
    print(f"[✓] {len(errors)} erreurs détectées\n")

    print("=== APERCU PRODUITS NETTOYES ===\n")

    for p in cleaned_products[:5]:
        print(p)

