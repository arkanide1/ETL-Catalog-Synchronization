from lxml import etree
import sys
import os

XML_SOURCE = input(
    "Entrez le chemin du fichier XML source [data/catalogue_clean.xml] : "
).strip()
if not XML_SOURCE:
    XML_SOURCE = "data/catalogue_clean.xml"

XSD_CIBLE = sys.argv[2] if len(sys.argv) > 2 else "xsd_metier.xsd"

XML_CIBLE = sys.argv[3] if len(sys.argv) > 3 else "data/catalogue_cible.xml"

XSL_OUTPUT = "scripts/transform.xsl"

for fichier in [XML_SOURCE, XSD_CIBLE]:
    if not os.path.exists(fichier):
        print(f"Fichier introuvable : {fichier}")
        sys.exit(1)

#Lecture du fichier catalogue source
tree_source = etree.parse(XML_SOURCE)
root_source = tree_source.getroot()

premiers_enfants = list(root_source)
if not premiers_enfants:
    print("Le XML source ne contient aucun article.")
    sys.exit(1)

balise_article = root_source[0].tag
print(f"Balise d'article détectée : <{balise_article}>")

premier_article = root_source[0]
sous_balises = [enfant.tag for enfant in premier_article]
print(f"Sous-balises trouvées : {sous_balises}")

def detecter_balise(sous_balises, mots_cles):
    for balise in sous_balises:
        balise_lower = balise.lower()
        for mot in mots_cles:
            if mot in balise_lower:
                return balise
    return None

MOTS_CLES = {
    "name": ["nom", "name", "titre", "title", "libelle", "designation"],
    "price": ["prix", "price", "tarif", "cout", "cost", "montant"],
    "categorie": ["categ", "category", "famille", "type", "rayon"],
    "date_ajout": ["date", "ajout", "creation", "added", "created"],
    "stock": ["stock", "quantite", "quantity", "qte", "disponible"],
    "description": ["desc", "detail", "info", "resume", "about"],
    "marque": ["marque", "brand", "fabricant", "maker", "manufacturer"],
}

mapping = {}
for champ_cible, mots_cles in MOTS_CLES.items():
    balise_trouvee = detecter_balise(sous_balises, mots_cles)
    if balise_trouvee:
        mapping[champ_cible] = balise_trouvee
        print(f"<{champ_cible}> ← <{balise_trouvee}>")
    else:
        print(f"<{champ_cible}> : aucune balise source trouvée")

champs_obligatoires = ["name", "price", "categorie"]
manquants = [c for c in champs_obligatoires if c not in mapping]

if manquants:
    print(f"Champs obligatoires introuvables dans le XML source : {manquants}")
    print("Vérifiez les noms de balises du fichier source.")
    sys.exit(1)

a_attribut_id = "id" in premier_article.attrib
print(f"Attribut id détecté : {'oui' if a_attribut_id else 'non,sera généré automatiquement'}")

#Génération du fichier XSLT catalogue_cible.xml

xsl_lignes = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">',
    '',
    '<xsl:template match="/">',
    '<products>',
    f'<xsl:apply-templates select="//{balise_article}"/>',
    '</products>',
    '</xsl:template>',
    '',
    f'<xsl:template match="{balise_article}">',
]

if a_attribut_id:
    xsl_lignes.append('<product id="{@id}">')
else:
    xsl_lignes.append('<product>')

champs_obligatoires_xsl = ["name", "price", "categorie"]
champs_optionnels_xsl = ["date_ajout", "stock", "description", "marque"]

for champ_cible, balise_source in mapping.items():
    if champ_cible in champs_obligatoires_xsl:
        xsl_lignes.append(
            f'<{champ_cible}><xsl:value-of select="{balise_source}"/></{champ_cible}>'
        )
    else:
        xsl_lignes.append(
            f'<xsl:if test="{balise_source} and {balise_source} != \'\'">'
        )
        xsl_lignes.append(
            f'<{champ_cible}><xsl:value-of select="{balise_source}"/></{champ_cible}>'
        )
        xsl_lignes.append('</xsl:if>')

xsl_lignes += [
    '</product>',
    '</xsl:template>',
    '',
    '</xsl:stylesheet>',
]

xsl_contenu = "\n".join(xsl_lignes)

with open(XSL_OUTPUT, "w", encoding="UTF-8") as f:
    f.write(xsl_contenu)


#Application de la transformation XSLT vers le xsd métier 

xsl_tree = etree.parse(XSL_OUTPUT)
transform = etree.XSLT(xsl_tree)
xml_cible_tree = transform(tree_source)

if not a_attribut_id:
    for index, product in enumerate(xml_cible_tree.getroot(), start=1):
        product.set("id", str(index))


with open(XML_CIBLE, "wb") as f:
    f.write(
        etree.tostring(
            xml_cible_tree,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8"
        )
    )



#Validation contre le schéma XSD

with open(XSD_CIBLE, "rb") as f:
    xsd_doc = etree.parse(f)

schema = etree.XMLSchema(xsd_doc)
valide = schema.validate(xml_cible_tree)

if valide:
    print("XML cible conforme au XSD.")
else:
    print("XML généré mais contient des erreurs de conformité par rapport au XSD métier :")
    for erreur in schema.error_log:
        print(f"Ligne {erreur.line} : {erreur.message}")
    

#Resume
print(f"Source   : {XML_SOURCE}")
print(f"XSL      : {XSL_OUTPUT}")
print(f"XSD      : {XSD_CIBLE}")
print(f"Résultat : {XML_CIBLE} {'conforme' if valide else 'non conforme'}")
