import json

from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
wd = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
driver =webdriver.Chrome('chromedriver',chrome_options=chrome_options)

res = {}
with open("polish_offensive_dict.json") as f:
  offensive_dict = json.load(f)

for word in offensive_dict:
  URL = 'https://pl.wiktionary.org/wiki/'+word
  wd.get(URL)
  get_element  = wd.find_elements_by_css_selector("dl[class='text-pl']")
  odmiana_seen = False
  wymowa_seen = False
  res[word] = {"odmiana": [], "znaczenie": [], "przyk": []}
  for i in range(len(get_element)):
    if "odmiana:" in get_element[i].text:
      odmiana_seen = True
      print("odmiana", i)
      res[word]["odmiana"].append(get_element[i].text)
      print(get_element[i].text)
    if wymowa_seen and not odmiana_seen:
      print("znaczenie?", i)
      print(get_element[i].text)
      res[word]["znaczenie"].append(get_element[i].text)
    if "wymowa:" in get_element[i].text:
      wymowa_seen = True
    if "przykłady:" in get_element[i].text:
      print("przyk", i)
      print(get_element[i].text)
      res[word]["przyk"].append(get_element[i].text)

with open('wiki_words2.json', 'w') as f:
    json.dump(res, f)