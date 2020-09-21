import requests
import re
import time
from bs4 import BeautifulSoup
import pandas as pd
import os
from pathlib import Path
import ast
from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

print('Starter opp web scraper for power.no')

# Starter med å lage en liste hvor all informasjon skal samles. Det er denne lsiten som danner grunnlaget for outputfilen.
totalList = []
# Starter stoppeklokken for å måle hvor lang tid web scraperen tar.
start_time = time.time()
# Definerer filstien hvor output-filen skal plasseres.
path = r'C:\\Users\\gon'
outputPath = r'C:\\Users\\gon\\output\\'

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

        # lager et chrome options objekt for å bestemme vindustærrelse og "headless" nettleser
        options = Options()
        #options.add_argument('--headless')
        options.add_argument('--window-size=1920x1080')

        # har lastet ned chrome driveren fra https://sites.google.com/a/chromium.org/chromedriver/downloads og lagt den i current working directory
        chrome_driver = path + '\\chromedriver.exe'
        # aapner nettstedet
        driver = webdriver.Chrome(options=options, executable_path=chrome_driver)
        driver.get(self.url)
        time.sleep(2)

        # klikker videre slik at alle produkter kommer frem

        wait = WebDriverWait(driver, 1)
        while True:
            try:
                #driverCrawl.find_element_by_xpath('//*[@id="product-information-tabs"]/div[1]').click()
                element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="product-list-load-more"]/button')))
                element.click()
            except TimeoutException:
                break


        html = driver.execute_script('return document.documentElement.outerHTML;')

        # parser HTML-koden og lagrer til BeautifulSoup objekter
        soupWebsite = BeautifulSoup(html, 'html.parser')
        time.sleep(1)
        driver.quit()
        # Lager en liste som inneholder alle produkter på internettsiden
        #allItems = soupWebsite.find_all("div", {"class":"product-item-top"})
        allItems = soupWebsite.find_all("div", {"class":"col-xxs-12 col-xs-6 product-container col-md-4 ng-star-inserted"})
        

        # Looper gjennom listen av alle varene som ble funnet på siden og innhenter informasjon som varenavn, spesifikasjoner, vare- og prod nr., pris, URL til den enkelte varen. 
        # Går videre inn i den enkelte vares URL for å trekke ut all info om spesifikasjoner
        for i in range(len(allItems)):
            # Lager en Dictionary for å systematisere datainnhentingen og koble riktig verdi til riktig variabel
            itemDict = {}
            
            # Legger først til produkttype i Dictionary, som blir definert av bruker før skrapingen settes i gang. 
            itemDict.update({'productType':self.productType})
            
            # Legger til navn på varen
            itemDict.update({'itemName':allItems[i].find("span", {"class":"product-name"}).text})
            
            # Legger til varespesifikasjoner, som listes opp på fellessiden (mao. ikke spesifikasjonene som ligger inne på varens egne side, det samles inn senere i programmet)
            itemSpecs = allItems[i].find_all("li", {"class":"ng-star-inserted"})
            counter = 1
            for j in range(len(itemSpecs)):
                itemDict.update({str('itemSpec_' + str(counter)):itemSpecs[j].text})
                counter += 1
     
            # Legge til om varen er på lager eller utsolgt? Det kan i så fall hentes fra class="stockstatus"        
            
            # Legger til-nå pris, også få med før-pris? Dersom det er både før- og nå-pris ligger det inne i class="price-wrapper". 
            # Undergruppe "product-price-now" brukes nå, men det må lages en egen variabel for før-pris som hentes fra "product-price-before". 
            # Dersom fullpris, skal før-pris settes lik fullpris eller som missing?
            itemPrice = allItems[i].find("pwr-price").text
            itemPrice = re.sub("[^0-9]","",itemPrice)
            itemDict.update({'itemPrice':int(itemPrice)})
            
            # Legger til URL. Samme URL blir listet opp minst 3 ganger i HTML-koden, så henter bare ut første i listen av 3.
            lenke = [a['href'] for a in allItems[i].select('a[href]')]
            lenke = str("https://www.power.no" + lenke[0])
            itemDict.update({'lenke':lenke})
            
            # Går inn i URL-en og henter spesifikasjoner (crawling)
            driverCrawl = webdriver.Chrome(options=options, executable_path=chrome_driver)
            driverCrawl.get(lenke)
            time.sleep(1)
            driverCrawl.find_element_by_xpath('//*[@id="product-information-tabs"]/div[1]').click()
            time.sleep(1)
            htmlCrawl = driverCrawl.execute_script('return document.documentElement.outerHTML;')

            # parser HTML-koden og lagrer til BeautifulSoup objekter
            soupCrawl = BeautifulSoup(htmlCrawl, 'html.parser')
            driverCrawl.quit()
            
            # Henter all informasjon fra tabellen som lister spesifikasjonene til varen, lister opp slik at variabelnavn bli Key, og verdi blir Value i Dictionary {variabelnavn:verdi}
            specs = soupCrawl.find('div', {'class':'panel panel-default ng-star-inserted'})
            specs = specs.find_all('div', {'class':'row ng-star-inserted'})
            
            ##########################################################################################################################################################################
            # Ikke ta med de som har missing value, dette er overskrifter og trenger ikke være med. Se eventuelt om overskriftene og infoen har noe som kan skille dem fra hverandre #
            ##########################################################################################################################################################################
            for k in range(len(specs)):
                itemDict.update({specs[k].find('div', {'class':'col-sm-8 col-xs-8'}).text:specs[k].find('div', {'class':'col-sm-4 col-xs-4'}).text})
            
            
            
            # Legger all informasjon samlet om en vare over til hovedlisten
            totalList.append(itemDict)
            # Utlisting for å gi beskjed om at informasjonen knyttet til en vare er innsamlet
            print('Data samlet inn for: ' + str(self.productType) + ', ' + str(allItems[i].find("span", {"class":"product-name"}).text))
            

# Skaper de ulike klassene her, hvor input fra bruker er URL og produkttype
#microwave = Webscrape('https://www.komplett.no/category/753/hvitevarer/mikroboelgeovner','microwave')
# Kjører programmet inne i klassen som utfører selve skrapingen
#microwave.obtain()

# Skaper de ulike klassene her, hvor input fra bruker er URL og produkttype
blender = Webscrape('https://www.power.no/kjoekkenutstyr/kjoekkenapparater/blender/pl-1690/','blender')
# Kjører programmet inne i klassen som utfører selve skrapingen
blender.obtain()

# Skaper de ulike klassene her, hvor input fra bruker er URL og produkttype
stoevsuger = Webscrape('https://www.power.no/hjem-og-fritid/stoevsuger-og-rengjoering/stoevsuger/pl-1609/','stoevsuger')
# Kjører programmet inne i klassen som utfører selve skrapingen
stoevsuger.obtain()



# Etter at all informasjon er samlet inn, genereres det en Pandas Dataframe som strukturerer dataen som ligger i listen totalList
powerFile = pd.DataFrame(totalList)

# Genererer deretter output i form av en excel-fil, men kan også lage i .txt eller .csv
powerFile.to_excel(str(outputPath) + 'testfil_' + str(time.strftime("%Y%m%d")) + '_' + str(time.strftime("%H%M")) + '.xlsx', index=False)
# Printer ut oppsummering av skraperen
print('')
print('Web scrapingen er ferdig og brukte ' + str(int(time.time() - start_time)) + ' sekunder på å kjøre')
print('')
print('Antall observasjoner samlet inn: ' + str(len(totalList)))
print('')
x = input('press any key to exit')
