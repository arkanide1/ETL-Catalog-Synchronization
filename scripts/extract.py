import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse("../data/source_catalog.xml")

# Get the root element
root = tree.getroot()

# Loop through all products
for product in root.findall("product"):

    product_id = product.find("id").text
    name = product.find("name").text
    price = product.find("price").text
    date = product.find("date").text

    print("ID:", product_id)
    print("Name:", name)
    print("Price:", price)
    print("Date:", date)
    print("-------------------")