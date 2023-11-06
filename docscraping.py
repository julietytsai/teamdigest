import requests
import re
import html
from cikscraping import CIKScraper
from webscraping import SECScraper
from sec_api import ExtractorApi


def text_preprocessing(text):
    text = html.unescape(text)

    # TABLE_START and ##TABLE_END
    text = re.sub(r'##TABLE_START|##TABLE_END', '', text)

    return text

def regulatory_compliance(item1a):
    # Preprocess Section Item 1A
    text = text_preprocessing(item1a)

    # Remove 
    text = re.sub(r'\n\n', '', text)

    # Define a regular expression pattern to capture risks and their descriptions
    pattern = r'([A-Z][a-zA-Z\s]+ Risks)'

    # Find all matches in the text
    matches = re.findall(pattern, text)

    # Create a dictionary and assign the text behind each risk
    risks_dict = {}
    text_segments = re.split(pattern, text)[1:]

    current_risk = None

    for item in text_segments:
        if item in matches:
            current_risk = item
        elif current_risk is not None:
            risks_dict[current_risk] = item
            current_risk = None

    regulatory_compliance = {key: value for key, value in risks_dict.items() if "legal" in key.lower() or "regulatory" in key.lower()}

    return regulatory_compliance

def product_portofolio(item1a):
    pattern = r'\n\n([A-Za-z, ]+)\n\n'
    matches = re.findall(pattern, item1a)

    intro_dict = {}
    text_segments = re.split(pattern, item1a)[1:]

    # Initialize a dictionary to store the pairs
    title_sentence_pairs = {}
    current_title = None
    current_sentences = []

    # Iterate through the sentences and group them under the titles
    for item in text_segments:
        if item in matches:
            if current_title:
                title_sentence_pairs[current_title] = current_sentences
            current_title = item
            current_sentences = []
        else:
            current_sentences.append(item)

    # Add the last set of sentences
    if current_title:
        title_sentence_pairs[current_title] = ' '.join(current_sentences)

    return title_sentence_pairs

def acquisitions(item8):
    text = text_preprocessing(parser.item8)
    pattern = r'\n\n(.*?acquisition.*?)\n\n'

    #matches = re.findall(pattern, text, re.IGNORECASE)

    #intro_dict = {}
    text_segments = re.split(pattern, text)[1:]

    return text_segments


class DocScraper:
    def __init__(self, url, FILE, headers, api_key, year):
        self.url = url
        self.headers = headers
        self.file = FILE
        self.api_key = api_key
        self.year = year
    
        # Store the item sections within 10-K report
        self.document = None
        self.item1 = None
        self.item1a = None
        self.item2 = None
        self.item7 = None
        self.item8 = None

        # Store the text variables
        self.regulatorycompliance = None
        self.productportfolio = None
        self.acquisitions = None


    def parsing_file(self):
        r = requests.get(self.url, headers = self.headers)
        raw_file = r.text
        doc_start_pattern = re.compile(r'<DOCUMENT>')
        doc_end_pattern = re.compile(r'</DOCUMENT>')
        type_pattern = re.compile(r'<TYPE>[^\n]+')
        doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_file)]
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_file)]
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_file)]

        document = {}
        for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
            if doc_type == self.file:
                document[doc_type] = raw_file[doc_start:doc_end]

        # Store the complete document
        self.document = document 

        extractorApi = ExtractorApi(self.api_key)
        
        # Extract Item 1, 1A, 2, 7, and 8
        self.item1 = extractorApi.get_section(self.url, "1", "text")
        self.item1a = extractorApi.get_section(self.url, "1A", "text")
        self.item2 = extractorApi.get_section(self.url, "2", "text")
        self.item7 = extractorApi.get_section(self.url, "7", "text")
        self.item8 = extractorApi.get_section(self.url, "8", "text")

        self.regulatorycompliance = regulatory_compliance(self.item1a)
        self.productportfolio = product_portofolio(self.item1)
        self.acquisitions = acquisitions(self.item8)

if __name__ == "__main__":
    headers = {"User-Agent": "bxie43@wisc.edu"}
    FILE = '10-K'
    Year = '2023'
    api_key = '053cfbf1aa19a8f110d11a302baa4b045cb7ac2448d6c117ffa134e6ca68afdc'


    company = CIKScraper("ADM", headers)
    company.parsing_tickers()

    scraper = SECScraper(company.cik, Year, FILE, headers)
    url = scraper.scrape_sec_data()[0]

    parser = DocScraper(url, FILE, headers, api_key, Year)
    parser.parsing_file()

    print("Item 1A:", parser.item1a)
    print("Regulatory_compliance:", parser.regulatorycompliance)
    print("----------------------")
    # print("Item 1a:", parser.item1a)
    # print("----------------------")
    # print("Item 2:", parser.item2)
    # print("----------------------")
    # print("Item 7:", parser.item7)
    # print("----------------------")
    # print("Item 8:", parser.item8)    