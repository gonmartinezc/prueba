import time
import random
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from typing import List, Dict

HEADERS = {
    "User-Agent": "Alberto Paramio Galisteo (aparamio@uoc.edu) - "
                  "SEC Scraper for academic use",
    "Accept-Encoding": "gzip, deflate"
}


def read_ticker_list(file_path: str) -> List[str]:
    """
    Reads a text file containing tickers, one per line, and returns them as a
    list in uppercase.

    Args:
        file_path (str): Path to the text file containing tickers.

    Returns:
        List[str]: List of ticker symbols in uppercase.
    """
    with open(file_path, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]


def map_tickers_to_ciks(tickers: List[str], company_list_path: str) -> pd.DataFrame:
    """
    Maps a list of ticker symbols to their corresponding CIKs using the company
    list CSV.

    Args:
        tickers (List[str]): List of ticker symbols to filter.
        company_list_path (str): Path to the CSV file containing columns
        'ticker', 'cik', and 'title'.

    Returns:
        pd.DataFrame: Filtered DataFrame with columns 'ticker', 'cik' (padded
        to 10 digits), and any other available metadata.
    """
    df = pd.read_csv(company_list_path, dtype={"cik": str})
    df = df[df["ticker"].isin(tickers)].copy()
    df["cik"] = df["cik"].str.zfill(10)
    return df


def load_filing_datasets(report_type: int) -> pd.DataFrame:
    """
    Loads one or both SEC filing datasets (10-K and/or 10-Q) based on the
    report type.

    Args:
        report_type (int):
            - 1 to load only 10-K filings
            - 2 to load only 10-Q filings
            - 0 to load and combine both 10-K and 10-Q filings

    Returns:
        pd.DataFrame: A DataFrame containing the selected filings, with at
        least columns:
            - cik (string, zero-padded)
            - filing_date
            - form
            - accession_number
            - filing_url

    Raises:
        ValueError: If report_type is not one of 0, 1, or 2.
    """
    if report_type == 1:
        return pd.read_csv("../dataset/10k_filings.csv",
                           dtype={"cik": str})
    elif report_type == 2:
        return pd.read_csv("../dataset/10q_filings.csv",
                           dtype={"cik": str})
    elif report_type == 0:
        df1 = pd.read_csv("../dataset/10k_filings.csv",
                          dtype={"cik": str})
        df2 = pd.read_csv("../dataset/10q_filings.csv",
                          dtype={"cik": str})
        return pd.concat([df1, df2], ignore_index=True)
    else:
        raise ValueError("report_type must be 0 (all), 1 (10-K), or 2 (10-Q)")


def filter_filings(df: pd.DataFrame, ciks: List[str], year: int,
                       quarter: int) -> pd.DataFrame:
    """
    Filters a DataFrame of SEC filings by CIKs, year, and quarter.

    Args:
        df (pd.DataFrame): DataFrame containing filings with at least 'cik' and
        'filing_date' columns.
        ciks (List[str]): List of CIKs (10-digit strings) to include.
        year (int): Year to filter filings by. Use 0 to include all years.
        quarter (int): Quarter to filter by (1–4). Use 0 to include all quarters.

    Returns:
        pd.DataFrame: Filtered DataFrame containing only filings that match the
        provided criteria.
    """
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


def download_and_parse_xbrl(url: str, tags: List[str]) -> Dict[str, str]:
    """
    Downloads an XBRL (XML) file from the SEC and extracts the values of
    specified tags.

    Args:
        url (str): Direct URL to the XBRL (.xml) file.
        tags (List[str]): List of tag names (XBRL elements) to extract from the
        XML content.

    Returns:
        Dict[str, str]: Dictionary where keys are tag names and values are the
        extracted text content.
        If a tag is not found, it will not be included in the result.
        Returns an empty dictionary if download or parsing fails.

    Notes:
        - Only top-level tags in the XML are checked.
        - Namespaces are ignored (only the local tag name is considered).
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        data = {}
        for elem in root:
            tag = elem.tag.split("}")[-1]
            if tag in tags:
                data[tag] = elem.text
        return data
    except Exception as e:
        print(f"Error downloading/parsing {url}: {e}")
        return {}


def process_filings(df_filings: pd.DataFrame, tickers_map: Dict[str, str],
                    tags_df: pd.DataFrame, year: int, quarter: int,
                    output_path: str) -> None:
    """
    Processes a list of SEC filings: downloads each XBRL report, extracts specified tags,
    and saves the data to a structured CSV file.

    Args:
        df_filings (pd.DataFrame): DataFrame containing the filtered filings.
                                   Must include 'cik', 'filing_date', and
                                   'filing_url'.
        tickers_map (Dict[str, str]): Dictionary mapping CIKs (as strings) to
        tickers.
        tags_df (pd.DataFrame): DataFrame containing the 'tag_name' column with
        XBRL tags to extract.
        year (int): Year of the filings being processed (used in output
        metadata).
        quarter (int): Quarter (1–4) or 0 for all quarters (used in output
        metadata).
        output_path (str): Path to the CSV file where the results will be saved.

    Returns:
        None

    Notes:
        - Downloads the XBRL XML file for each filing from the SEC.
        - Extracts only the tags listed in `tags_df`.
        - Each row in the output CSV corresponds to one filing.
        - Adds basic metadata: cik, ticker, year, quarter.
        - Includes polite scraping delays to avoid overloading the SEC servers.
    """
    tag_names = tags_df.columns.str.lower().str.strip().tolist()
    if "tag_name" not in tag_names:
        raise ValueError("Column 'tag_name' not found in xbrl_tags.csv")

    tags_df.columns = tag_names  # Normalize headers
    tag_list = tags_df["tag_name"].tolist()

    records = []

    for _, row in df_filings.iterrows():
        cik = row["cik"]
        ticker = tickers_map.get(cik, "UNKNOWN")
        filing_url = row["filing_url"]

        base_url = filing_url.rsplit("/", 1)[0]
        possible_xbrl_url = (base_url + "/" + base_url.split("/")[-1] + "_htm.xml")

        print(f"Processing: {ticker} ({cik})")
        tag_values = download_and_parse_xbrl(possible_xbrl_url, tag_list)

        record = {
            "cik": cik,
            "ticker": ticker,
            "year": pd.to_datetime(row["filing_date"]).year,
            "quarter": quarter if quarter != 0 else "ALL"
        }
        for tag in tag_list:
            record[tag] = tag_values.get(tag, None)
        records.append(record)
        time.sleep(random.uniform(1, 2.5))

    df_result = pd.DataFrame(records)
    df_result.to_csv(output_path, index=False)
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    TICKER_FILE = "../dataset/tickers/tickers_prueba.txt"
    COMPANY_LIST_FILE = "../dataset/company_list.csv"
    TAGS_FILE = "../dataset/xbrl_tags.csv"

    REPORT_TYPE = 1  # 0 = all, 1 = 10-K, 2 = 10-Q
    YEAR = 2024         # 0 = all years
    QUARTER = 0      # 0 = all quarters

    OUTPUT_FILE = (f"../dataset/xbrl_data_{YEAR if YEAR != 0 else 'all'}_"
                   f"{'10k' if REPORT_TYPE == 1 else '10q' if REPORT_TYPE == 2 
                   else '10k_10q'}.csv")

    tickers = read_ticker_list(TICKER_FILE)
    company_df = map_tickers_to_ciks(tickers, COMPANY_LIST_FILE)
    cik_list = company_df["cik"].tolist()
    ticker_map = dict(zip(company_df["cik"], company_df["ticker"]))

    filings = load_filing_datasets(REPORT_TYPE)
    filtered = filter_filings(filings, cik_list, YEAR, QUARTER)
    tags = pd.read_csv(TAGS_FILE)

    process_filings(filtered, ticker_map, tags, YEAR, QUARTER, OUTPUT_FILE)
