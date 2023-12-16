import requests
import pandas as pd

class CIKScraper():
    def __init__(self, tickers, headers):
        self.ticker = tickers
        self.company = None
        self.headers = headers
        self.cik = None

    def parsing_tickers(self):
        url = "https://www.sec.gov/files/company_tickers.json"

        tickers_cik = requests.get(url, headers = self.headers)

        tickers_cik = pd.json_normalize(pd.json_normalize(tickers_cik.json(),max_level=0).values[0])
        tickers_cik["cik_str"] = tickers_cik["cik_str"].astype(str)
        ticker_table = tickers_cik[tickers_cik["ticker"]==self.ticker]
        self.cik = ticker_table["cik_str"].values[0]
        self.company = ticker_table["title"].values[0]
        return ticker_table
    


if __name__ == "__main__":

    headers = {"User-Agent": "bxie43@wisc.edu"}
    year = '2023'
    FILE = '10-K'

    company = CIKScraper("GIS", headers)[0]
    company.parsing_tickers()
