"""
Module: test_sec_connection
Description: Simple script to test connection to SEC's index.json with proper
headers.
"""

import requests

HEADERS = {
    "User-Agent": "Alberto Paramio Galisteo (aparamio@uoc.edu) - "
                  "SEC Scraper for academic use",
    "Accept-Encoding": "gzip, deflate"
}

TEST_CIK = "0000320193"  # Apple Inc.
URL = f"https://data.sec.gov/submissions/CIK{TEST_CIK}.json"


def test_sec_connection():
    print(f"🔍 Testing connection to: {URL}")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")

        if response.status_code == 200:
            print("SUCCESS: Connected and received valid response from SEC.")
            print(f"First 200 characters of content:\n{response.text[:200]}")
        elif response.status_code == 404:
            print("Not Found (404): URL is correct, but the SEC returned "
                  "no data.")
        else:
            print(f"Unexpected response: {response.status_code}")

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    test_sec_connection()
