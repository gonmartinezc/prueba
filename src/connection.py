# src/connection.py

import requests

HEADERS = {
    "User-Agent": "Alberto Paramio Galisteo (aparamio@uoc.edu) - "
                  "SEC Scraper for academic use",
    "Accept-Encoding": "gzip, deflate"
}

TEST_CIK = "0000320193"  # Apple Inc.
URL = f"https://data.sec.gov/submissions/CIK{TEST_CIK}.json"


def validate_connection():
    print(f"Testing connection to: {URL}")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            print("SUCCESS: Connected to SEC.")
            return True
        else:
            print(f"Unexpected status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"Connection failed: {e}")
        return False


if __name__ == "__main__":
    validate_connection()

