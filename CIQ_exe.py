from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
import lxml
import getpass
from IPython.display import display, Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dve-shm-uage')


def page_login(username, password, url):
    bot = webdriver.Chrome(options=options)
    wait = WebDriverWait(bot, 20)
    bot.get(url)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#onetrust-accept-btn-handler"))).click()

    time.sleep(2)

    bot.find_element(By.ID, 'input28').send_keys(username)
    bot.find_element(By.ID, 'input28').send_keys(Keys.RETURN)

    time.sleep(2)

    password_field = bot.find_element(By.ID, 'input60')
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    time.sleep(2)

    return bot   

def get_company_data(bot, company_id, url, tag, idx):
    
    bot.get(url.format(company_id))

    df = None 
    
    try:
        table = bot.find_element(By.ID, tag)

        data = []
        for row in table.find_elements(By.TAG_NAME, "tr"):
            row_data = [cell.text for cell in row.find_elements(By.TAG_NAME, "td")]
            if row_data:
                data.append(row_data)
        headers = data[0]
        non_empty_headers = [header.strip() for header in headers if header]
        cleaned_rows = [[cell for cell in row if cell] for row in data[1:]]
        cleaned_rows = [row for row in cleaned_rows if any(cell for cell in row if cell)]

        if len(cleaned_rows) > 0: # Check if it has multiple rows
            try:
                df = pd.DataFrame(cleaned_rows[1:], columns=non_empty_headers) 
            except ValueError:
                try:
                    df = pd.DataFrame([cleaned_rows[0]], columns=non_empty_headers)  # Ensure this is a list of lists
                except Exception:
                    pass
        else: # Text extraction
            df = pd.DataFrame([table.text.replace('\n\n', ';')], columns = idx)
            
    except NoSuchElementException: # Data not disclosured
        df = pd.DataFrame([" "] * len(idx), index=idx).T
    
    # Only proceed if df is successfully created
    if df is not None:
        df.insert(0, 'company_id', str(company_id))
        if len(df[:-1]) != 0:
            df = df[:-1]

    return df



def merge_tables(tb1, tb2):
    return pd.concat([tb1, tb2], axis = 0)


if __name__ == "__main__":

    customers_url = 'https://www.capitaliq.com/CIQDotNet/BusinessRel/Customers.aspx?CompanyId={}'
    customers_index = ['Customer Name', 'Supplier Name', 'Relationship Type', 'Primary Industry', 'Source']
    customers_tag = 'myCustomersGrid_gridSection_myDataGrid'

    competitors_url = 'https://www.capitaliq.com/CIQDotNet/BusinessRel/Competitors.aspx?CompanyId={}'
    competitors_index = ["Competitor's Name", 'Company', 'LTM Revenue ($mm)', 'LTM Date', 'Source']
    competitors_tag = 'myCompetitorsGrid_gridSection_myDataGrid'

    alliances_url = 'https://www.capitaliq.com/CIQDotNet/BusinessRel/StrategicAlliances.aspx?CompanyId={}'
    alliances_index = ["Strategic Alliance Name", 'Company Name', 'Primary Industry', 'Source']
    alliances_tag = 'myStrategicAlliancesGrid_gridSection_myDataGrid'

    suppliers_url = 'https://www.capitaliq.com/CIQDotNet/BusinessRel/Suppliers.aspx?CompanyId={}'
    suppliers_index = ["Supplier Name", 'Customer Name', 'Relationship Type', 'Primary Industry', 'Source']
    suppliers_tag = 'mySuppliersGrid_gridSection_myDataGrid'


    acquisitions_url = 'https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId={}&transactionViewType=1'
    acquisitions_index = ["Announced Date", 'Closed Date', 'Transaction Type', 'Role', 'Target', 'Buyer/Investors', 'Sellers',
                                                                'Rounds', 'Round Type', 'Pre-Money Valuation ($mm)', 'Post-Money Valuation ($mm)', 'Size ($mm)', 
                                                                'Aggregate Amount Raised ($mm)†']
    acquisitions_tag = 'MATransactionGrid'


    brands_url = 'https://www.capitaliq.com/CIQDotNet/Company/LongBusinessDescription.aspx?CompanyId={}'
    brands_index = ['Business Description and Products']
    brands_tag = 'Displaysection1'

    master_idx = pd.read_csv("Master_sheet - Sheet1.csv")
    company_list = master_idx['company_id_SPCIQ']

    username = 'bxie43@wisc.edu'
    password = 'Ben803803`'
    login_url = 'https://www.capitaliq.com/CIQDotNet/login-okta.aspx'



    bot = page_login(username, password, login_url)

    customers_table = pd.DataFrame()
    for company_id in company_list:
        customers_table = merge_tables(customers_table, get_company_data(bot, company_id, customers_url, customers_tag, customers_index))
    
    competitors_table = pd.DataFrame()
    for company_id in company_list:
        competitors_table = merge_tables(competitors_table, get_company_data(bot, company_id, competitors_url, competitors_tag, competitors_index))

    alliances_table = pd.DataFrame()
    for company_id in company_list:
        alliances_table = merge_tables(alliances_table, get_company_data(bot, company_id, alliances_url, alliances_tag, alliances_index))

    suppliers_table = pd.DataFrame()
    for company_id in company_list:
        suppliers_table = merge_tables(suppliers_table, get_company_data(bot, company_id, suppliers_url, suppliers_tag, suppliers_index))

    acquisitions_table = pd.DataFrame()
    for company_id in company_list:
        acquisitions_table = merge_tables(acquisitions_table, get_company_data(bot, company_id, acquisitions_url, acquisitions_tag, acquisitions_index))

    brands_table = pd.DataFrame()
    for company_id in company_list:
        brands_table = merge_tables(brands_table, get_company_data(bot, company_id, brands_url, brands_tag, brands_index))


    customers_table.to_csv('customers.csv', index=False)
    competitors_table.to_csv('competitors.csv', index=False)
    alliances_table.to_csv('alliances.csv', index=False)
    suppliers_table.to_csv('source_of_raw_materials.csv', index=False)
    acquisitions_table.to_csv('acquisitions.csv', index = False)
    brands_table.to_csv('brands.csv', index=False)

    bot.quit()