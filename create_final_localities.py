#!/usr/bin/env python3
"""
Create Final Localities Script
Manually curate the main localities for the database
"""

import pandas as pd

def create_final_localities():
    """Create a curated list of main localities"""
    
    # Main localities that are actual places (manually curated)
    main_localities = [
        # Major areas around Weija
        "KASOA",
        "WEIJA", 
        "GBAWE",
        "ABLEKUMA",
        "AWOSHIE",
        "MALLAM",
        "MCCARTHY",
        "ODORKOR",
        "KWASHIEMAN",
        "TETEGU",
        "TUBA",
        "BORTIANOR",
        "DANSOMAN",
        "SOWUTUOM",
        "LAPAZ",
        "AMANFROM",
        "AMASAMAN",
        "KOKROBITE",
        "APLAKU",
        "KWASHIEBU",
        "DARKUMAN",
        "TABORA",
        "OFANKOR",
        "GALILEA",
        "SAKAMAN",
        "MATAHEKO",
        "POKUASE",
        "OMANJOR",
        "BUBIASHIE",
        "TEMA",
        "KANESHIE",
        "AWUTU",
        "ABEKA",
        "OLEBU",
        "DOME",
        "AGONA",
        "ADENTA",
        "KALABULE",
        "PALAS",
        "TESHIE",
        "BAWJIASE",
        "FANMILK",
        "KWAHU",
        "BUSIA",
        "PALACE",
        "LIBERIA",
        "BRIGADE",
        "MENSKROM",
        
        # Additional areas that might be valid
        "NIC",
        "CHOICE",
        "BARRIER",
        "SAMPA",
        "ODOKOR",
        "SOWUTOUM",
        "GBEWE",
        "AWOSHI",
        "MACCARTHY",
        "BLOCKFACTORY",
        "MCCHARTHY",
        "MCCATHY",
        "KWASHIMAN",
        "MALLA",
        "DJAMAN",
        "BAAH",
        "MALAM",
        "GALELIA",
        "ODORKO",
        "TATOP",
        "TABOLA",
        "KAOSA",
        "SOWUTUM",
        "MCARTHY",
        
        # Major cities/regions
        "ACCRA",
        "AMANFRO"
    ]
    
    # Remove duplicates and sort
    main_localities = sorted(list(set(main_localities)))
    
    # Create DataFrame
    final_localities = pd.DataFrame([
        {
            'locality': locality,
            'orgname': 'weija',
            'created_at': pd.Timestamp.now(),
            'updated_at': pd.Timestamp.now()
        }
        for locality in main_localities
    ])
    
    # Save to CSV
    output_file = 'final_localities_for_db.csv'
    final_localities.to_csv(output_file, index=False)
    
    print(f"Created final localities CSV: {output_file}")
    print(f"Total localities: {len(final_localities)}")
    print("\nFinal localities:")
    for locality in main_localities:
        print(f"  - {locality}")
    
    return final_localities

def create_mapping_from_original():
    """Create a mapping from original localities to final localities"""
    
    # Load the original mapping
    try:
        import json
        with open('locality_to_main_mapping.json', 'r') as f:
            original_mapping = json.load(f)
    except FileNotFoundError:
        print("Original mapping file not found. Run extract_main_localities.py first.")
        return
    
    # Load final localities
    final_localities = pd.read_csv('final_localities_for_db.csv')
    final_locality_set = set(final_localities['locality'].tolist())
    
    # Create new mapping
    new_mapping = {}
    for original, extracted in original_mapping.items():
        if extracted in final_locality_set:
            new_mapping[original] = extracted
        else:
            # Try to find a close match
            for final_loc in final_locality_set:
                if final_loc in extracted or extracted in final_loc:
                    new_mapping[original] = final_loc
                    break
            else:
                # Default to Unknown if no match found
                new_mapping[original] = 'Unknown'
    
    # Save new mapping
    with open('final_locality_mapping.json', 'w') as f:
        json.dump(new_mapping, f, indent=2)
    
    print(f"\nCreated final mapping with {len(new_mapping)} entries")
    print("Saved to: final_locality_mapping.json")

if __name__ == "__main__":
    print("Creating final curated localities...")
    final_localities = create_final_localities()
    create_mapping_from_original()
    print("\nDone!") 