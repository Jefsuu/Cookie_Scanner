#importando as bibliotecas necessárias
#selenium para acessar as paginas, coletar os links e os cookies
from selenium import webdriver
from selenium.webdriver.common.by import By
#pandas para organizar os cookies que estavam em um formato parecido com json para o formato de tabela 
from pandas import DataFrame, read_csv
#o metodo abaixo serve pra unidimensionar as listas geradas
from pandas.core.common import flatten
#urlib para extrair o dominio da url
from urllib.parse import urlparse

#configurando para que o webdriver seja executado em modo inivisivel
options = webdriver.ChromeOptions()
options.add_argument('--headless')

#função criada para scanear o site
def scan_cookies(site):
    #extraindo o dominio do site e scheme do site
    domain = urlparse(site).netloc
    scheme = urlparse(site).scheme
    #iniciando o webdriver
    driver = webdriver.Chrome(options=options)
    #acessando o site
    driver.get(site)
    #pegando os cookies da primeira pagina e salvando em uma lista
    cookies = [i for i in driver.get_cookies()]
    #pegando todos os links da pagina principal
    links = [i.get_attribute('href') for i in driver.find_elements(By.TAG_NAME, 'a')]
    #retirando os links invalidos
    links = [i for i in links if (i != None) and (i != '') and (scheme in i)]

    #acessando os links da lista e se o link for do mesmo dominio do site, pega todo os links desse link. Se o dominio for diferente, somente os 
    #cookies e sai da pagina
    url = []
    for i in links:
        driver.get(i)
        if urlparse(i).netloc == domain:
            url.append([x.get_attribute('href') for x in driver.find_elements(By.TAG_NAME, 'a')])
        else:
            for a in driver.get_cookies():
                cookies.append(a)

    #junta a lista gerada acima com a lista de links
    links.append(url)
    #unidimensiona a lista de links
    links = list(flatten(links))
    #limpando links invalidos
    links = [i for i in links if (i != None) and (i != '') and (scheme in i)]
    #removendo links duplicados
    links = list(set(links))

    #entrando em cada link e coletando os cookies e armazenando cada um na lista [cookies]
    for x in links:
        driver.get(x)
        for a in driver.get_cookies():
            cookies.append(a)
    #fechando o webdriver
    driver.quit()

    #limpando o link do site para gerar um nome para o arquivo de saida
    nome = domain.split('.com')[0]

    #Cria um dataframe com os cookies encontrados, remove os cookies duplicados com base no 'domain' e 'name'.
    #coleta uma base de cookies localizada no github, faz um merge entre o resultados do scan e a base para obter mais informações sobre os cookies encontrados
    DataFrame(cookies).drop_duplicates(['domain','name']).reset_index(drop=True)\
        .merge(read_csv('https://raw.githubusercontent.com/jkwakman/Open-Cookie-Database/master/open-cookie-database.csv',
    usecols=['Platform','Category', 'Domain', 'Description', 'Retention period', 'Data Controller', 'User Privacy & GDPR Rights Portals','Cookie / Data Key name']),
    how='left', left_on='name', right_on='Cookie / Data Key name').to_excel(f'Relátorio de cookies {nome}.xlsx', index=False)
    #criando um arquivo com os links analisados
    with open(f'Links analisados {nome}.txt', 'w') as f:
        for i in links:
            f.write(i)
            f.write('\n')
        f.close()

#chamando a função e passando o link do site a ser analisado
scan_cookies('https://www.google.com/')