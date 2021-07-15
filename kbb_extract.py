# -*- coding: utf-8 -*-
import requests.exceptions
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib3, sys, os
from bs4 import BeautifulSoup
import re
import pandas as pd
from time import sleep
import datetime
import os, sys
from collections import defaultdict
from itertools import repeat

output_path = os.path.dirname(os.path.realpath(__file__)) + '/output'

def getBeautifulSoup(page):
    url = page
    agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    retries = Retry(total=10, connect=5, read=2, backoff_factor=0.8)
    http = urllib3.PoolManager(retries=retries)
    page = http.request('GET', url, headers=agent)
    return BeautifulSoup(page.data, features='lxml')

def getVehicleWebpage(page):
    webpage = []
    soup = getBeautifulSoup(page)
    for description in soup.find_all('div', attrs={'class': 'item-card-body margin-bottom-auto'}):
        for website in description.find_all('div', attrs={'class':'display-flex justify-content-between'}):
            for address in website.find_all('a', attrs={'rel':'nofollow'}):
                webpage.append('https://www.kbb.com' + address.get('href'))
    df = pd.DataFrame(webpage, columns = ['Webpage'])
    return df


def getVehicleName(page):
    soup = getBeautifulSoup(page)
    return soup.find('h1').text

def getVehicleMileage(page):
    mileage = []
    soup = getBeautifulSoup(page)
    for feature in soup.find_all('li', attrs={'class':'list-bordered list-condensed'}):
        if feature.find('div', attrs={'aria-label':'MILEAGE'}) is not None:
            mileage.append(feature.text)
    try:
        return mileage[0]
    except IndexError:
        return None

def getVehicleEngine(page):
    engine = []
    soup = getBeautifulSoup(page)
    for feature in soup.find_all('li', attrs={'class':'list-bordered list-condensed'}):
        if feature.find('div', attrs={'aria-label':re.compile('^ENGINE*')}) is not None:
                engine.append(feature.text)
    try:
        return engine[0]
    except IndexError:
        return None

def getVehicleTransmission(page):
    transmission = []
    soup = getBeautifulSoup(page)
    for feature in soup.find_all('li', attrs={'class':'list-bordered list-condensed'}):
        if feature.find('div', attrs={'aria-label':re.compile('^TRANSMISSION*')}) is not None:
            transmission.append(feature.text)
    try:
        return transmission[0]
    except IndexError:
        return None

def getVehicleDriveType(page):
    drive_type = []
    soup = getBeautifulSoup(page)
    for feature in soup.find_all('li', attrs={'class':'list-bordered list-condensed'}):
        if feature.find('div', attrs={'aria-label':re.compile('^DRIVE TYPE*')}) is not None:
            drive_type.append(feature.text)
    try:
        return drive_type[0]
    except IndexError:
        return None

def getVehicleMPG(page):
    mpg = []
    soup = getBeautifulSoup(page)
    for feature in soup.find_all('li', attrs={'class':'list-bordered list-condensed'}):
        if feature.find('div', attrs={'aria-label':re.compile('^MPG*')}) is not None:
            mpg.append(feature.text)
    try:
        return mpg[0]
    except IndexError:
        return None

def getVehicleEVRange(page):
    ev = []
    soup = getBeautifulSoup(page)
    for feature in soup.find_all('li', attrs={'class':'list-bordered list-condensed'}):
        if feature.find('div', attrs={'aria-label':re.compile('^EV RANGE*')}) is not None:
            ev.append(feature.text)
    try:
        return ev[0]
    except IndexError:
        return None

def getVehicleColor(page):
    color = []
    soup = getBeautifulSoup(page)
    for feature in soup.find_all('li', attrs={'class':'list-bordered list-condensed'}):
        if feature.find('div', attrs={'class':re.compile('^color-swatch margin*')}) is not None:
            color.append(feature.text)
    try:
        return ', '.join(color).strip()
    except IndexError:
        return None

def getVehiclePice(page):
    pricing = []
    soup = getBeautifulSoup(page)
    for price in soup.find_all('span', attrs={'class':'first-price'}):
        pricing.append(price.text)
    try:
        return pricing[0]
    except IndexError:
        return None

def outputResults(model, year):
    df = getVehicleWebpage('https://www.kbb.com/cars-for-sale/all/' + str(year) + '/mercedes-benz/' + model + '/san-francisco-ca-94111?distance=0&dma=&searchRadius=0&location=&marketExtension=include&isNewSearch=true&showAccelerateBanner=false&sortBy=relevance&numRecords=25')
    df['Price']=df['Webpage'].apply(getVehiclePice)
    df['Vehicle']=df['Webpage'].apply(getVehicleName)
    df['Color']=df['Webpage'].apply(getVehicleColor)
    df['EV Range']=df['Webpage'].apply(getVehicleEVRange)
    df['MPG']=df['Webpage'].apply(getVehicleMPG)
    df['Drive Type']=df['Webpage'].apply(getVehicleDriveType)
    df['Engine'] = df['Webpage'].apply(getVehicleEngine)
    df['Transmission']=df['Webpage'].apply(getVehicleTransmission)
    df['Mileage']=df['Webpage'].apply(getVehicleMileage)
    df.to_csv(output_path + '/' + model.upper() + ' ' + str(year) + '.csv', index=False, encoding='utf-8')