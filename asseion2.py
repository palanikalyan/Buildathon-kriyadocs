import re
import requests
import xml.etree.ElementTree as ET

def identify_accession_numbers(text):
  """Identifies the accession numbers in the text and returns a list of them."""
  accession_numbers = []
  accession_number_patterns = [
      re.compile(r"^[A-Za-z]\d{5}$"),
      re.compile(r"^[A-Za-z]{2}\d{6}$"),
      re.compile(r"^[A-Za-z]{3}\d{7}$"),
  ]
  for accession_number_pattern in accession_number_patterns:
    matches = accession_number_pattern.finditer(text)
    for match in matches:
      accession_numbers.append(match.group(0))
  return accession_numbers

def get_namespace(accession_number):
  """Gets the namespace for the accession number."""
  url = "https://registry.api.identifiers.org/restApi/namespaces/" + accession_number
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    return data["prefix"]
  else:
    return None

def get_url(accession_number, namespace):
  """Gets the URL for the accession number."""
  url = "https://resolver.api.identifiers.org/" + namespace + ":" + accession_number
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    return data["compactIdentifierResolvedURL"]
  else:
    return None

def generate_xml(accession_numbers):
  """Generates the XML output for the accession numbers."""
  root = ET.Element("accession_numbers")
  for accession_number in accession_numbers:
    element = ET.SubElement(root, "accession_number")
    element.set("assigning_authority", get_namespace(accession_number))
    element.set("xlink:href", get_url(accession_number, get_namespace(accession_number)))
    text = ET.SubElement(element, "text")
    text.text = accession_number
  return root

def main():
  text = "The raw reads of the 30 ST22 S. aureus genomes sequenced in this study were deposited in GenBank under BioProject accession no. PRJNA929648."
  accession_numbers = identify_accession_numbers(text)
  xml = generate_xml(accession_numbers)
  print(xml)

if __name__ == "__main__":
  main()
