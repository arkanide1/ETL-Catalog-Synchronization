import xml.etree.ElementTree as ET
from datetime import datetime
import re
import os

REPORT_NS = "http://ensias.ma/catalogue/rapport"
DATE_FORMAT = "%Y-%m-%d"

DEFAULT_CLEAN_XML = os.path.join(os.path.dirname(__file__), "..", "data", "catalogue_clean.xml")
DEFAULT_REPORT_XML = os.path.join(os.path.dirname(__file__), "..", "data", "rapport_erreurs.xml")

def check_id(product_id, seen_ids):
    errors = []
    if not product_id or not product_id.strip():
        errors.append(make_error("?", "id", "VALEUR_MANQUANTE", "l'id est absent", "(vide)"))
        return errors, product_id

    pid = product_id.strip()
    try:
        val = int(pid)
        if val <= 0:
            errors.append(make_error(pid, "id", "VALEUR_INVALIDE",
                f"l'id doit etre positif, valeur trouvee : {val}", pid))
    except ValueError:
        errors.append(make_error(pid, "id", "FORMAT_INCORRECT",
            f"l'id n'est pas un entier : '{pid}'", pid))
        return errors, pid

    if pid in seen_ids:
        errors.append(make_error(pid, "id", "DOUBLON",
            f"l'id {pid} est duplique", pid))
    else:
        seen_ids.add(pid)

    return errors, pid

def check_name(pid, name):
    errors = []
    if name is None or name.strip() == "":
        errors.append(make_error(pid, "name", "VALEUR_MANQUANTE",
            "le champ name est vide", "(vide)"))
    elif len(name.strip()) > 100:
        errors.append(make_error(pid, "name", "VALEUR_INVALIDE",
            f"le nom depasse 100 caracteres ({len(name.strip())})", name.strip()[:30] + "..."))
    return errors

def check_price(pid, price_text):
    errors = []
    if price_text is None or price_text.strip() == "":
        errors.append(make_error(pid, "price", "VALEUR_MANQUANTE",
            "le champ price est vide, ce produit sera bloque lors de la transformation", "(vide)"))
        return errors
    try:
        val = float(price_text.strip())
        if val <= 0:
            errors.append(make_error(pid, "price", "VALEUR_INVALIDE",
                f"le prix doit etre superieur a 0, valeur : {val}", price_text.strip()))
    except ValueError:
        errors.append(make_error(pid, "price", "FORMAT_INCORRECT",
            f"prix non numerique : '{price_text}'", price_text.strip()))
    return errors

def check_category(pid, category_text):
    errors = []
    if category_text is None or category_text.strip() == "":
        errors.append(make_error(pid, "category", "VALEUR_MANQUANTE",
            "le champ category est vide", "(vide)"))
        return errors
    cat = category_text.strip()
    if cat == "Unknown":
        errors.append(make_error(pid, "category", "CATEGORIE_NON_RESOLUE",
            "categorie 'Unknown' : la valeur source etait invalide ou absente", cat))
    if len(cat) > 60:
        errors.append(make_error(pid, "category", "VALEUR_INVALIDE",
            f"categorie trop longue ({len(cat)} chars, max 60)", cat[:30] + "..."))
    return errors

def check_date(pid, date_text):
    errors = []
    if date_text is None or date_text.strip() == "":
        errors.append(make_error(pid, "date", "AVERTISSEMENT",
            "date vide, la balise date_ajout sera absente dans le XML cible", "(vide)"))
        return errors
    try:
        datetime.strptime(date_text.strip(), DATE_FORMAT)
    except ValueError:
        errors.append(make_error(pid, "date", "FORMAT_INCORRECT",
            f"format de date invalide, attendu YYYY-MM-DD, recu : '{date_text}'", date_text.strip()))
    return errors

def make_error(pid, field, error_type, message, value):
    return {
        "product_id": str(pid),
        "champ": field,
        "type": error_type,
        "message": message,
        "valeur": str(value)
    }

def validate_catalogue(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    all_errors = []
    seen_ids = set()

    for product in root.findall("product"):
        raw_id = product.findtext("id") or ""
        id_errors, pid = check_id(raw_id, seen_ids)
        all_errors += id_errors
        all_errors += check_name(pid, product.findtext("name"))
        all_errors += check_price(pid, product.findtext("price"))
        all_errors += check_category(pid, product.findtext("category"))
        all_errors += check_date(pid, product.findtext("date"))

    return all_errors, len(root.findall("product"))

def generate_error_report(errors, total_products, output_path):
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    nb_errors = len(errors)

    # produits bloquants = ceux avec name ou price invalide
    blocking_types = {"VALEUR_MANQUANTE", "VALEUR_INVALIDE", "FORMAT_INCORRECT", "DOUBLON"}
    blocking_fields = {"name", "price"}
    blocked_ids = set(
        e["product_id"] for e in errors
        if e["champ"] in blocking_fields and e["type"] in blocking_types
    )
    statut = "ECHEC_VALIDATION" if nb_errors > 0 else "SUCCES"
    rapport = ET.Element("rapport_erreurs", attrib={
        "xmlns": REPORT_NS,
        "date_generation": now,
        "nb_erreurs": str(nb_errors),
        "nb_produits": str(total_products),
        "nb_bloquants": str(len(blocked_ids)),
        "statut": statut
    })
    resume = ET.SubElement(rapport, "resume_par_type")
    type_counts = {}
    for e in errors:
        type_counts[e["type"]] = type_counts.get(e["type"], 0) + 1
    for t, cnt in sorted(type_counts.items()):
        ET.SubElement(resume, "type_erreur", attrib={"code": t, "count": str(cnt)})

    bloquants_el = ET.SubElement(rapport, "produits_bloquants")
    for pid in sorted(blocked_ids, key=lambda x: int(x) if x.isdigit() else 0):
        ET.SubElement(bloquants_el, "produit_id").text = pid

    detail = ET.SubElement(rapport, "detail_erreurs")
    for i, err in enumerate(errors, start=1):
        anomalie = ET.SubElement(detail, "anomalie", attrib={"numero": str(i)})
        ET.SubElement(anomalie, "produit_id").text = err["product_id"]
        ET.SubElement(anomalie, "champ").text = err["champ"]
        ET.SubElement(anomalie, "type").text = err["type"]
        ET.SubElement(anomalie, "message").text = err["message"]
        ET.SubElement(anomalie, "valeur").text = err["valeur"]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tree_out = ET.ElementTree(rapport)
    ET.indent(tree_out, space="    ")
    tree_out.write(output_path, encoding="UTF-8", xml_declaration=True)

    return nb_errors, len(blocked_ids)

if __name__ == "__main__":
    errors, total = validate_catalogue(DEFAULT_CLEAN_XML)

    print(f"produits analyses : {total}")
    print(f"anomalies trouvees : {len(errors)}\n")

    for e in errors:
        tag = "[BLOQUANT]" if e["type"] not in ("AVERTISSEMENT", "CATEGORIE_NON_RESOLUE") else "[warning]"
        print(f"{tag} produit {e['product_id']} | {e['champ']} | {e['type']} | {e['message']}")

    nb_err, nb_blocked = generate_error_report(errors, total, DEFAULT_REPORT_XML)
    print(f"\nrapport genere : data/rapport_erreurs.xml")
    print(f"{nb_err} erreurs | {nb_blocked} produits bloquants")
    print(f"transformation autorisee : {'non' if nb_blocked else 'oui'}")