import urllib.request

class SECScraper:
    def __init__(self, CIK, Year, FILE, headers):
        self.CIK = CIK
        self.Year = Year
        self.FILE = FILE
        self.headers = headers

    def scrape_sec_data(self):
        urls = []
        try:            
            quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
            string_match1 = 'edgar/data/'
            for quarter in quarters:
                url = f'https://www.sec.gov/Archives/edgar/full-index/{self.Year}/{quarter}/master.idx' # Search for master index for each quarter
                req = urllib.request.Request(url, headers=self.headers)
                response = urllib.request.urlopen(req)
                element2, element3, element4 = None, None, None
                for line in response:
                    content = line.decode('utf-8')
                    if self.CIK in content and self.FILE in content: # Check if CIK and FILE are within the content
                        if string_match1 in content:
                            element2 = content.split('|') 
                            for element3 in element2:
                                if string_match1 in element3: # Extract the headers for the corresponding document
                                    element4 = element3.strip() # Remove the whitespace
                                    if element4 and f'edgar/data/{self.CIK}/' in element4: # Check if the url has the CIK right after the string_match1
                                         url3 = 'https://www.sec.gov/Archives/' + element4 # Return the complete url
                                         
                                         urls.append(url3)
            return urls

            
        except urllib.error.URLError as e:
            return f"Failed to retrieve content. Error: {e}" 
        