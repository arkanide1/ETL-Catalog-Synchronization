import os

from extract import extract_data
from clean import clean_data, generate_clean_xml
from error_detector import (
    validate_catalogue,
    generate_error_report
)


def main():

    print("=" * 50)
    print("ETL CATALOG SYNCHRONIZATION")
    print("=" * 50)

    # -------------------------
    # 1. EXTRACTION
    # -------------------------
    print("\n[1] Extraction...")

    products = extract_data()

    print(f"{len(products)} produits extraits")

    # -------------------------
    # 2. CLEANING
    # -------------------------
    print("\n[2] Nettoyage...")

    cleaned_products = clean_data(products)

    clean_xml = os.path.join(
        "data",
        "catalogue_clean.xml"
    )

    generate_clean_xml(
        cleaned_products,
        clean_xml
    )

    # -------------------------
    # 3. VALIDATION
    # -------------------------
    print("\n[3] Validation...")

    errors, total = validate_catalogue(clean_xml)

    report_xml = os.path.join(
        "data",
        "rapport_erreurs.xml"
    )

    nb_errors, nb_blocked = generate_error_report(
        errors,
        total,
        report_xml
    )

    print(f"{nb_errors} erreurs détectées")
    print(f"{nb_blocked} produits bloquants")

    # -------------------------
    # 4. TRANSFORMATION
    # -------------------------
    if nb_blocked > 0:

        print("\n[✗] Transformation annulée")
        print("Des produits bloquants existent.")
        return

    print("\n[4] Transformation...")

    os.system("python scripts/transform.py")

    print("\n[✓] Pipeline terminé avec succès")


if __name__ == "__main__":
    main()