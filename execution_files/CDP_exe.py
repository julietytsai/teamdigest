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
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent


ua = UserAgent()
user_agent = ua.random

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dve-shm-uage')
options.add_argument('ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'user-agent={user_agent}')

def page_login():
    url = 'https://www.cdp.net/en/users/sign_in'
    
    ua = UserAgent()
    user_agent = ua.random

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dve-shm-uage')
    options.add_argument('ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f'user-agent={user_agent}')

    
    bot = webdriver.Chrome(options=options) # options=options
    wait = WebDriverWait(bot, 20)
    bot.get(url)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#onetrust-accept-btn-handler"))).click()
    time.sleep(1)

    bot.find_element(By.ID, 'user_email').send_keys(username)
    bot.find_element(By.ID, 'user_password').send_keys(password)
    button = bot.find_element(By.CSS_SELECTOR, "button[type='submit']")
    button.click()
    time.sleep(1)

    return bot

def search_company(bot, company_name):

    time.sleep(5)

    bot.get('https://www.cdp.net/en/scores')

    try:
        popup_button = WebDriverWait(bot, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ga-track-regional-popup-item-north-america"))
        )
        popup_button.click()
        time.sleep(1)  # Waiting for 1 second after the click

    except TimeoutException:
        pass  # If the button does not appear, do nothing and continue

    # popup_button = bot.find_element(By.CLASS_NAME, "ga-track-regional-popup-item-north-america")
    # popup_button.click()
    # time.sleep(1)

    input_box = bot.find_element(By.ID, "queries_name")
    input_box.send_keys(company_name)
    submit_button = bot.find_element(By.CLASS_NAME, "response_search_form--btn")
    submit_button.click()

    link = bot.find_element(By.CSS_SELECTOR, "a.pagination__per_page--selected")
    href = link.get_attribute('href')
    href = href.replace('page=5', 'page=20')
    bot.get(href)

    time.sleep(5)

    return bot

def scraper(bot, year, company_name):
    time.sleep(1)
    # Use WebDriverWait for a more efficient wait
    try:
        WebDriverWait(bot, 5).until(EC.presence_of_element_located((By.ID, "challenge-stage"))).click()
    except NoSuchElementException:
        pass  # If the element is not found, do nothing and continue
    except TimeoutException:
        pass  # If the wait times out, do nothing and continue

    # Find the table by its class name (or other suitable selector)
    table = bot.find_element(By.CLASS_NAME, "sortable_table")

    # Extract all rows from the table
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Initialize lists to store data and hrefs
    data = []
    hrefs = []

    # Extract data from each row
    for row in rows[1:]:  # Skip the header row
        cols = row.find_elements(By.TAG_NAME, "td")
        row_data = []
        row_hrefs = []
        for i, col in enumerate(cols):
            links = col.find_elements(By.TAG_NAME, "a")
            if links:
                # Extract text and href for each link
                link_text = links[0].text
                link_href = links[0].get_attribute('href')
                row_data.append(link_text)
                row_hrefs.append(link_href)
            else:
                # If no link, add the text and a None for href
                row_data.append(col.text)
                row_hrefs.append(None)
        
        data.append(row_data)
        hrefs.append(row_hrefs)

    # Create a DataFrame from the extracted data
    column_headers = [col.text for col in rows[0].find_elements(By.TAG_NAME, "th")]
    df = pd.DataFrame(data, columns=column_headers)

    # Add the hrefs as a new column
    df['Response Links'] = pd.Series([href[1] for href in hrefs])

    df = df[df['Year'] == year]
    df = df[df['Name'].str.contains(company_name, case=False)]

    return df
    

def find_section(row):

    try:
        WebDriverWait(bot, 5).until(EC.presence_of_element_located((By.ID, "challenge-stage"))).click()
    except NoSuchElementException:
        time.sleep(10)  # If the element is not found, do nothing and continue
    except TimeoutException:
        time.sleep(10)  # If the wait times out, do nothing and continue

    if 'Climate Change' in row['Response']:
        bot.get(row['Response Links'])

        WebDriverWait(bot, 10).until(EC.visibility_of_element_located((By.ID, 'formatted_responses_section_31715')))
        scraped_text = bot.find_element(By.ID, 'formatted_responses_section_31715').text

    elif 'Forest' in row['Response']:
        bot.get(row['Response Links'])

        WebDriverWait(bot, 10).until(EC.visibility_of_element_located((By.ID, 'formatted_responses_section_90809')))
        scraped_text = bot.find_element(By.ID, 'formatted_responses_section_90809').text    

    elif 'Water Security' in row['Response']:
        bot.get(row['Response Links'])

        WebDriverWait(bot, 10).until(EC.visibility_of_element_located((By.ID, 'formatted_responses_section_31639')))
        scraped_text = bot.find_element(By.ID, 'formatted_responses_section_31639').text   

    else:
        scraped_text = 'Unknown Response Type'

    return scraped_text


def merge_table(tb1, tb2):
    return pd.concat([tb1, tb2], axis = 0)
    
def apply_scraping(df):
    global bot, company_name

    try:

        df['text'] = df.apply(find_section, axis=1)

    except Exception:
        df['text'] = ''
        
    return df 

if __name__ == "__main__":

    username = 'bensshieh21@proton.me'
    password = 'kCT$!7Tzaw4cFJK'

    year = '2023'

    # Read the company names in the master sheet.
    master_idx = pd.read_excel("master_excel_all_variables.xlsx")
    company_list = master_idx['company_id_spciq']


    # Important: This process could fail due to the hcaptcha mechanism of CDP website. 
    # If the website has blocked your bot, please wait at least 5 minutes and start the scraping again.
    sus = pd.DataFrame()
    for company_name in company_list:
        bot = page_login()
        bot = search_company(bot, company_name)
        df = scraper(bot, year, company_name)
        df = apply_scraping(df)
        sus = merge_table(sus, df)

    sus.to_excel('sustainability.xlsx', index=False)