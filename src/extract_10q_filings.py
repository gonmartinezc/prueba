"""
Module: extract_10q_filings
Description: Parses SEC index.json files from dataset/index_json/
and extracts metadata about all 10-Q filings.
"""

import os
import json
import pandas as pd
from typing import List, Dict


def extract_10q_from_file(json_path: str) -> List[Dict]:
    """
    Extracts 10-Q filings metadata from a single index.json file.

    Args:
        json_path (str): Path to a company's index.json file

    Returns:
        List[Dict]: List of extracted 10-Q filing records
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    filings = data.get("filings", {}).get("recent", {})
    cik = data.get("cik", "UNKNOWN")

    results = []
    for i, form_type in enumerate(filings.get("form", [])):
        if form_type != "10-Q":
            continue

        accession_raw = filings["accessionNumber"][i]
        filing_date = filings["filingDate"][i]
        primary_doc = filings["primaryDocument"][i]

        # Build filing URL
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


def extract_all_10q(index_json_dir: str) -> pd.DataFrame:
    """
    Processes all index.json files and collects 10-Q filing info.

    Args:
        index_json_dir (str): Directory containing CIK index.json files

    Returns:
        pd.DataFrame: All 10-Q filings across companies
    """
    all_10q = []

    for filename in os.listdir(index_json_dir):
        if filename.endswith(".json"):
            full_path = os.path.join(index_json_dir, filename)
            records = extract_10q_from_file(full_path)
            all_10q.extend(records)

    df = pd.DataFrame(all_10q)
    return df


if __name__ == "__main__":
    INPUT_DIR = "../dataset/index_json"
    OUTPUT_FILE = "../dataset/10q_filings.csv"

    df_10q = extract_all_10q(INPUT_DIR)
    df_10q.to_csv(OUTPUT_FILE, index=False)
    print(f"Extracted {len(df_10q)} 10-Q filings.")
    print(f"Saved to: {OUTPUT_FILE}")
