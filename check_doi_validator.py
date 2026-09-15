#!/usr/bin/env python3
"""
DOI Validator untuk 76 Referensi Modul IoT
Memeriksa validitas DOI dan mengambil metadata dari CrossRef API

Usage:
    python check_doi_validator.py

Requirements:
    pip install requests
"""

import requests
import json
import time
from typing import Dict, List, Tuple

# List DOI yang akan dicek (MDPI Sensors, IEEE, Elsevier, dll.)
DOI_LIST = [
    # Sensors (MDPI) - format: 10.3390/s{volume}{issue}{article}
    ("1", "10.3390/s22030995", "Ali et al., Sensors 2022"),
    ("2", "10.3390/s22155836", "Mirani et al., Sensors 2022"),
    ("3", None, "Soori et al., IoT and CPS 2023 - ELSEVIER"),
    ("4", "10.3390/en16083465", "Mansour et al., Energies 2023"),
    ("5", "10.3390/s21154951", "Devan et al., Sensors 2021"),
    ("6", "10.3390/s24082509", "Islam et al., Sensors 2024"),
    ("7", "10.1109/JIOT.2022.3176394", "Marini et al., IEEE IoT Journal 2022"),
    ("9", "10.1109/TICPS.2023.3299032", "Feng & Hu, IEEE TCPS 2023"),
    ("14", "10.3390/app11114879", "Silva et al., Applied Sciences 2021"),
    ("15", "10.1109/ACCESS.2021.3092512", "Merabtine et al., IEEE Access 2021"),
    ("16", "10.3390/electronics11152282", "Behera et al., Electronics 2022"),
    ("18", "10.1016/j.cosrev.2023.100549", "Hazra et al., Computer Science Review 2023"),
    ("19", "10.3390/informatics11040071", "Andriulo et al., Informatics 2024"),
    ("20", "10.1109/COMST.2023.3234072", "Kar et al., IEEE CST 2023"),
    ("21", "10.1016/j.future.2021.11.011", "Rana et al., FGCS 2022"),
    ("22", "10.1109/COMST.2024.3374901", "Ghaleb et al., IEEE CST 2026"),
    ("23", "10.1109/JIOT.2025.XXXXXXX", "Mohammed et al., IEEE IoT 2025"),
    ("24", "10.1016/j.eswa.2022.116703", "Jabbar et al., Expert Systems 2022"),
    ("25", "10.3390/s23146332", "Križanović et al., Sensors 2023"),
    ("26", "10.3390/s22041638", "Fedullo et al., Sensors 2022"),
    ("28", "10.1109/COMST.2024.3466230", "Zanbouri et al., IEEE CST 2025"),
    ("29", "10.1109/MCOMSTD.2021.2100017", "Hamidi-Sepehr et al., IEEE CS Magazine 2021"),
    ("30", "10.1109/OJIES.2021.3135524", "Atiq et al., IEEE OJIES 2022"),
    ("31", "10.3390/en14154497", "Kang et al., Energies 2021"),
    ("32", "10.1109/ACCESS.2022.3209110", "Bouzidi et al., IEEE Access 2022"),
    ("33", "10.1109/TLA.2022.9667146", "Mazon-Olivo & Pan, IEEE LATAM 2022"),
    ("34", "10.1016/j.compind.2021.103469", "Semeraro et al., Computers in Industry 2021"),
    ("35", "10.1016/j.jmsy.2021.05.011", "Leng et al., J. Manufacturing Systems 2021"),
    ("36", "10.1007/s10845-022-01957-9", "Rosati et al., J. Intelligent Manufacturing 2022"),
    ("37", "10.3390/eng4030103", "Romanssini et al., Eng 2023"),
    ("38", "10.1007/s10462-022-10293-3", "Tama et al., AI Review 2022"),
    ("39", "10.1109/ACCESS.2024.3368102", "Gawde et al., IEEE Access 2024"),
    ("40", "10.3390/s25216610", "Kolok et al., Sensors 2025"),
    ("41", "10.3390/s25041006", "Aminzadeh et al., Sensors 2025"),
    ("42", "10.3390/iot3040028", "Ladegourdie & Kua, IoT 2022"),
    ("43", "10.1016/j.jii.2024.100602", "Busboom, J. Industrial Info Integration 2024"),
    ("45", "10.1016/j.jii.2023.100482", "Martins et al., J. Industrial Info Integration 2023"),
    ("48", "10.1109/LES.2024.3376832", "Becoña et al., IEEE Embedded Systems Letters 2024"),
    ("49", "10.1109/ACCESS.2022.3205838", "Perez et al., IEEE Access 2022"),
    ("50", "10.1016/j.rineng.2025.105866", "Khalifeh et al., Results in Engineering 2025"),
    ("51", "10.1109/COMST.2021.3066908", "Centenaro et al., IEEE CST 2021"),
    ("52", "10.1109/ACCESS.2022.3189816", "Alvarez et al., IEEE Access 2022"),
    ("53", "10.1109/TAES.2024.3370738", "Talgat et al., IEEE Trans. Aerospace 2024"),
    ("54", "10.3390/s24175818", "Vandervelden et al., Sensors 2024"),
    ("55", "10.1145/3418295", "Jung et al., CACM 2021"),
    ("56", "10.1145/3696456.3696490", "Sharma et al., ACM CCS 2024"),
    ("58", "10.1016/j.comcom.2021.09.003", "Laroui et al., Computer Communications 2021"),
    ("59", "10.1109/COMST.2023.3329445", "Walia et al., IEEE CST 2024"),
    ("60", "10.3390/mi13060851", "Alajlan & Ibrahim, Micromachines 2022"),
    ("61", "10.1109/MCAS.2023.3273801", "Lin et al., IEEE CAS Magazine 2023"),
    ("62", "10.1016/j.jksuci.2022.03.005", "Ray, J. King Saud Univ. 2022"),
    ("63", "10.1109/ACCESS.2022.3202331", "Zaidi et al., IEEE Access 2022"),
    ("64", "10.3390/s26082550", "Alharthi et al., Sensors 2026"),
    ("65", "10.1016/j.iot.2024.101153", "Oliveira et al., Internet of Things 2024"),
    ("67", "10.1109/JIOT.2024.3497577", "Yalli et al., IEEE IoT Journal 2025"),
    ("68", "10.1109/ACCESS.2024.3387876", "Hasan et al., IEEE Access 2024"),
    ("69", "10.1109/JIOT.2022.3221520", "Roy et al., IEEE IoT Journal 2023"),
    ("70", "10.3390/s21062016", "Gonzalez Viejo et al., Sensors 2021"),
    ("71", "10.1016/j.sbsr.2024.100632", "Astuti et al., Sensing and Bio-Sensing Research 2024"),
    ("72", "10.3390/chemosensors13010023", "Mutz et al., Chemosensors 2025"),
    ("73", "10.1002/advs.202401329", "Jang et al., Advanced Science 2024"),
    ("74", "10.30630/joiv.7.3.1667", "Susanti et al., JOIV 2023"),
    ("75", "10.1109/JIOT.2023.3289614", "Ye et al., IEEE IoT Journal 2024"),
    ("76", "10.58417/jrc.v6i5.1775", "Dewatama et al., JRC 2025"),
]

def check_doi(doi: str) -> Tuple[bool, Dict]:
    """
    Memeriksa DOI menggunakan CrossRef API
    Returns: (is_valid, metadata)
    """
    if doi is None or "XXXXXXX" in doi:
        return False, {"error": "DOI not provided or incomplete"}
    
    url = f"https://api.crossref.org/works/{doi}"
    headers = {
        "User-Agent": "IoT-Module-DOI-Validator/1.0 (mailto:research@university.edu)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            
            # Extract relevant metadata
            metadata = {
                "title": message.get("title", [""])[0] if message.get("title") else "",
                "authors": [
                    f"{author.get('given', '')} {author.get('family', '')}"
                    for author in message.get("author", [])[:3]  # First 3 authors
                ],
                "published": message.get("published", {}).get("date-parts", [[None]])[0],
                "container_title": message.get("container-title", [""])[0] if message.get("container-title") else "",
                "volume": message.get("volume", ""),
                "issue": message.get("issue", ""),
                "page": message.get("page", ""),
                "doi": message.get("DOI", ""),
                "url": message.get("URL", "")
            }
            return True, metadata
        else:
            return False, {"error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def main():
    print("=" * 80)
    print("DOI VALIDATOR - 76 REFERENSI MODUL IoT")
    print("=" * 80)
    print()
    
    results = {
        "valid": [],
        "invalid": [],
        "not_provided": []
    }
    
    for ref_num, doi, description in DOI_LIST:
        print(f"[{ref_num}] Checking: {description}")
        
        if doi is None:
            print(f"    ⚠️  DOI not provided - needs manual verification")
            results["not_provided"].append((ref_num, description))
        elif "XXXXXXX" in doi:
            print(f"    ⚠️  DOI incomplete: {doi}")
            results["invalid"].append((ref_num, doi, description, "Incomplete DOI"))
        else:
            is_valid, metadata = check_doi(doi)
            
            if is_valid:
                print(f"    ✅ VALID: {doi}")
                print(f"       Title: {metadata['title'][:60]}...")
                if metadata['published']:
                    print(f"       Published: {metadata['published']}")
                print(f"       Journal: {metadata['container_title']}")
                results["valid"].append((ref_num, doi, description, metadata))
            else:
                print(f"    ❌ INVALID: {doi}")
                print(f"       Error: {metadata.get('error', 'Unknown error')}")
                results["invalid"].append((ref_num, doi, description, metadata.get('error', 'Unknown')))
        
        print()
        time.sleep(1)  # Rate limiting - CrossRef API courtesy
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Valid DOIs: {len(results['valid'])}")
    print(f"❌ Invalid DOIs: {len(results['invalid'])}")
    print(f"⚠️  Not Provided: {len(results['not_provided'])}")
    print()
    
    # Invalid DOIs
    if results['invalid']:
        print("\n❌ INVALID DOIs (requires attention):")
        for ref_num, doi, desc, error in results['invalid']:
            print(f"  [{ref_num}] {doi} - {desc}")
            print(f"        Error: {error}")
    
    # Not provided
    if results['not_provided']:
        print("\n⚠️  DOIs NOT PROVIDED (manual verification needed):")
        for ref_num, desc in results['not_provided']:
            print(f"  [{ref_num}] {desc}")
    
    # Save to file
    output_file = "doi_validation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Results saved to: {output_file}")

if __name__ == "__main__":
    main()
