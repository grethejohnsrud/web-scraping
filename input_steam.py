import webscrape_steam
start_time = webscrape_steam.time.time()

archivePath = 's:\\Organisasjon\\A200\\S240\\03_KPI\\01_Produksjon\\01_Delundersøkelser\\Elektroniske spill\\Output\\'
archivePathDailyFile = str(archivePath + 'steamdata_' + webscrape_steam.time.strftime("%Y%m%d") + '.xlsx')
archivePathMonthlyFile = str(archivePath + 'steamdata_' + webscrape_steam.time.strftime("%Y%m") + '.xlsx')
myDailyFile = webscrape_steam.Path(archivePathDailyFile)
myMonthlyFile = webscrape_steam.Path(archivePathMonthlyFile)

if myDailyFile.is_file(): # checks if web scraping already has been completed today
    print('the file containing data for electronic games has already been created today')
    webscrape_steam.time.sleep(5)
else:
    print('web scraping top 100 most sold games on Steam (electronic games store)')
    print('')
    # add to the list under to include more prices, 25 prices every page
    #multiplePage = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40]
    #27022020: page 1 now includes page 2, so to prevent duplicates, page 2 wil not be scraped. Top seller list now dynamic, possible press page down couple of times and get 100 first observations
    multiplePage = [3,4]
    firstPage = webscrape_steam.WebscrapeSteam('https://store.steampowered.com/search/?category1=998&filter=topsellers')
    firstPage.obtain()
    print('Page 1 scraped')
    
    for i in range(len(multiplePage)):
        loopPage = webscrape_steam.WebscrapeSteam('https://store.steampowered.com/search/?filter=topsellers&page=' + str(multiplePage[i]) + '&category1=998')
        loopPage.obtain()
        print('Page ' + str(multiplePage[i]) + ' scraped')
    

    # creates temporary files for product name, clean price, price and date (bør kunne legge alt i en fil, mao en temp fil)
    steamFile_temp1 = webscrape_steam.pd.DataFrame(webscrape_steam.productNameTotal, columns=['name'])
    steamFile_temp2 = webscrape_steam.pd.DataFrame(list(zip(webscrape_steam.productPriceCleanTotal, webscrape_steam.productPriceTotal, webscrape_steam.productPriceOrgCleanTotal, webscrape_steam.productPriceOrgTotal))\
    , columns=['price_clean', 'price', 'org_price_clean', 'org_price'])
    steamFile_temp3 = webscrape_steam.pd.DataFrame(webscrape_steam.productPriceDiscountTotal, columns=['discount'])
    steamFile_temp4 = webscrape_steam.pd.DataFrame(list(zip(webscrape_steam.productRelDateTotal, webscrape_steam.dateCollected, webscrape_steam.yearCollected, webscrape_steam.monthCollected, \
    webscrape_steam.dayCollected, webscrape_steam.appidTotal)) , columns=['release_date','date_collected', 'year_collected', 'month_collected', 'day_collected', 'app_id'])
    steamFile_temp5 = webscrape_steam.pd.DataFrame(list(zip(webscrape_steam.genre1Total, webscrape_steam.genre2Total, webscrape_steam.genre3Total, webscrape_steam.genre4Total, webscrape_steam.genre5Total,\
    webscrape_steam.genre6Total, webscrape_steam.genre7Total, webscrape_steam.plasseringTotal)) , columns=['genre1', 'genre2', 'genre3', 'genre4', 'genre5', 'genre6', 'genre7', 'plassering'])
    # merges the five datsets
    steamFile = webscrape_steam.pd.concat([steamFile_temp1, steamFile_temp2, steamFile_temp3, steamFile_temp4, steamFile_temp5], sort=False, axis=1)
    # exports the datasets as an excel and csv file
    steamFile.to_excel(str(archivePath) + str('steamdata_' + webscrape_steam.time.strftime("%Y%m%d") + '.xlsx'), index=False)
    steamFile.to_csv(str(archivePath) + str('steamdata_' + webscrape_steam.time.strftime("%Y%m%d") + '.csv'), index=False, sep=';')

    # collects data per month, create new files if first time a given month
    if myMonthlyFile.is_file():
       df = webscrape_steam.pd.read_excel(archivePathMonthlyFile, converters={'date_collected' : str, 'year_collected' : str, 'month_collected' : str, 'day_collected' : str})
       df = df.append(steamFile, sort=False)
       df.to_excel(str(archivePath) + str('steamdata_' + webscrape_steam.time.strftime("%Y%m") + '.xlsx'), index=False)
       df.to_csv(str(archivePath) + str('steamdata_' + webscrape_steam.time.strftime("%Y%m") + '.csv'), index=False, sep=';')
    else:
        steamFile.to_excel(str(archivePath) + str('steamdata_' + webscrape_steam.time.strftime("%Y%m") + '.xlsx'), index=False)
        steamFile.to_csv(str(archivePath) + str('steamdata_' + webscrape_steam.time.strftime("%Y%m") + '.csv'), index=False, sep=';')

    print('')
    print('the web scraping is done and took ' + str(int(webscrape_steam.time.time() - start_time)) + ' seconds to run')
    print('total prices collected: ' + str(len(webscrape_steam.productNameTotal)))
    print('')
    x = input('press any key to exit')
