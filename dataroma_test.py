import requests
from bs4 import BeautifulSoup

def test_dataroma_date():
    url = "https://www.dataroma.com/m/holdings.php?m=LMM"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    body = soup.find('body')
    if body:
        text = body.get_text(separator='\n', strip=True)
        lines = text.split('\n')
        # Print first 30 lines which usually contain the header
        for i, line in enumerate(lines[:30]):
            print(f"{i}: {line}")

test_dataroma_date()
