import re
import requests
import xml.etree.ElementTree as ET

registry_api_url = "https://registry.api.identifiers.org/restApi/namespaces"
response = requests.get(registry_api_url)
namespace_data = response.json()

namespace_patterns = {ns["prefix"]: ns["pattern"] for ns in namespace_data}

text = """
The raw reads of the 30 ST22 S. aureus genomes sequenced in this study were deposited in GenBank under BioProject accession no. PRJNA929648.

The Kibdelosporangium philippinense ATCC 49844T whole genome shotgun sequence (WGS) project has been deposited at DDBJ/ENA/GenBank under accession JAJVCN000000000. The raw data from BioProject PRJNA790681 were submitted to the NCBI Sequence Read Archive (SRA) under three experiment accession numbers: SRX13551729 (Illumina fastq files), SRX13555714 (Nanopore reads in fastq format), and SRX13556647 (Nanopore reads in fast5 format).

The complete genome sequences were deposited in National Center for Biotechnology Information (NCBI) under the accession number CP110363 (https://www.ncbi.nlm.nih.gov/nuccore/CP110363). The raw sequences obtained from Nanopore PromethION sequencer were deposited in the Sequence Read Archive under the BioProject PRJNA895949 (https://www.ncbi.nlm.nih.gov/bioproject/PRJNA895949). The raw sequences obtained from DNBSEQ-T7RS platform were deposited in the Sequence Read Archive under the BioProject PRJNA898672 (https://www.ncbi.nlm.nih.gov/bioproject/PRJNA898672).
"""

accession_numbers = re.findall(r'\b[A-Z]+\d+\b', text)

xml_tags = []

for accession_number in accession_numbers:
    namespace = None
    compact_identifier = None
    resolved_url = None
    
    for prefix, pattern in namespace_patterns.items():
        if re.match(pattern, accession_number):
            namespace = prefix
            compact_identifier = f"{prefix}:{accession_number}"
            break
    
    if namespace:
        resolver_api_url = f"https://resolver.api.identifiers.org/{compact_identifier}"
        response = requests.get(resolver_api_url)
        resolved_data = response.json()
        
        if resolved_data["resolvedUrl"]:
            resolved_url = resolved_data["resolvedUrl"]
    
    if resolved_url:
        xml_tag = ET.Element("ext-link", {
            "ext-link-type": "uri",
            "assigning-authority": namespace,
            "xlink:href": resolved_url
        })
        xml_tag.text = accession_number
        xml_tags.append(xml_tag)

formatted_output = "\n".join([ET.tostring(tag).decode() for tag in xml_tags])
print(formatted_output)
