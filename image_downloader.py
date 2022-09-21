import requests
from bs4 import BeautifulSoup


query = 'Quevedo, Bizarrap'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
}
params = {
    "q": query, # search query
    "tbm": "isch",                # image results
    "hl": "en",                   # language of the search
    "gl": "es",                   # country where search comes from
    "ijn": "0"                    # page number
}
html = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)
soup = BeautifulSoup(html.text, "lxml")

