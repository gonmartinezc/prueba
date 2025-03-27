"""
Module: download_index_json
Description: Downloads index.json files for all companies listed
in company_list.csv using their CIKs. Includes polite scraping,
CIK formatting, estimated time calculation, and user confirmation.
"""

import os
import time
import random
import requests
import pandas as pd


HEADERS = {
    "User-Agent": "Alberto Paramio Galisteo (aparamio@uoc.edu) - "
                  "SEC Scraper for academic use",
    "Accept-Encoding": "gzip, deflate"
}


def clean_cik(cik: str) -> str:
    """Ensures the CIK is a 10-digit zero-padded string."""
    return str(cik).split('.')[0].zfill(10)


def estimate_download_time(num_items: int, avg_seconds: float = 2.0) -> float:
    """Estimates total time in seconds for all downloads."""
    return num_items * avg_seconds


def confirm_download_time(seconds: float) -> bool:
    """Displays estimated time and asks user to confirm."""
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    print(f"Estimated download time for full list: {minutes} min {sec} sec")
    response = input("Do you want to continue? (y/n): ").strip().lower()
    return response == "y"


def download_index_json(cik: str, output_dir: str) -> bool:
    """Downloads the index.json for a given CIK and saves it."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    output_path = os.path.join(output_dir, f"{cik}.json")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 404:
            print(f"Skipping: {cik} — Not found (404)")
            return False

        response.raise_for_status()

        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"Downloaded: {cik}")
        return True

    except Exception as e:
        print(f"Error downloading {cik}: {e}")
        return False


def download_all_index_files(csv_path: str, output_dir: str) -> None:
    """
    Downloads index.json files for all companies in the CSV.

    Args:
        csv_path (str): Path to company_list.csv
        output_dir (str): Directory where the files are saved
    """
    df = pd.read_csv(csv_path, dtype={"cik": str})
    total = len(df)

    estimated_time = estimate_download_time(total)
    if not confirm_download_time(estimated_time):
        print("Download cancelled.")
        return

    for index, row in df.iterrows():
        cik = clean_cik(row["cik"])
        download_index_json(cik, output_dir)
        time.sleep(random.uniform(1, 2.5))


if __name__ == "__main__":
    CSV_PATH = "../dataset/company_list.csv"
    OUTPUT_DIR = "../dataset/index_json"
    download_all_index_files(CSV_PATH, OUTPUT_DIR)
