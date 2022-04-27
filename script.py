from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common import keys
from pandas import read_html, DataFrame, ExcelWriter
from bs4 import BeautifulSoup
from time import sleep
import re
from googletrans import Translator

options = webdriver.ChromeOptions()
options.add_argument('--headless')
from urllib.parse import urlparse

def script(lista):

    driver = webdriver.Chrome(options=options)
    planilha = ExcelWriter('relatório cookie-script.xlsx', engine='xlsxwriter')
    translator = Translator()

    for x in lista:
        driver.get('https://cookie-script.com/cookie-scanner')
        s = driver.find_element(By.XPATH, value='//*[@id="scandomain"]')
        s.clear()
        s.send_keys(x)
        driver.find_element(By.XPATH, value='//*[@id="btn-1626345321042"]').click()
        element = WebDriverWait(driver, 240).until(EC.presence_of_element_located((By.XPATH, '//*[@id="t3-content"]/div[3]')))
        sleep(3)
        soup = BeautifulSoup(element.get_attribute('outerHTML'))


        df = DataFrame(columns=['Cookie key','Domain', 'Path', 'Cookie type', 'Expiration', 'Description', 'Tipo'])

        for i in soup.find_all(class_='reporttitle'):
            temp = read_html(i.find_next('table', class_='reporttable table').prettify(), flavor='bs4')[0]
            temp['Tipo'] = re.sub(r'[~^0-9]', '',i.text)
            df = df.append(temp)
        
        df.reset_index(drop=True, inplace=True)
        df.drop([i for i in range(len(df)) if i%2!=0 ], inplace=True)
        df.reset_index(drop=True, inplace=True)
        df['Cookie key'] = df['Cookie key'].str.replace('  More info', '')
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)

        df['Descrição'] = [translator.translate(text=i, src='en', dest='pt').text for i in df['Description'].to_list()]

        df.to_excel(planilha, sheet_name=urlparse(x).netloc, index=False)

    planilha.save()
    planilha.close()
    driver.quit()
    

script(lista=['https://www.google.com', 'https://twitter.com'])