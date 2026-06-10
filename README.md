# ETL-Catalog-Synchronization

## Project Overview

This project simulates an ETL (Extract, Transform, Load) pipeline for catalog synchronization between two XML systems.

The goal is to:
- Read a source XML catalog
- Detect and clean incorrect data
- Transform the data into a target XML structure
- Validate the final XML using an XSD schema
- Generate an XML error report

---

## Current Progress

### 1. Created a Source XML Catalog

A `source_catalog.xml` file was created containing around 100 products with intentionally messy and invalid data to simulate real-world data quality issues.

---

## Errors Added Intentionally

The source XML contains several types of incorrect data, including:

- Empty product names
- Extra spaces in names
- Inconsistent capitalization
- Special characters (`###`)
- Missing prices
- Invalid prices (`N/A`)
- Negative prictection
- Invalid date formats
- Mixed date formats
- Missing categories
- Invalid category names
- Concatenated product names (`LaptopHP`, `MonitorDell`, etc.)
---

## Example of Messy Data

```xml
<product>
    <id>1</id>
    <name> Monitor Dell### </name>
    <price>N/A</price>
    <date>04/02/2026</date>
    <category />
</product>
## Student 2 — Data Cleaning & Error De
Implemented features:

- Cleaning product names
- Cleaning prices
- Normalizing date formats
- Cleaning categories
- Detecting invalid or missing data
- Generating XML error reports

Generated file:

- data/error_report.xml

Main script:

- scripts/Clean.py