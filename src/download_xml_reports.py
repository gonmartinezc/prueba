import os
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List

HEADERS = {
    "User-Agent": "Alberto Paramio Galisteo (aparamio@uoc.edu) - SEC Scraper for academic use",
    "Accept-Encoding": "gzip, deflate"
}

def transform_htm_to_xml_url(filing_url: str) -> str:
    """
    Transforms a .htm filing_url to the corresponding _htm.xml URL.
    """
    if filing_url.endswith(".htm"):
        return filing_url.replace(".htm", "_htm.xml")
    return filing_url

def download_xml_reports(filings_df: pd.DataFrame, output_dir: str, retries: int = 2) -> None:
    os.makedirs(output_dir, exist_ok=True)
    for _, row in filings_df.iterrows():
        cik = row["cik"].lstrip("0")
        ticker = row.get("ticker", "UNKNOWN")
        filing_url = row["filing_url"]

        print(f"Processing: {ticker} ({cik})")

        xml_url = transform_htm_to_xml_url(filing_url)
        filename = os.path.basename(xml_url)
        output_path = os.path.abspath(os.path.join(output_dir, filename))

        if os.path.exists(output_path):
            print(f"✔ File already exists: {filename}")
            continue

        for attempt in range(retries + 1):
            try:
                response = requests.get(xml_url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"✔ Downloaded: {filename}")
                break
            except Exception as e:
                if attempt < retries:
                    print(f"Retrying ({attempt + 1}/{retries}) for {filename}")
                    time.sleep(random.uniform(1, 2))
                else:
                    print(f"❌ Failed to download {filename}: {e}")
        time.sleep(random.uniform(1, 2.5))

def main():
    TICKER_FILE = "../dataset/tickers/tickers_prueba.txt"
    COMPANY_LIST_FILE = "../dataset/company_list.csv"
    OUTPUT_DIR = "../dataset/xml_reports"
    REPORT_TYPE = 1  # 0 = both, 1 = 10-K, 2 = 10-Q
    YEAR = 2023
    QUARTER = 0  # 0 = all

    def read_ticker_list(file_path: str) -> List[str]:
        with open(file_path, "r") as f:
            return [line.strip().upper() for line in f if line.strip()]

    def map_tickers_to_ciks(tickers: List[str], company_list_path: str) -> pd.DataFrame:
        df = pd.read_csv(company_list_path, dtype={"cik": str})
        df = df[df["ticker"].isin(tickers)].copy()
        df["cik"] = df["cik"].str.zfill(10)
        return df

    def load_filing_datasets(report_type: int) -> pd.DataFrame:
        if report_type == 1:
            return pd.read_csv("../dataset/10k_filings.csv", dtype={"cik": str})
        elif report_type == 2:
            return pd.read_csv("../dataset/10q_filings.csv", dtype={"cik": str})
        elif report_type == 0:
            df1 = pd.read_csv("../dataset/10k_filings.csv", dtype={"cik": str})
            df2 = pd.read_csv("../dataset/10q_filings.csv", dtype={"cik": str})
            return pd.concat([df1, df2], ignore_index=True)
        else:
            raise ValueError("report_type must be 0 (all), 1 (10-K), or 2 (10-Q)")

    def filter_filings(df: pd.DataFrame, ciks: List[str], year: int, quarter: int) -> pd.DataFrame:
        df["year"] = pd.to_datetime(df["filing_date"]).dt.year
        df["month"] = pd.to_datetime(df["filing_date"]).dt.month
        filtered = df[df["cik"].isin(ciks)]

        if year != 0:
            filtered = filtered[filtered["year"] == year]

        if quarter in [1, 2, 3, 4]:
            quarter_map = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}
            start_m, end_m = quarter_map[quarter]
            filtered = filtered[(filtered["month"] >= start_m) & (filtered["month"] <= end_m)]

        return filtered

    tickers = read_ticker_list(TICKER_FILE)
    df_company = map_tickers_to_ciks(tickers, COMPANY_LIST_FILE)
    cik_list = df_company["cik"].tolist()

    filings = load_filing_datasets(REPORT_TYPE)
    filtered = filter_filings(filings, cik_list, YEAR, QUARTER)
    filtered = filtered.merge(df_company[["cik", "ticker"]], on="cik", how="left")

    download_xml_reports(filtered, OUTPUT_DIR)

if __name__ == "__main__":
    main()



