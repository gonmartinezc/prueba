"""
Module: extract_10k_filings
Description: Parses SEC index.json files from dataset/index_json/
and extracts metadata about all 10-K filings.
"""

import os
import json
import pandas as pd
from typing import List, Dict


def extract_10k_from_file(json_path: str) -> List[Dict]:
    """
    Extracts 10-K filings metadata from a single index.json file.

    Args:
        json_path (str): Path to a company's index.json file

    Returns:
        List[Dict]: List of extracted 10-K filing records
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    filings = data.get("filings", {}).get("recent", {})
    cik = data.get("cik", "UNKNOWN")

    results = []
    for i, form_type in enumerate(filings.get("form", [])):
        if form_type != "10-K":
            continue

        accession_raw = filings["accessionNumber"][i]
        filing_date = filings["filingDate"][i]
        primary_doc = filings["primaryDocument"][i]

        # Build URL
        accession_clean = accession_raw.replace("-", "")
        base_url = (f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                    f"{accession_clean}")
        filing_url = f"{base_url}/{primary_doc}"

        results.append({
            "cik": cik,
            "accession_number": accession_raw,
            "filing_date": filing_date,
            "form": form_type,
            "filing_url": filing_url
        })

    return results


def extract_all_10k(index_json_dir: str) -> pd.DataFrame:
    """
    Processes all index.json files and collects 10-K filing info.

    Args:
        index_json_dir (str): Directory containing CIK index.json files

    Returns:
        pd.DataFrame: All 10-K filings across companies
    """
    all_10k = []

    for filename in os.listdir(index_json_dir):
        if filename.endswith(".json"):
            full_path = os.path.join(index_json_dir, filename)
            records = extract_10k_from_file(full_path)
            all_10k.extend(records)

    df = pd.DataFrame(all_10k)
    return df


if __name__ == "__main__":
    INPUT_DIR = "../dataset/index_json"
    OUTPUT_FILE = "../dataset/10k_filings.csv"

    df_10k = extract_all_10k(INPUT_DIR)
    df_10k.to_csv(OUTPUT_FILE, index=False)
    print(f"Extracted {len(df_10k)} 10-K filings.")
    print(f"Saved to: {OUTPUT_FILE}")
