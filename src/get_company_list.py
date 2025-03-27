"""
Module: get_company_list
Description: Parses company_tickers.json from the SEC and creates a CSV with
CIK, ticker, and company name.
"""

import json
import pandas as pd
from typing import List, Dict


def load_company_list(json_path: str) -> pd.DataFrame:
    """
    Loads the company_tickers.json file and returns a structured DataFrame.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        pd.DataFrame: DataFrame with columns: cik, ticker, title
    """
    with open(json_path, 'r') as f:
        data: Dict = json.load(f)

    companies: List[Dict[str, str]] = []
    for item in data.values():
        cik_str = str(item['cik_str']).zfill(10)  # Pad CIK to 10 digits
        companies.append({
            'cik': cik_str,
            'ticker': item['ticker'],
            'title': item['title']
        })

    df = pd.DataFrame(companies)
    return df


if __name__ == "__main__":
    input_path = "../dataset/company_tickers.json"
    output_path = "../dataset/company_list.csv"

    df_companies = load_company_list(input_path)
    print(df_companies.head())

    df_companies.to_csv(output_path, index=False)
    print(f"Company list saved to: {output_path}")
