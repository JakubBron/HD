from faker import Faker
import random
import datetime
import os
import string
import csv

# initialize faker

faker = Faker('pl_PL')
# database and implementation specific constants
gabaryty_maxTextLen = 20
zlecenia_maxTextLen = 250
our_seed = 2137

# data specific params / dictionaries
chance_pno = 0.7
chance_companyPerson = 0.5
chance_truckMalfunction = 0.6
timeStartDate = datetime.datetime(2020, 1, 1)
timeEndDate = datetime.datetime(2024, 10, 25)
timeEndDate_T2 = datetime.datetime(2025, 8, 10)
fuelTypesList = ['ON', 'PB95', 'LPG']
maxMalfunctionsPerTruck = 5
maxUpdated = 5
nullValue = ''

# setting RNGs
Faker.seed(our_seed)
random.seed(our_seed)

def generate_gabaryty(number, id_gabarytu = 0):
    dict_gabaryty = []
    for i in range(number):
        description = faker.text(gabaryty_maxTextLen)
        max_dim_x = random.randint(1, 9999)
        max_dim_y = random.randint(1, 9999)
        max_dim_z = random.randint(1, 9999)
        markup = round(random.uniform(5, 150), 2)
        
        dict_gabaryty.append( { 'ID_gabarytu': id_gabarytu, 
                                'Opis': description,
                                'Wymiar_X': max_dim_x,
                                'Wymiar_Y': max_dim_y,
                                'Wymiar_Z': max_dim_z,
                                'Marza': markup} )
        id_gabarytu += 1
    
    return dict_gabaryty, id_gabarytu

def generate_placowki(number_pno, number_dyst, id_placowki=0):
    dict_placowki = []
    for i in range(number_pno):
        address = faker.address().replace('\n', ' ')
        dict_placowki.append({'ID_placowki': id_placowki, 'Adres_placowki': address, 'Is_centrum_dystrybucyjne': 0})
        id_placowki += 1

    for i in range(number_dyst):
        address = faker.address().replace('\n', ' ')
        dict_placowki.append({'ID_placowki': id_placowki, 'Adres_placowki': address, 'Is_centrum_dystrybucyjne': 1})
        id_placowki += 1
    
    return dict_placowki, id_placowki

def generate_statusy():
    id_statusu = 4
    dict_statusy = [
        {'ID_statusu': 0, 'Opis_statusu': 'Przyjęte'},
        {'ID_statusu': 1, 'Opis_statusu': 'W realizacji'},
        {'ID_statusu': 2, 'Opis_statusu': 'Zakończone'},
        {'ID_statusu': 3, 'Opis_statusu': 'Anulowane'}
    ]
    return dict_statusy, id_statusu

def generate_zlecenia(number, dict_placowki, dict_gabaryty, dict_statusy, id_zlecenia=0):
    zlecenia = []
    for i in range(number):
        phone_number = f'+48{faker.msisdn()[4:]}'
        nazwa_zamawiajacego = ''
        if random.random() <= chance_companyPerson:
            nazwa_zamawiajacego = faker.name()[:zlecenia_maxTextLen]
        else:
            nazwa_zamawiajacego = faker.company()[:zlecenia_maxTextLen]

        all_pno_from_dict = set([x['ID_placowki'] for x in dict_placowki])
        adres_nadania = nullValue
        punkt_nadania = nullValue
        if random.random() <= chance_pno:
            punkt_nadania = all_pno_from_dict.pop()
        else:
            adres_nadania = faker.address().replace('\n', ' ')

        adres_odbioru = nullValue
        punkt_odbioru = nullValue
        if random.random() <= chance_pno:
            punkt_odbioru = all_pno_from_dict.pop()
        else:
            adres_odbioru = faker.address().replace('\n', ' ')
            
        gabaryt = random.randint(0, len(dict_gabaryty) - 1)
        marza_gabarytu = dict_gabaryty[gabaryt]["Marza"]
        cena = round(random.randint(10,9999) * (1+marza_gabarytu/100), 2)
        nr_faktury = f'FV-{random.randint(1000000, 9999999)}'
        status = random.randint(0, len(dict_statusy) - 1)
        data_przyjecia = faker.date_between(start_date=timeStartDate, end_date=timeEndDate)
        data_zakonczenia = faker.date_between(start_date=data_przyjecia, end_date=timeEndDate)
        
        data_przyjecia = str(data_przyjecia)
        data_zakonczenia = str(data_zakonczenia)
        
        zlecenia.append({
            'ID_zlecenia': id_zlecenia,
            'Nazwa_zamawiajacego': nazwa_zamawiajacego,
            'Tel_zamawiajacego': phone_number,
            'Adres_nadania': adres_nadania,
            'Adres_odbioru': adres_odbioru,
            'Punkt_nadania': punkt_nadania,
            'Punkt_odbioru': punkt_odbioru,
            'Gabaryt': gabaryt,
            'Cena': cena,
            'Nr_faktury': nr_faktury,
            'Status': status,
            'Data_przyjecia': data_przyjecia,
            'Data_zakoczenia': data_zakonczenia
        })
        id_zlecenia += 1

    return zlecenia, id_zlecenia

def generate_transportyzlecenia(placowki, zlecenia, statusy, id_zlecenia=0, id_transportu=0):
    transportyzlecenia = []
    i = id_zlecenia
    for i in range(id_zlecenia, len(zlecenia)):
        # jeśli nie wykonaliśmy danego zlecenia (wcale lub jeszcze nie wykonaliśmy), nie ma ono trasy
        if statusy[zlecenia[i]['Status']]['Opis_statusu'] in ['Anulowane', 'Przyjęte']:
            continue

        # poczatek zlecenia - pierwszy transport
        data_poczatek = datetime.datetime.strptime(zlecenia[i]['Data_przyjecia'], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(zlecenia[i]['Data_zakoczenia'], '%Y-%m-%d')
        data_koniec = faker.date_between(start_date=data_poczatek, end_date=end_date)
        skad = nullValue
        placowki_dystr_id = set([x['ID_placowki'] for x in placowki if x['Is_centrum_dystrybucyjne']])
        dokad = random.choice(list(placowki_dystr_id))
        placowki_dystr_id.remove(dokad)
        transportyzlecenia.append({
            'ID_zlecenia': i,
            'ID_transportu': id_transportu,
            'Data_poczatek': str(data_poczatek)[:10],
            'Data_koniec': str(data_koniec)[:10],
            'Skad': skad,
            'Dokad': dokad
        })
        id_transportu += 1

        # losowa ilosc nastepnych transportow
        for j in range(random.randint(0, len(placowki_dystr_id)-1)):
            data_poczatek = data_koniec
            data_koniec = faker.date_between(start_date=data_poczatek, end_date=end_date)
            skad = dokad
            dokad = random.choice(list(placowki_dystr_id))
            placowki_dystr_id.remove(dokad)
            transportyzlecenia.append({
                'ID_zlecenia': i,
                'ID_transportu': id_transportu,
                'Data_poczatek': str(data_poczatek)[:10],
                'Data_koniec': str(data_koniec)[:10],
                'Skad': skad,
                'Dokad': dokad
            })
            id_transportu += 1

        # jeśli zlecenie trwa, nie generujemy ostatniego etapu
        if statusy[zlecenia[i]['Status']]['Opis_statusu'] != 'Zakończone':
            continue

        # ostatni etap
        data_poczatek = data_koniec
        data_koniec = end_date
        skad = dokad
        dokad = nullValue
        transportyzlecenia.append({
            'ID_zlecenia': i,
            'ID_transportu': id_transportu,
            'Data_poczatek': str(data_poczatek)[:10],
            'Data_koniec': str(data_koniec)[:10],
            'Skad': skad,
            'Dokad': dokad
        })
        id_transportu += 1


    return transportyzlecenia, id_transportu

def generate_DzC_and_DoA(transportyzlecenia, number_of_trucks, id_transportu=0):
    DzC = []
    DoA = []
    for i in range(id_transportu, len(transportyzlecenia)):
        id_ciezarowki = random.randint(0, number_of_trucks)

        # create DzC
        zuzycie_paliwa = random.randint(3, 1000)
        typ_paliwa = random.choice(fuelTypesList)
        # data from Data_koniec and random hours
        data_pomiaru = datetime.datetime.strptime(transportyzlecenia[i]['Data_koniec'], '%Y-%m-%d') + datetime.timedelta(hours=random.randint(1, 24), minutes=random.randint(1, 60), seconds=random.randint(1, 60))
        emisja_tlenkow_wegla = round(300.0 + random.random()*1500,2)
        emisja_tlenkow_azotu = round(20.0 + random.random()*60,2)
        emisja_tlenkow_siarki = round(0.05 + random.random()*10, 2)

        DzC.append({
            'ID transportu': i,
            'ID ciezarowki': id_ciezarowki,
            'Zuzycie paliwa': zuzycie_paliwa,
            'Typ paliwa': typ_paliwa,
            'Data pomiaru': str(data_pomiaru),
            'Emisja tlenkow wegla': emisja_tlenkow_wegla,
            'Emisja tlenkow azotu': emisja_tlenkow_azotu,
            'Emisja tlenkow siarki': emisja_tlenkow_siarki
        })

        # create DoA
        if random.random() < chance_truckMalfunction:
            continue
        malfunctions_per_truck = random.randint(0, maxMalfunctionsPerTruck)
        for _ in range(malfunctions_per_truck):
            # data from Data_koniec and random hours
            data_awarii = datetime.datetime.strptime(transportyzlecenia[i]['Data_koniec'], '%Y-%m-%d') + datetime.timedelta(hours=random.randint(1, 24), minutes=random.randint(1, 60), seconds=random.randint(1, 60))

            DoA.append({
                'ID transportu': i,
                'ID ciezarowki': id_ciezarowki,
                'Data awarii': str(data_awarii),
                'Kod awarii': ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(2, 5)))
            })

    return DzC, DoA

def export_to_csv(data, path, filename, write_header=False):
        keys = data[0].keys()
        with open(f'{path}/{filename}', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            if write_header:
                writer.writeheader()
            writer.writerows(data)

############################################################

if __name__ == "__main__":
    # id counters
    id_zlecenia = 0
    id_gabarytu = 0
    id_statusu = 0
    id_placowki = 0
    id_transportu = 0

    # set number of data to be generated
    numberOf_gabaryty_t1 = 10
    numberOf_pno_t1 = 10
    numberOf_dystryb_t1 = 10
    numberOf_zlecenia_t1 = 10

    numberOf_gabaryty_t2 = 10
    numberOf_pno_t2 = 5
    numberOf_dystryb_t2 = 1
    numberOf_zlecenia_t2 = 5
    numberOfTrucks = 10

    # generating in T1 time moment
    gabaryty, id_gabarytu = generate_gabaryty(numberOf_gabaryty_t1, id_gabarytu=0)
    placowki, id_placowki = generate_placowki(numberOf_pno_t1, numberOf_dystryb_t1, id_placowki=0)
    statusy, id_statusu = generate_statusy()
    zlecenia, id_zlecenia_t1 = generate_zlecenia(numberOf_zlecenia_t1, placowki, gabaryty, statusy,  id_zlecenia=0)
    transportyzlecenia, id_transportu_t1 = generate_transportyzlecenia(placowki, zlecenia, statusy, id_zlecenia=0, id_transportu=0)
    DzC, DoA = generate_DzC_and_DoA(transportyzlecenia, numberOfTrucks, id_transportu=0)
    
    # save to CSV files - t1
    if not os.path.exists('./t1'):
        os.mkdir('./t1')
    export_to_csv(gabaryty,'./t1','gabaryty.csv')
    export_to_csv(placowki,'./t1','placowki.csv')
    export_to_csv(statusy,'./t1','statusy.csv')
    export_to_csv(zlecenia,'./t1','zlecenia.csv')
    export_to_csv(transportyzlecenia,'./t1','transportyzlecenia.csv')
    export_to_csv(DzC,'./t1','DzC.csv', True)
    export_to_csv(DoA,'./t1','DoA.csv', True)


    # generating in t2 time moment
    placowki2, id_placowki = generate_placowki(numberOf_pno_t2, numberOf_dystryb_t2, id_placowki=id_placowki)
    for x in placowki2:
        placowki.append(x)
    
    gabaryty2, id_gabarytu = generate_gabaryty(numberOf_gabaryty_t2, id_gabarytu = id_gabarytu)
    for x in gabaryty2:
        gabaryty.append(x)


    zlecenia2, id_zlecenia_t2 = generate_zlecenia(numberOf_zlecenia_t2, placowki, gabaryty, statusy, id_zlecenia=id_zlecenia_t1)
    for x in zlecenia2:
        zlecenia.append(x)

    transportyzlecenia2, id_transportu_t2 = generate_transportyzlecenia(placowki, zlecenia, statusy, id_zlecenia=id_zlecenia_t1, id_transportu=id_transportu_t1)
    for x in transportyzlecenia2:
        transportyzlecenia.append(x)
    
    DzC2, DoA2 = generate_DzC_and_DoA(transportyzlecenia, numberOfTrucks, id_transportu=id_transportu_t1)
    for x in DzC2:
        DzC.append(x)

    for x in DoA2:
        DoA.append(x)

    # minor changes: change 'ulica' to 'aleja' and 'ul.' to 'al.'
    for x in zlecenia:
        x['Adres_nadania'] = x['Adres_nadania'].replace('ulica', 'aleja')
        x['Adres_nadania'] = x['Adres_nadania'].replace('ul. ', 'al. ')
        x['Adres_odbioru'] = x['Adres_odbioru'].replace('ulica', 'aleja')
        x['Adres_odbioru'] = x['Adres_odbioru'].replace('ul. ', 'al. ')


    # save to CSV files - t2
    if not os.path.exists('./t2'):
        os.mkdir('./t2')
    export_to_csv(gabaryty,'./t2','gabaryty.csv')
    export_to_csv(placowki,'./t2','placowki.csv')
    export_to_csv(statusy,'./t2','statusy.csv')
    export_to_csv(zlecenia,'./t2','zlecenia.csv')
    export_to_csv(transportyzlecenia,'./t2','transportyzlecenia.csv')
    export_to_csv(DzC,'./t2','DzC.csv', True)
    export_to_csv(DoA,'./t2','DoA.csv', True)
