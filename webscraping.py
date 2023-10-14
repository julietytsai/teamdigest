import urllib.request

class SECScraper:
    def __init__(self, CIK, Year, FILE):
        self.CIK = CIK
        self.Year = Year
        self.FILE = FILE

    def scrape_sec_data(self):
        quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
        for quarter in quarters:
            url = f'https://www.sec.gov/Archives/edgar/full-index/{self.Year}/{quarter}/master.idx'
            headers = {'User-Agent': 'bxie43@wisc.edu'}
            req = urllib.request.Request(url, headers=headers)

            try:
                response = urllib.request.urlopen(req)
                element2, element3, element4 = None, None, None
                string_match1 = 'edgar/data/'

                for line in response:
                    content = line.decode('utf-8')
                    if self.CIK in content and self.FILE in content:
                        if string_match1 in content:
                            element2 = content.split('|')
                            for element3 in element2:
                                if string_match1 in element3:
                                    element4 = element3.strip()
                if element4:
                    url3 = 'https://www.sec.gov/Archives/' + element4
                    return url3
                
            except urllib.error.URLError as e:
                return f"Failed to retrieve content. Error: {e}" 
        