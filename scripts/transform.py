from lxml import etree

XML_SOURCE = "data/catalogue_clean.xml"
XSD_CIBLE  = "data/xsd_metier.xsd"
XML_CIBLE  = "data/catalogue_cible.xml"

tree   = etree.parse(XML_SOURCE)
root   = tree.getroot()
cible  = etree.Element("products")

for product in root.findall("product"):
    p = etree.SubElement(cible, "product")
    p.set("id", product.findtext("id", ""))
    etree.SubElement(p, "name").text      = product.findtext("name", "")
    etree.SubElement(p, "price").text     = product.findtext("price", "")
    etree.SubElement(p, "categorie").text = product.findtext("category", "")
    date = product.findtext("date", "")
    if date:
        etree.SubElement(p, "date_ajout").text = date

with open(XML_CIBLE, "wb") as f:
    f.write(etree.tostring(
        etree.ElementTree(cible),
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8"
    ))

with open(XML_CIBLE, "wb") as f:
    f.write(etree.tostring(
        etree.ElementTree(cible),
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8"
    ))

# validate from the file on disk, not from memory
with open(XSD_CIBLE, "rb") as f:
    schema = etree.XMLSchema(etree.parse(f))

with open(XML_CIBLE, "rb") as f:        # ← read the file back from disk
    xml_from_disk = etree.parse(f)       # ← parse it again

valide = schema.validate(xml_from_disk)  # ← validate the file version

if valide:
    print("XML cible conforme au XSD.")
else:
    print("Erreurs de conformite :")
    for erreur in schema.error_log:
        print(f"  Ligne {erreur.line} : {erreur.message}")