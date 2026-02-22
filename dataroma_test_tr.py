import requests
from bs4 import BeautifulSoup
import re

url = "https://www.dataroma.com/m/holdings.php?m=LMM"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

print("Period parsing:")
# Find the text "Period:"
period_label = soup.find(string=re.compile("Period:"))
if period_label:
    parent = period_label.parent
    # The actual period like "Q4 2025" might be the next sibling or inside a span
    # Let's just print parent and ancestors
    print("Label parent:", parent.name, parent.text.strip())
    # Actually in the page text it was just lines
    # Let's search by class usually dataroma uses 'sym' for symbols. 
    period_span = soup.find("span", id="period") # wild guess
    print("span id=period:", period_span)

print("\nRow parsing:")
table = soup.find("table", id="grid")
if table:
    tbody = table.find("tbody")
    tr = tbody.find("tr")
    tds = tr.find_all("td")
    print(f"Number of TDs: {len(tds)}")
    print("Cells:")
    for i, td in enumerate(tds):
        print(f" {i}: {td.get_text(strip=True)} | html: {td}")
