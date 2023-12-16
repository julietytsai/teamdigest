from docscraping import DocScraper
from cikscraping import CIKScraper
from webscraping import SECScraper
from sec_api import ExtractorApi
import pandas as pd


if __name__ == "__main__":


    headers = {"User-Agent": "bxie43@wisc.edu"}
    FILE = '10-K'
    Year = '2023'
    api_key = '4443770e404975687133744ecfc296d86e74498fc8e5536678eae20c35423505'

    master_idx = pd.read_excel("master_excel_all_variables.xlsx")
    company_list = master_idx['company_ticker']


    regulatory_compliance = pd.DataFrame(columns=['ticker', 'year', 'file', 'regulatory_compliance'])
    product_portfolio = pd.DataFrame(columns=['ticker', 'year', 'file', 'product_portfolio'])
    acquisition_info = pd.DataFrame(columns=['ticker', 'year', 'file', 'acquisition_info'])

    for ticker in company_list:
        try:
            company = CIKScraper(ticker, headers)
            company.parsing_tickers()
            scraper = SECScraper(company.cik, Year, FILE, headers)
            url = scraper.scrape_sec_data()[0]

            try:
                parser = DocScraper(url, FILE, headers, api_key, Year, ticker)
                parser.parsing_file()


                # regulatory_compliance
                data_rc = {
                'ticker': ticker,
                'year': Year,
                'file': FILE,
                'regulatory_compliance': [parser.regulatorycompliance]
                }

                df_rc = pd.DataFrame(data_rc)
                regulatory_compliance = pd.concat([regulatory_compliance, df_rc], axis = 0)


                # product_portfolio
                data_pp = {
                'ticker': ticker,
                'year': Year,
                'file': FILE,
                'product_portfolio': [parser.productportfolio]
                }
                df_pp = pd.DataFrame(data_pp)
                product_portfolio = pd.concat([product_portfolio, df_pp], axis = 0)

                # acquisitions information
                data_ai = {
                'ticker': ticker,
                'year': Year,
                'file': FILE,
                'acquisition_info': [parser.acquisitions]
                }
                df_ai = pd.DataFrame(data_ai)
                acquisition_info = pd.concat([acquisition_info, df_ai], axis = 0)

            except Exception as e:
                print(e)

        except Exception as e:
            print("data is not available in:", ticker) 
            print(e)
            pass