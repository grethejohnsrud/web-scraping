import webscrape
start_tid = webscrape.time.time()

# Her kan du endre hvilke dager (1=mandag, 2=tirsdag ...) og tidspunkt som skal skrapes
date = [1,6]
hour = ['00', '12', '19']

# Her kan du skrive til- og fra-destinasjoner for de ulike byene
osloDrosje = webscrape.Taxi('Oslo', 'Jernbanetorget 1, 0154 Oslo, Norge', 'Oslo Lufthavn, Ullensaker, Norge', date, hour)
bergenDrosje = webscrape.Taxi('Bergen', 'Bergen stasjon, 5015 Bergen, Norge', 'Bergen Lufthavn (BGO), Flyplassvegen 519, 5258 Bergen, Norge', date, hour)
stavangerDrosje = webscrape.Taxi('Stavanger', 'Stavanger Stasjon, Jernbaneveien 3, 4005 Stavanger, Norge', 'Stavanger lufthavn, Sola, Norge', date, hour)
trondheimDrosje = webscrape.Taxi('Trondheim', 'Trondheim S, Trondheim, Norge', 'Trondheim lufthavn, Stjørdal, Norge', date, hour)
tromsoDrosje = webscrape.Taxi('Tromsø', 'Hans Nilsens veg 41, 9020 Tromsdalen, Norge', 'Tromsø Lufthavn (TOS), Flyplassvegen 31, 9016 Tromsø, Norge', date, hour)
drammenDrosje = webscrape.Taxi('Drammen', 'Dr. Hansteins gate 4, 3044 Drammen, Norge', 'Dronninggata 18, 3019 Drammen, Norge', date, hour)
kristiansandDrosje = webscrape.Taxi('Kristiansand', 'Vestre Strandgate 41, 4612 Kristiansand, Norge', 'Kjevik lufthavn, 4657 Kjevik, Norge', date, hour)


# Selve skrapingen for de ulike byene, EXCELFILENE ER MIDLERTIDIG LAGRING
osloDrosje.innhenting()
webscrape.drosjeFil.to_excel(str(webscrape.backupSti) + str('drosjedataOslo_' + webscrape.time.strftime("%Y%m%d") + '_KL' + webscrape.time.strftime("%H%M%S")+ '.xlsx'), index=False)
bergenDrosje.innhenting()
webscrape.drosjeFil.to_excel(str(webscrape.backupSti) + str('drosjedataBergen_' + webscrape.time.strftime("%Y%m%d") + '_KL' + webscrape.time.strftime("%H%M%S")+ '.xlsx'), index=False)
#stavangerDrosje.innhenting()
#webscrape.drosjeFil.to_excel(str(webscrape.backupSti) + str('drosjedataStavanger_' + webscrape.time.strftime("%Y%m%d") + '_KL' + webscrape.time.strftime("%H%M%S")+ '.xlsx'), index=False)
#trondheimDrosje.innhenting()
#webscrape.drosjeFil.to_excel(str(webscrape.backupSti) + str('drosjedataTrondheim_' + webscrape.time.strftime("%Y%m%d") + '_KL' + webscrape.time.strftime("%H%M%S")+ '.xlsx'), index=False)
#tromsoDrosje.innhenting()
#webscrape.drosjeFil.to_excel(str(webscrape.backupSti) + str('drosjedataTromso_' + webscrape.time.strftime("%Y%m%d") + '_KL' + webscrape.time.strftime("%H%M%S")+ '.xlsx'), index=False)
#drammenDrosje.innhenting()
#webscrape.drosjeFil.to_excel(str(webscrape.backupSti) + str('drosjedataDrammen_' + webscrape.time.strftime("%Y%m%d") + '_KL' + webscrape.time.strftime("%H%M%S")+ '.xlsx'), index=False)
#kristiansandDrosje.innhenting()
#webscrape.drosjeFil.to_excel(str(webscrape.backupSti) + str('drosjedataKristiansand_' + webscrape.time.strftime("%Y%m%d") + '_KL' + webscrape.time.strftime("%H%M%S")+ '.xlsx'), index=False)

# Avslutter og lagrer datasettet som excel-fil
webscrape.driver.close()
webscrape.drosjeFil.to_excel(str('drosjedata_' + webscrape.time.strftime("%Y%m%d") + '_KL' + webscrape.time.strftime("%H%M%S")+ '.xlsx'), index=False)
print('')
print(str('drosjedata_' + str(webscrape.time.strftime("%Y%m%d")) + '_KL' + str(webscrape.time.strftime("%H%M%S")+ '.xlsx')) + ' ble lagret paa stien ' + str(webscrape.os.getcwd()))
print('')
print('skrapingen er ferdig og tok ' + str(int(webscrape.time.time() - start_tid)) + ' sekunder aa fullfore')