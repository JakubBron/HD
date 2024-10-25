from faker import Faker
import random
import datetime
import json
import string
import csv

# initialize faker

faker = Faker('pl_PL')
# DB and implementation specific
gabaryty_maxTextLen = 20
zlecenia_maxTextLen = 250
our_seed = 2137

# data specific
chance_pno = 0.7
chance_companyPerson = 0.5
chance_truckMalfunction = 0.4
timeStartDate = datetime.datetime(2020, 1, 1)
timeEndDate = datetime.datetime(2024, 10, 25)
timeEndDate_T2 = datetime.datetime(2025, 8, 10)
fuelTypesList = ['ON', 'PB95', 'LPG']
numberOfTrucks = 10
maxMalfunctionsPerTruck = 5
maxUpdated = 5


Faker.seed(our_seed)
random.seed(our_seed)


def generate_gabaryty(number, id=0):
    dict_gabaryty = []
    for i in range(number):
        id = id
        description = faker.text(gabaryty_maxTextLen)
        max_dim_x = random.randint(1, 9999)
        max_dim_y = random.randint(1, 9999)
        max_dim_z = random.randint(1, 9999)
        markup = round(random.uniform(5, 150), 2)
        
        dict_gabaryty.append( { 'ID_gabarytu': id, 
                                'Opis': description,
                                'Wymiar_X': max_dim_x,
                                'Wymiar_Y': max_dim_y,
                                'Wymiar_Z': max_dim_z,
                                'Marza': markup} )
    
    return dict_gabaryty

def generate_placowki(number_pno, number_dyst, id=0):
    dict_placowki = []
    for i in range(number_pno):
        id = id
        address = faker.address().replace('\n', ' ')
        dict_placowki.append({'ID_placowki': id, 'Adres_placowki': address, 'Is_centrum_dystrybucyjne': False})
    for i in range(number_dyst):
        id = id + number_pno
        address = faker.address().replace('\n', ' ')
        dict_placowki.append({'ID_placowki': id, 'Adres_placowki': address, 'Is_centrum_dystrybucyjne': True})
    return dict_placowki

def generate_statusy():
    dict_statusy = [
        {'ID_statusu': 0, 'Opis_statusu': 'Przyjęte'},
        {'ID_statusu': 1, 'Opis_statusu': 'W trakcie realizacji'},
        {'ID_statusu': 2, 'Opis_statusu': 'Zakończone'},
        {'ID_statusu': 3, 'Opis_statusu': 'Anulowane'}
    ]
    return dict_statusy

def generate_zlecenia(number, dict_placowki, dict_gabaryty, dict_statusy, id=0):
    zlecenia = []
    for i in range(number):
        id = id
        phone_number = f'+48{faker.msisdn()[3:]}'
        nazwa_zamawiajacego = ''
        if random.random() <= chance_companyPerson:
            nazwa_zamawiajacego = faker.name()[:zlecenia_maxTextLen]
        else:
            nazwa_zamawiajacego = faker.company()[:zlecenia_maxTextLen]

        all_pno_from_dict = set([x['ID_placowki'] for x in dict_placowki])
        adres_nadania = 'NULL'
        punkt_nadania = 'NULL'
        if random.random() <= chance_pno:
            punkt_nadania = all_pno_from_dict.pop()
        else:
            adres_nadania = faker.address().replace('\n', ' ')

        adres_odbioru = 'NULL'
        punkt_odbioru = 'NULL'
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
            'ID_zlecenia': id,
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

    return zlecenia

def generate_transportyzlecenia(placowki, zlecenia, statusy, id_transportu=0):
    transportyzlecenia = []
    id_trasnportu = id_transportu
    for i in range(len(zlecenia)):
        # jeśli nie wykonaliśmy danego zlecenia (wcale lub jeszcze nie wykonaliśmy), nie ma ono trasy
        if statusy[zlecenia[i]['Status']]['Opis_statusu'] in ['Anulowane', 'Przyjęte']:
            continue
        id_zlecenia = i
        data_poczatek = datetime.datetime.strptime(zlecenia[i]['Data_przyjecia'], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(zlecenia[i]['Data_zakoczenia'], '%Y-%m-%d')
        data_koniec = faker.date_between(start_date=data_poczatek, end_date=end_date)
        skad = 'NULL'
        placowki_dystr_id = set([x['ID_placowki'] for x in placowki if x['Is_centrum_dystrybucyjne']])
        dokad = random.choice(list(placowki_dystr_id))
        placowki_dystr_id.remove(dokad)
        transportyzlecenia.append({
            'ID_zlecenia': id_zlecenia,
            'ID_transportu': id_trasnportu,
            'Data_poczatek': str(data_poczatek)[:10],
            'Data_koniec': str(data_koniec)[:10],
            'Skad': skad,
            'Dokad': dokad
        })

        for j in range(random.randint(0, len(placowki_dystr_id)-1)):
            id_zlecenia = i
            id_trasnportu += 1
            data_poczatek = data_koniec
            data_koniec = faker.date_between(start_date=data_poczatek, end_date=end_date)
            skad = dokad
            dokad = random.choice(list(placowki_dystr_id))
            placowki_dystr_id.remove(dokad)
            transportyzlecenia.append({
                'ID_zlecenia': id_zlecenia,
                'ID_transportu': id_trasnportu,
                'Data_poczatek': str(data_poczatek)[:10],
                'Data_koniec': str(data_koniec)[:10],
                'Skad': skad,
                'Dokad': dokad
            })
        # jeśli zlecenie trwa, zapisujemy tylko etapy już przejechane
        if statusy[zlecenia[i]['Status']]['Opis_statusu'] != 'Zakończone':
            continue

        id_zlecenia = id_zlecenia
        id_trasnportu += 1
        data_poczatek = data_koniec
        data_koniec = end_date
        skad = dokad
        dokad = 'NULL'
        transportyzlecenia.append({
            'ID_zlecenia': id_zlecenia,
            'ID_transportu': id_trasnportu,
            'Data_poczatek': str(data_poczatek)[:10],
            'Data_koniec': str(data_koniec)[:10],
            'Skad': skad,
            'Dokad': dokad
        })
        id_trasnportu+=1


    return transportyzlecenia


def generate_DzC(transportyzlecenia, number_of_trucks, id_transportu=0):
    DzC = []
    for i in range(len(transportyzlecenia)):
        id_transportu = id_transportu
        id_ciezarowki = random.randint(0, number_of_trucks)
        zuzycie_paliwa = random.randint(3, 1000)
        typ_paliwa = random.choice(fuelTypesList)
        # data from Data_koniec and random hours
        data_pomiaru = datetime.datetime.strptime(transportyzlecenia[i]['Data_koniec'], '%Y-%m-%d') + datetime.timedelta(hours=random.randint(1, 24), minutes=random.randint(1, 60), seconds=random.randint(1, 60))
        emisja_tlenkow_wegla = round(300.0 + random.random()*1500,2)
        emisja_tlenkow_azotu = round(20.0 + random.random()*60,2)
        emisja_tlenkow_siarki = round(0.05 + random.random()*10, 2)

        DzC.append({
            'ID transportu': id_transportu,
            'ID ciezarowki': id_ciezarowki,
            'Zuzycie paliwa': zuzycie_paliwa,
            'Typ paliwa': typ_paliwa,
            'Data pomiaru': str(data_pomiaru),
            'Emisja tlenkow wegla': emisja_tlenkow_wegla,
            'Emisja tlenkow azotu': emisja_tlenkow_azotu,
            'Emisja tlenkow siarki': emisja_tlenkow_siarki
        })

    return DzC

def generate_DoA(transportyzlecenia, number_of_trucks, start_id=0):
    DoA = []
    for i in range(len(transportyzlecenia)):
        if random.random() > chance_truckMalfunction:
            continue

        malfunctions_per_truck = random.randint(0, maxMalfunctionsPerTruck)
        for _ in range(malfunctions_per_truck):
            id_transportu = i+start_id
            id_ciezarowki = random.randint(0, number_of_trucks)
            # data from Data_koniec and random hours
            data_awarii = datetime.datetime.strptime(transportyzlecenia[i]['Data_koniec'], '%Y-%m-%d') + datetime.timedelta(hours=random.randint(1, 24), minutes=random.randint(1, 60), seconds=random.randint(1, 60))

            DoA.append({
                'ID transportu': id_transportu,
                'ID ciezarowki': id_ciezarowki,
                'Data awarii': str(data_awarii),
                'Kod awarii': ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(2, 5)))
            })

    return DoA

def export_to_csv(data, filename):
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

############################################################

if __name__ == "__main__":
    # now in T1
    numberOf_gabaryty = 10
    gabaryty = generate_gabaryty(numberOf_gabaryty)

    numberOf_pno = 10
    numberOf_dytryb = 10
    placowki = generate_placowki(numberOf_pno, numberOf_dytryb)

    statusy = generate_statusy()
    
    numberOf_zlecenia = 10
    zlecenia = generate_zlecenia(numberOf_zlecenia, placowki, gabaryty, statusy)
    #print(json.dumps(zlecenia, indent=4))

    numberOf_transportyzlecenia = len(zlecenia)
    transportyzlecenia = generate_transportyzlecenia(placowki, zlecenia, statusy)
    #print(json.dumps(transportyzlecenia, indent=4))

    numberOf_DzC = len(transportyzlecenia)
    DzC = generate_DzC(transportyzlecenia, numberOfTrucks)
    #print(json.dumps(DzC, indent=4))

    numberOf_DoA = len(transportyzlecenia)
    DoA = generate_DoA(transportyzlecenia, numberOfTrucks)
    #print(json.dumps(DoA, indent=4))

    export_to_csv(gabaryty, './t1/gabaryty.csv')
    export_to_csv(placowki, './t1/placowki.csv')
    export_to_csv(statusy, './t1/statusy.csv')
    export_to_csv(zlecenia, './t1/zlecenia.csv')
    export_to_csv(transportyzlecenia, './t1/transportyzlecenia.csv')
    export_to_csv(DzC, './t1/DzC.csv')
    export_to_csv(DoA, './t1/DoA.csv')

    # now in T2
    timeEndDate = timeEndDate_T2
    
    placowki2 = generate_placowki(20, 15, numberOf_pno+numberOf_dytryb)
    for x in placowki2:
        placowki.append(x)
    
    zlecenia2 = generate_zlecenia(20, placowki, gabaryty, statusy, numberOf_zlecenia)
    for x in zlecenia2:
        zlecenia.append(x)
    
    updated = 0
    for i in range(len(zlecenia)):
        if updated < maxUpdated:
            zlecenia[i]['Adres_nadania']=zlecenia[i]['Adres_nadania'].replace('ulica', 'aleja')
            zlecenia[i]['Adres_odbioru']=zlecenia[i]['Adres_odbioru'].replace('ulica', 'aleja')
            updated+=1
    #print(json.dumps(zlecenia, indent=4))

    transportyzlecenia2 = generate_transportyzlecenia(placowki, zlecenia, statusy, numberOf_transportyzlecenia)
    for x in transportyzlecenia2:
        transportyzlecenia.append(x)
    #print(json.dumps(transportyzlecenia, indent=4))

    DzC2 = generate_DzC(transportyzlecenia, numberOfTrucks, numberOf_DzC)
    for x in DzC2:
        DzC.append(x)
    #print(json.dumps(DzC, indent=4))

    DoA2 = generate_DoA(transportyzlecenia, numberOfTrucks, numberOf_DoA)
    for x in DoA2:
        DoA.append(x)
    #print(json.dumps(DoA, indent=4))

    export_to_csv(gabaryty, './t2/gabaryty.csv')
    export_to_csv(placowki, './t2/placowki.csv')
    export_to_csv(statusy, './t2/statusy.csv')
    export_to_csv(zlecenia, './t2/zlecenia.csv')
    export_to_csv(transportyzlecenia, './t2/transportyzlecenia.csv')
    export_to_csv(DzC, './t2/DzC.csv')
    export_to_csv(DoA, './t2/DoA.csv')
    