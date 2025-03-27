"""
Module: download_company_list
Description: Downloads the official company_tickers.json file from the SEC
website.
"""

import requests
import os


def download_company_tickers(output_path: str) -> None:
    """
    Downloads the company_tickers.json file from the SEC and saves it locally.

    Args:
        output_path (str): Path where the JSON file should be saved.
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        "User-Agent": "MySECProject/1.0 (your_email@example.com)",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov"
    }

    try:
        print(f"Downloading company_tickers.json from {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Ensure output folder exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"Saved to: {output_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")


if __name__ == "__main__":
    output_file = "../dataset/company_tickers.json"
    download_company_tickers(output_file)
