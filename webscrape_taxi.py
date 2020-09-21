import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pandas as pd

# tast inn nettsted (dersom endret).
nettsted = 'https://www.taxikalkulator.no/'

# lager et chrome options objekt for å bestemme vindustærrelse og "headless" nettleser
options = Options()
#options.add_argument('--headless')
options.add_argument('--window-size=1920x1080')

# har lastet ned chrome driveren fra https://sites.google.com/a/chromium.org/chromedriver/downloads og lagt den i current working directory
chrome_driver = os.getcwd() + '\\chromedriver.exe'

# filsti til backup-filer
backupSti = os.getcwd() + '\\backup\\'

# aapner nettstedet
driver = webdriver.Chrome(options=options, executable_path=chrome_driver)
driver.get(nettsted)
time.sleep(3)

# Lager rammeverk til datasettet 
drosjeFil = pd.DataFrame()

# klassen som utfoerer selve skrapingen
class Taxi:
    def __init__(self, by, fra, til, dato, hour):
        self.fra = fra
        self.til = til
        self.by = by
        self.dato = dato
        self.hour = hour
        self.drosjeData = {}

    def innhenting(self):
        # skriver inn til- og fra-adresse
        driver.find_element_by_id('from_address_input').send_keys(Keys.PAGE_UP)
        driver.find_element_by_id('from_address_input').click()
        driver.find_element_by_id('from_address_input').clear()
        driver.find_element_by_id('from_address_input').send_keys(self.fra)
        time.sleep(1)
        driver.find_element_by_id('from_address_input').send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        driver.find_element_by_id('to_address_input').click()
        driver.find_element_by_id('to_address_input').clear()
        driver.find_element_by_id('to_address_input').send_keys(self.til)
        time.sleep(2)
        driver.find_element_by_id('to_address_input').send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        if self.by != 'Oslo':
            time.sleep(8)
        global drosjeFil
        for i in range(len(self.dato)):
            driver.find_element_by_id('datepicker').send_keys(Keys.PAGE_UP)
            driver.find_element_by_id('datepicker').click()
            driver.find_element_by_xpath(str('//*[@id="ui-datepicker-div"]/div/a[2]')).click()
            driver.find_element_by_xpath(str('//*[@id="ui-datepicker-div"]/table/tbody/tr[3]/td[' + str(self.dato[i]) + ']/a')).click()
            for j in range(len(self.hour)):
                # Tidspunkt
                driver.find_element_by_id('timepicker').click()
                # Velge time
                driver.find_element_by_xpath('//*[@id="timepicker_hour"]').click()
                driver.find_element_by_xpath('//*[@id="timepicker_hour"]').send_keys(Keys.ARROW_LEFT)
                driver.find_element_by_xpath('//*[@id="timepicker_hour"]').send_keys(Keys.DELETE)
                driver.find_element_by_xpath('//*[@id="timepicker_hour"]').send_keys(Keys.DELETE)
                driver.find_element_by_xpath('//*[@id="timepicker_hour"]').send_keys(self.hour[j])

                # Velge minutt
                driver.find_element_by_xpath('//*[@id="timepicker_min"]').click()
                driver.find_element_by_xpath('//*[@id="timepicker_min"]').send_keys(Keys.ARROW_LEFT)
                driver.find_element_by_xpath('//*[@id="timepicker_min"]').send_keys(Keys.DELETE)
                driver.find_element_by_xpath('//*[@id="timepicker_min"]').send_keys(Keys.DELETE)
                driver.find_element_by_xpath('//*[@id="timepicker_min"]').send_keys('00')
                time.sleep(2)
                driver.find_element_by_xpath('//*[@id="timepicker_min"]').send_keys(Keys.ENTER)

                # Kjøre spørringen og samle inn data
                #driver.find_element_by_id('calc_submit').click()
                #driver.find_element_by_id('calc_submit').click()
                if self.by == 'Oslo':
                    time.sleep(8)
                else:
                    time.sleep(5)
                html = driver.execute_script('return document.documentElement.outerHTML;')
                soupDrosje = BeautifulSoup(html, 'html.parser')

                # Henter navnene på drosjesentralene
                drosjeSentral = soupDrosje.find("div", {"id": "price_list"}).find_all("h4")
                for k in range(len(drosjeSentral)):
                    drosjeSentral[k] = drosjeSentral[k].get_text()
                    drosjeSentral[k] = drosjeSentral[k].strip('\n')
                self.drosjeData['drosjesentral'] = drosjeSentral

                # Skriver inn by
                drosjeBy = []
                for k in range(len(drosjeSentral)):
                    drosjeBy.append(self.by)
                self.drosjeData['by'] = drosjeBy

                # Skriver inn fra destinasjon
                drosjeFra = []
                for k in range(len(drosjeSentral)):
                    drosjeFra.append(self.fra)
                self.drosjeData['fra'] = drosjeFra

                # Skriver inn til destinasjon
                drosjeTil = []
                for k in range(len(drosjeSentral)):
                    drosjeTil.append(self.til)
                self.drosjeData['til'] = drosjeTil

                # Skriver inn klokkeslett
                drosjeKlokke = []
                for k in range(len(drosjeSentral)):
                    drosjeKlokke.append(str(self.hour[j] + ':00'))
                self.drosjeData['klokkeslett'] = drosjeKlokke

                # skriver inn dag
                drosjeDag = []
                if self.dato[i] == 1:
                    dag = 'mandag'
                if self.dato[i] == 2:
                    dag = 'tirsdag'
                if self.dato[i] == 3:
                    dag = 'onsdag'
                if self.dato[i] == 4:
                    dag = 'torsdag'
                if self.dato[i] == 5:
                    dag = 'fredag'
                if self.dato[i] == 6:
                    dag = 'lørdag'
                if self.dato[i] == 7:
                    dag = 'søndag'
                for k in range(len(drosjeSentral)):
                    drosjeDag.append(dag)
                self.drosjeData['dag'] = drosjeDag

                # Henter dato for siste oppdatering av priser
                drosjeOppdatert = soupDrosje.find("div", {"id": "price_list"}).find_all("div",{"class": "row-update-date"})
                for k in range(len(drosjeOppdatert)):
                    drosjeOppdatert[k] = drosjeOppdatert[k].get_text()
                    drosjeOppdatert[k] = drosjeOppdatert[k].strip('\n\t')
                    drosjeOppdatert[k] = drosjeOppdatert[k].replace('Oppdatert: ', '')
                    drosjeOppdatert[k] = drosjeOppdatert[k].replace('-', '.')
                self.drosjeData['sistoppdatert'] = drosjeOppdatert

                # Henter starttakst
                drosjeStarttakst = soupDrosje.find("div", {"id": "price_list"}).find_all("div", {"class": "pd_start_price row_price_details_row_price"})
                for k in range(len(drosjeStarttakst)):
                    drosjeStarttakst[k] = drosjeStarttakst[k].get_text()
                    drosjeStarttakst[k] = drosjeStarttakst[k].strip('\n')
                    drosjeStarttakst[k] = drosjeStarttakst[k].replace(' kr', '')
                    drosjeStarttakst[k] = round(float(drosjeStarttakst[k]),2)
                self.drosjeData['starttakst'] = drosjeStarttakst

                # Henter KM-pris
                drosjeKmpris = soupDrosje.find("div", {"id": "price_list"}).find_all("div", {"class": "pd_km_rate_1"})
                for k in range(len(drosjeKmpris)):
                    drosjeKmpris[k] = drosjeKmpris[k].get_text()
                    drosjeKmpris[k] = drosjeKmpris[k].strip('\n')
                    drosjeKmpris[k] = drosjeKmpris[k].replace(' kr / km', '')
                    drosjeKmpris[k] = round(float(drosjeKmpris[k]),2)
                self.drosjeData['kmpris'] = drosjeKmpris

                # Henter timepris
                drosjeTimepris = soupDrosje.find("div", {"id": "price_list"}).find_all("div",{"class": "pd_hourly_rate"})
                for k in range(len(drosjeTimepris)):
                    drosjeTimepris[k] = drosjeTimepris[k].get_text()
                    drosjeTimepris[k] = drosjeTimepris[k].strip('\n')
                    drosjeTimepris[k] = drosjeTimepris[k].replace(' kr / h', '')
                    drosjeTimepris[k] = round(float(drosjeTimepris[k]),2)
                self.drosjeData['timepris'] = drosjeTimepris

                # Beregne jamførpris
                drosjeJamfor = []
                if len(drosjeStarttakst) == len(drosjeKmpris) == len(drosjeTimepris):
                    for l in range(len(drosjeStarttakst)):
                        drosjeJamfor.append(round(drosjeStarttakst[l] + (8 * drosjeKmpris[l]) + ((13 * drosjeTimepris[l]) / 60),2))
                self.drosjeData['jamforpris'] = drosjeJamfor
                drosjeFil = drosjeFil.append(pd.DataFrame.from_dict(self.drosjeData))
                

                # Printer status
                print('Fant ' + str(len(drosjeSentral)) + ' priser for ' + str(self.by) + ' ' + str(dag) + ' kl ' + str(self.hour[j] + ':00'))
            drosjeFil.to_excel(str(backupSti) + str('tom_' + self.by + '_' + dag + '_' + time.strftime("%Y%m%d") + '_KL' + time.strftime("%H%M%S")+ '.xlsx'), index=False)