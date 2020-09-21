import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import os
from pathlib import Path
import ast
from random import randint

steamFile = pd.DataFrame()
productNameTotal = []
productRelDateTotal = []
productPriceTotal = [] # the actual price the customer has to pay
productPriceCleanTotal = []
productPriceOrgTotal = []
productPriceOrgCleanTotal = []
productPriceDiscountTotal = []
dateCollected = []
yearCollected = []
monthCollected = []
dayCollected = []
genre1Total = []
genre2Total = []
genre3Total = []
genre4Total = []
genre5Total = []
genre6Total = []
genre7Total = []
appidTotal = []
plasseringTotal = []
counter = 1


class WebscrapeSteam:
    def __init__(self, url):
        self.url = url
    
    def obtain(self):
        global counter
        # get html code from url
        rSteam = requests.get(self.url)
        #time.sleep(randint(1,5))
        time.sleep(1)
        cSteam = rSteam.content

        # parse HTML and save to BeautifulSoup objects
        soupSteam = BeautifulSoup(cSteam, 'html.parser')
        time.sleep(1)

        # find product names, date released and add date collected
        
        productName = soupSteam.find_all("span", {"class":"title"})
        productRelDate = soupSteam.find_all("div", {"class":"col search_released responsive_secondrow"})
        print('Prices found on this page: ' + str(len(productName)))
        for i in range(len(productName)):
            productName[i] = productName[i].text
            productNameTotal.append(productName[i])
            productRelDate[i] = productRelDate[i].text
            productRelDateTotal.append(productRelDate[i])
            dateCollected.append(str(time.strftime("%Y%m%d")))
            yearCollected.append(str(time.strftime("%Y")))
            monthCollected.append(str(time.strftime("%m")))
            dayCollected.append(str(time.strftime("%d")))
            plasseringTotal.append(counter)
            counter += 1

        # find actual product prices and clear noise
        productPrice = soupSteam.find_all("div", {"class":"col search_price_discount_combined responsive_secondrow"})
        for i in range(len(productPrice)):
            productPrice[i] = productPrice[i].text
            productPrice[i] = productPrice[i].replace('/r', '')
            productPrice[i] = productPrice[i].replace('/n', '')
            productPrice[i] = productPrice[i].replace('\n\n\n', '')
            productPrice[i] = productPrice[i].strip()
            if '%' in productPrice[i]: # special cleaning for products which are on sale, found by searching for %, indicating percentage of price drop
                productPrice[i] = productPrice[i][productPrice[i].find(' kr'):]
                productPrice[i] = productPrice[i].replace(' kr', '', 1)
            productPriceTotal.append(productPrice[i])
            productPrice[i] = productPrice[i].replace('Free to Play', '0.00')
            productPrice[i] = productPrice[i].replace('Free To Play', '0.00')
            productPrice[i] = productPrice[i].replace('Play for Free!', '0.00')
            productPrice[i] = productPrice[i].replace('Free', '0.00')
            productPrice[i] = productPrice[i].replace('Play the Demo', '0.00')
            if productPrice[i] == '':
                productPrice[i] = '0.00'
            productPrice[i] = productPrice[i].replace(' kr', '')
            #productPrice[i] = productPrice[i].replace('.', '')
            productPrice[i] = productPrice[i].replace(',', '.')
            productPrice[i] = productPrice[i].strip()
            productPrice[i] = float(productPrice[i])
            productPriceCleanTotal.append(productPrice[i])

        # find original product prices and clear noise
        productPriceOrg = soupSteam.find_all("div", {"class":"col search_price_discount_combined responsive_secondrow"})
        for i in range(len(productPriceOrg)):
            productPriceOrg[i] = productPriceOrg[i].text
            productPriceOrg[i] = productPriceOrg[i].replace('/r', '')
            productPriceOrg[i] = productPriceOrg[i].replace('/n', '')
            productPriceOrg[i] = productPriceOrg[i].replace('\n\n\n', '')
            productPriceOrg[i] = productPriceOrg[i].strip()
            if '%' in productPriceOrg[i]: # special cleaning for products which are on sale, found by searching for %, indicating percentage of price drop
                productPriceOrg[i] = productPriceOrg[i][:productPriceOrg[i].find(' kr')]
                productPriceOrg[i] = productPriceOrg[i].split("%",1)[1]
                productPriceOrg[i] = productPriceOrg[i].replace(' kr', '', 1)
            productPriceOrgTotal.append(productPriceOrg[i])
            productPriceOrg[i] = productPriceOrg[i].replace('Free to Play', '0.00')
            productPriceOrg[i] = productPriceOrg[i].replace('Free To Play', '0.00')
            productPriceOrg[i] = productPriceOrg[i].replace('Play for Free!', '0.00')
            productPriceOrg[i] = productPriceOrg[i].replace('Free', '0.00')
            productPriceOrg[i] = productPriceOrg[i].replace('Play the Demo', '0.00')
            if productPriceOrg[i] == '':
                productPriceOrg[i] = '0.00'
            productPriceOrg[i] = productPriceOrg[i].replace(' kr', '')
            #productPriceOrg[i] = productPriceOrg[i].replace('.', '')
            productPriceOrg[i] = productPriceOrg[i].replace(',', '.')
            productPriceOrg[i] = productPriceOrg[i].strip()
            productPriceOrg[i] = float(productPriceOrg[i])
            productPriceOrgCleanTotal.append(productPriceOrg[i])

        # estimate discount
        for i in range(len(productPrice)):
            if productPrice[i] == 0.0 or productPriceOrg[i] == 0.0:
                productPriceDiscountTotal.append(".")
            else:
                productPriceDiscountTotal.append(round(productPrice[i]/productPriceOrg[i],2))

        # get genre/tag
        genre = soupSteam.find("div", {"id":"search_resultsRows"}).find_all("a")
        for i in range(len(genre)):
            genre1 = '.'
            genre2 = '.'
            genre3 = '.'
            genre4 = '.'
            genre5 = '.'
            genre6 = '.'
            genre7 = '.'
            genre[i] = genre[i].get("data-ds-tagids")
            if genre[i] != None:
                genre[i] = genre[i].replace("'","")
                genre[i] = ast.literal_eval(genre[i])
                if len(genre[i]) == 1:
                    genre1 = genre[i][0]
                    genre2 = '.'
                    genre3 = '.'
                    genre4 = '.'
                    genre5 = '.'
                    genre6 = '.'
                    genre7 = '.'
                if len(genre[i]) == 2:
                    genre1 = genre[i][0]
                    genre2 = genre[i][1]
                    genre3 = '.'
                    genre4 = '.'
                    genre5 = '.'
                    genre6 = '.'
                    genre7 = '.'
                if len(genre[i]) == 3:
                    genre1 = genre[i][0]
                    genre2 = genre[i][1]
                    genre3 = genre[i][2]
                    genre4 = '.'
                    genre5 = '.'
                    genre6 = '.'
                    genre7 = '.'
                if len(genre[i]) == 4:
                    genre1 = genre[i][0]
                    genre2 = genre[i][1]
                    genre3 = genre[i][2]
                    genre4 = genre[i][3]
                    genre5 = '.'
                    genre6 = '.'
                    genre7 = '.'
                if len(genre[i]) == 5:
                    genre1 = genre[i][0]
                    genre2 = genre[i][1]
                    genre3 = genre[i][2]
                    genre4 = genre[i][3]
                    genre5 = genre[i][4]
                    genre6 = '.'
                    genre7 = '.'
                if len(genre[i]) == 6:
                    genre1 = genre[i][0]
                    genre2 = genre[i][1]
                    genre3 = genre[i][2]
                    genre4 = genre[i][3]
                    genre5 = genre[i][4]
                    genre6 = genre[i][5]
                    genre7 = '.'
                if len(genre[i]) == 7:
                    genre1 = genre[i][0]
                    genre2 = genre[i][1]
                    genre3 = genre[i][2]
                    genre4 = genre[i][3]
                    genre5 = genre[i][4]
                    genre6 = genre[i][5]
                    genre7 = genre[i][6]
            genre1Total.append(genre1)
            genre2Total.append(genre2)
            genre3Total.append(genre3)
            genre4Total.append(genre4)
            genre5Total.append(genre5)
            genre6Total.append(genre6)
            genre7Total.append(genre7)
        
        
        #produkt-ID
        appIdItemKey = soupSteam.find("div", {"id":"search_resultsRows"}).find_all("a")
        for i in range(len(appIdItemKey)):
            appIdItemKey[i] = appIdItemKey[i].get("data-ds-itemkey")
            appIdItemKey[i] = appIdItemKey[i].replace("'","")
            #appIdItemKey[i] = ast.literal_eval(appIdItemKey[i])
            appidTotal.append(appIdItemKey[i])