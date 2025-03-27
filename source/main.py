"""
Module: main
Description: Orchestrates the complete SEC scraper workflow step by step.
"""

from get_company_list import load_company_list
from download_company_list import download_company_tickers
import os
# import pandas as pd

# Paths
TICKERS_JSON = "../dataset/company_tickers.json"
COMPANY_LIST_CSV = "../dataset/company_list.csv"


def step1_download_and_prepare_company_list():
    """
    Step 1: Download and convert company_tickers.json to a CSV list of
    companies.
    """
    print("Step 1: Downloading and preparing company list...")

    # Download JSON if not already downloaded
    if not os.path.exists(TICKERS_JSON):
        download_company_tickers(TICKERS_JSON)
    else:
        print(f"File already exists: {TICKERS_JSON}")

    # Parse and convert to CSV
    df = load_company_list(TICKERS_JSON)
    df.to_csv(COMPANY_LIST_CSV, index=False)
    print(f"Saved parsed company list to: {COMPANY_LIST_CSV}")


if __name__ == "__main__":
    print("SEC 10-K Scraper Pipeline Started")
    step1_download_and_prepare_company_list()
    print("Step 1 complete.")
