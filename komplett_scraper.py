import requests
import re
import time
from bs4 import BeautifulSoup
import pandas as pd
import os
from pathlib import Path
import ast
from random import randint

print('Starter opp web scraper for komplett.no')

# Starter med å lage en liste hvor all informasjon skal samles. Det er denne lsiten som danner grunnlaget for outputfilen.
totalList = []
# Starter stoppeklokken for å måle hvor lang tid web scraperen tar.
start_time = time.time()
# Definerer filstien hvor output-filen skal plasseres.
outputPath = r'C:\Users\gon\\output\\'

# Selve klassen hvor skrapingen gjennomføres.
class Webscrape:
    def __init__(self, url, productType):
        # url og produkttype må defineres for hver varegruppe, se hvordan like etter klassen.
        self.url = url
        # Legger til produkttype for å enklere kategorisere i ettertid
        self.productType = productType

    def obtain(self):
        # Gjør den totale listen global, slik at man kan endre på listen selv inne i en klasse
        global totalList
        # Henter HTML-koden fra URL'en
        requestWebsite = requests.get(self.url)
        time.sleep(1)
        contentWebsite = requestWebsite.content

        # parser HTML-koden og lagrer til BeautifulSoup objekter
        soupWebsite = BeautifulSoup(contentWebsite, 'html.parser')
        time.sleep(1)

        # Lager en liste som inneholder alle produkter på internettsiden
        allItems = soupWebsite.find_all("div", {"class":"product-list-item"})

        # Looper gjennom listen av alle varene som ble funnet på siden og innhenter informasjon som varenavn, spesifikasjoner, vare- og prod nr., pris, URL til den enkelte varen. 
        # Går videre inn i den enkelte vares URL for å trekke ut all info om spesifikasjoner
        for i in range(len(allItems)):
            # Lager en Dictionary for å systematisere datainnhentingen og koble riktig verdi til riktig variabel
            itemDict = {}
            
            # Legger først til produkttype i Dictionary, som blir definert av bruker før skrapingen settes i gang. 
            itemDict.update({'productType':self.productType})
            
            # Legger til navn på varen
            itemDict.update({'itemName':allItems[i].find("h2").text})
            
            # Legger til varespesifikasjoner, som listes opp på fellessiden (mao. ikke spesifikasjonene som ligger inne på varens egne side, det samles inn senere i programmet)
            itemDict.update({'itemSpecs':allItems[i].find("p").text})
            
            # Legger til vare- og prod. nr. Dette ligger i samme class i HTML-koden, men er separert med en /, derfor må denne informasjonen deles opp før den legges til Dictionary
            itemData = allItems[i].find("div", {"class":"product-data"}).text
            itemDataSplit = itemData.split("/",1)
            for j in range(len(itemDataSplit)):
                itemDataSplit[j] = itemDataSplit[j].strip()
                itemDict.update({itemDataSplit[j].split(":",2)[0].lower():itemDataSplit[j].split(":",2)[1].strip()})

            # Legge til om varen er på lager eller utsolgt? Det kan i så fall hentes fra class="stockstatus"        
            
            # Legger til-nå pris, også få med før-pris? Dersom det er både før- og nå-pris ligger det inne i class="price-wrapper". 
            # Undergruppe "product-price-now" brukes nå, men det må lages en egen variabel for før-pris som hentes fra "product-price-before". 
            # Dersom fullpris, skal før-pris settes lik fullpris eller som missing?
            itemPrice = allItems[i].find("span", {"class":"product-price-now"}).text
            itemPrice = re.sub("[^0-9]","",itemPrice)
            itemDict.update({'itemPrice':itemPrice})
            
            # Legger til URL. Samme URL blir listet opp minst 3 ganger i HTML-koden, så henter bare ut første i listen av 3.
            lenke = [a['href'] for a in allItems[i].select('a[href]')]
            lenke = str("https://www.komplett.no" + lenke[1])
            itemDict.update({'lenke':lenke})
            
            # Går inn i URL-en og henter spesifikasjoner (crawling)
            crawlWebsite = requests.get(lenke)
            time.sleep(1)
            contentCrawl = crawlWebsite.content
            
            # parser HTML-koden og lagrer til BeautifulSoup objekter
            soupCrawl = BeautifulSoup(contentCrawl, 'html.parser')
            
            # Henter all informasjon fra tabellen som lister spesifikasjonene til varen, lister opp slik at variabelnavn bli Key, og verdi blir Value i Dictionary {variabelnavn:verdi}
            specs = soupCrawl.find_all('tr')
            for k in range(len(specs)):
                itemDict.update({specs[k].find('th', {'scope':'row'}).text:specs[k].find('td').text})

            # Legger all informasjon samlet om en vare over til hovedlisten
            totalList.append(itemDict)
            time.sleep(randint(1,2))
            # Utlisting for å gi beskjed om at informasjonen knyttet til en vare er innsamlet
            print('Data samlet inn for: ' + str(self.productType) + ', ' + str(allItems[i].find("h2").text))

# Skaper de ulike klassene her, hvor input fra bruker er URL og produkttype
microwave = Webscrape('https://www.komplett.no/category/753/hvitevarer/mikroboelgeovner','microwave')
# Kjører programmet inne i klassen som utfører selve skrapingen
microwave.obtain()

# Skaper de ulike klassene her, hvor input fra bruker er URL og produkttype
bluetoothhoyttaler = Webscrape('https://www.komplett.no/category/12513/tv-lyd-bilde/baerbar-og-traadloes-lyd/baerbar-bluetooth-hoeyttaler?nlevel=10719%C2%A710263%C2%A712513&hits=600','bluetoothSpeaker')
# Kjører programmet inne i klassen som utfører selve skrapingen
bluetoothhoyttaler.obtain()

# Skaper de ulike klassene her, hvor input fra bruker er URL og produkttype
pcskjerm = Webscrape('https://www.komplett.no/category/11158/datautstyr/skjermer/skjermer?nlevel=10000%C2%A710392%C2%A711158&hits=600','pcskjerm')
# Kjører programmet inne i klassen som utfører selve skrapingen
pcskjerm.obtain()

# Etter at all informasjon er samlet inn, genereres det en Pandas Dataframe som strukturerer dataen som ligger i listen totalList
komplettFile = pd.DataFrame(totalList)

# Genererer deretter output i form av en excel-fil, men kan også lage i .txt eller .csv
komplettFile.to_excel(str(outputPath) + 'testfil_' + str(time.strftime("%Y%m%d")) + '_' + str(time.strftime("%H%M")) + '.xlsx', index=False)
# Printer ut oppsummering av skraperen
print('')
print('Web scrapingen er ferdig og brukte ' + str(int(time.time() - start_time)) + ' sekunder på å kjøre')
print('')
print('Antall observasjoner samlet inn: ' + str(len(totalList)))
print('')
x = input('press any key to exit')
