import requests
import time
from bs4 import BeautifulSoup

url = 'https://www.eerstekamer.nl/stemmingen_per_vergaderdag'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

c = []

while url:
    time.sleep(2)  
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    for link in soup.find_all('h2'):
        try:
            for l in link.find_all('a', id=lambda value: value and value.startswith("p")):
                datum = l.next_element.replace('\n', '').replace('\r', '').split(' (')[0].rstrip()
                for i in l.next_element.next_element.next_element.next_element.find_all("li", {"class": "opsomitem met_image image_breed"}):
                    try:
                        for f in i.find_all("div", {"class": "opsomitem grid-x nowr"}):
                            if 'voor' in f.find('img')['src']:
                                uitslag = 'aangenomen'
                            elif 'tegen' in f.find('img')['src']:
                                uitslag = 'verworpen'
                            else:
                                raise ValueError('Geen uitslag beschikbaar.')
                            titel = f.find('div', class_='opsomtekst').text.replace('\n', '').replace('\t', '').replace('\r', '').split(' (')[0].rstrip()
                            url = 'https://www.eerstekamer.nl' + f.a['href'] if f.a['href'] is not '#' else None
                            code = f.find('div', class_='opsomtekst').text.replace('\n', '').replace('\t', '').replace('\r', '').split('(', 1)[1].split(')')[0]
                            stemming = f.find_all('a')[-1].text.split(',')[0]
                            stemming_url = 'https://www.eerstekamer.nl' + f.find_all('a')[-1]['href']
                            if 'zitten en opstaan' in stemming:
                                zo_stemming = f.find_all("div", {"class": "openclose"})[0].text.strip().replace('voor: ', '').replace(' en', ',').split('tegen: ')
                                zo_stemming_voor = zo_stemming[0].replace(" ", "").split(",")
                                zo_stemming_tegen = zo_stemming[1].replace(" ", "").split(",")
                                sp = {"voor": zo_stemming_voor, "tegen": zo_stemming_tegen} 
                            if 'Hoofdelijke' in stemming:
                                ho_stemming = f.find_all("div", {"class": "openclose"})[0].text.strip().replace('voor: ', '').replace(' en', ',').split('tegen: ')
                                ho_stemming_v = ho_stemming[0].split(", ")
                                ho_stemming_voor=[]
                                for s in ho_stemming_v:
                                    x = []
                                    x.append(s.split('(')[0].rstrip())
                                    x.append(s.split('(', 1)[1].split(')')[0])
                                    ho_stemming_voor.append(x)
                                ho_stemming_t = ho_stemming[1].split(",")
                                ho_stemming_tegen=[]
                                for s in ho_stemming_t:
                                    x = []
                                    x.append(s.split('(')[0].rstrip().lstrip())
                                    x.append(s.split('(', 1)[1].split(')')[0])
                                    ho_stemming_tegen.append(x)
                                sp = {"voor": ho_stemming_voor, "tegen": ho_stemming_tegen}
                            if 'Hamerstuk' in stemming:
                                aantekening = f.find_all("div", {"class": "openclose"})[0].text.strip().replace('aantekening gevraagd: ', '').replace(' en', ',').split(",")
                                sp = {"aantekening": aantekening}
                            s = {code: {"naam": titel, "datum": datum, "wet_url": url, "code": code, stemming.lower(): sp, "stemming_url": stemming_url}}
                            c.append(s)
                    except:
                        continue
        except:
            continue

    url = "https://www.eerstekamer.nl" + soup.find('a', class_='grid-x nowr')['href'] if "eerdere stemmingen" in soup.find('a', class_='grid-x nowr').text else None

data = {}
data['stemmingen'] = c

with open('stemmingen_eerste_kamer.json', 'w') as outfile:
    json.dump(data, outfile)
