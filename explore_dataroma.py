import requests
from bs4 import BeautifulSoup
import time

url = "https://www.dataroma.com/m/holdings.php?m=LMM&q=20243"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("Page Title:", soup.title.string)
    
    # Let's find specific texts mentioning Quarter
    h2s = soup.find_all('h2')
    print("H2 tags:", [h2.text for h2 in h2s])
    
    # Are there any links with 'q='?
    q_links = soup.find_all('a', href=lambda href: href and 'q=' in href)
    if q_links:
        print("Found links with q=:")
        for link in q_links[:5]:
            print(f" - {link.text}: {link['href']}")
            
except Exception as e:
    print(f"Error: {e}")
