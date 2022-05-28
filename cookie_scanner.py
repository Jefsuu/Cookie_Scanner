from selenium import webdriver
from selenium.webdriver.common.by import By
#pandas para organizar os cookies que estavam em um formato parecido com json para o formato de tabela 
from pandas import DataFrame, read_csv
#o metodo abaixo serve pra unidimensionar as listas geradas
from pandas.core.common import flatten
#urlib para extrair o dominio da url
from urllib.parse import urlparse
#biblioteca que usa a API do google para traduzir a descrição do cookie, quando disponivel
from googletrans import Translator
#biblioteca para usar converter o formato de data que o navegador retorna em cada cookie
from datetime import datetime
import time
#biblioteca para fazer requisições em sites
import requests
#biblioteca que permite multiprocessamento
from joblib import Parallel, delayed
from itertools import chain
#configurando para que o webdriver seja executado em modo invisivel
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("enable-automation")
options.add_argument("disable-infobars")
options.add_argument('--headless')
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-browser-side-navigation")
options.add_argument("--no-sandbox")
options.add_argument("--dns-prefetch-disable")
prefs = {
    "download_restrictions": 3,
}
options.add_experimental_option(
    "prefs", prefs
)

######################################################

inicio = datetime.now()
#função para calcular o tempo de rentenção do cookie, enviando a data de expiração para um site que calcula a diferença entre datas 
#e pegando o resultado
def calcula_exp(t):
    #pegando a data e horario atual
    now = datetime.now()
    #colocando a data em um formato mais legivel, e separando entre a data e o horario
    datesplit = datetime.strftime(now, '%d/%m/%Y %H:%M:%S').split(' ')
    #um try para tentar executar esse trecho do código, porque pode acontecer do navegador voltar uma data grande que a conversão
    #para um formato legivel não é possivel
    try :
        if t != None:
            #convertendo a data de expiração que veio do cookie
            dt = time.strftime(r'%d/%m/%Y %H:%M:%S', time.localtime(t))
            #contruindo o dicionario a ser enviado na requisição ao site
            #t1 e t2 são referentes a data e horario inicial
            #t3 e t4 são referentes a data e horario finais, ou seja, a data de expiração do cookie
            date = {
                'ca': '1',
                't1': f"{datesplit[0].split('/')[0]}-{datesplit[0].split('/')[1]}-{datesplit[0].split('/')[2]}",
                't2': f"{datesplit[1].split(':')[0]}:{datesplit[1].split(':')[1]}:{datesplit[1].split(':')[2]}",
                't3': f"{dt.split(' ')[0].split('/')[0]}-{dt.split(' ')[0].split('/')[1]}-{dt.split(' ')[0].split('/')[2]}",
                't4': f"{dt.split(' ')[1].split(':')[0]}:{dt.split(' ')[1].split(':')[1]}:{dt.split(' ')[1].split(':')[2]}"   
            }
            #enviando a requisição para o site e ja pegando o resultado, que é uma string
            data_conv = requests.post('https://www.calcule.net/calendario/calculadora-de-datas-calcular-dias-meses-semanas-horas/', data=date).content
            
            #separando a string nos segmentos de interesse, está em um try pois as pode acontecer do site não conseguir calcular a diferença
            try:
                datas = data_conv.decode('utf-8').split('|')[4:]
                ano = int(datas[0].replace('+',''))
                mes = int(datas[1].replace('+',''))
                dia = int(datas[2].replace('.', ''))
                semanas = int(datas[3].replace('.', ''))
                horas = int(datas[4].replace('.', ''))
                minutos = int(datas[5].replace('.', ''))
                segundos = int(datas[6].replace('.', ''))
            except:
                return ""

            #IFs para atriuir o tempo de retenção ao cookie
            if ano > 0:
                if mes > 0:
                    date_v = f'{ano} ano(s) e {mes} mese(s)' 
                    dia = 0
                    semanas = 0
                    minutos = 0
                    horas = 0
                    ano = 0
                    
                if (mes < 0) and (ano > 0):
                    date_v = f'{ano} ano(s)'
                    ano = 0
                    mes = 0
                    dia = 0
                    semanas = 0
                    minutos = 0
                    horas = 0
                    
            elif (mes > 0 ):
                date_v = f'{mes} mese(s)'
                ano = 0
                mes = 0
                dia = 0
                semanas = 0
                minutos = 0
                horas = 0
                
            elif (semanas > 0):
                date_v = f'{semanas} semana(s)'
                ano = 0
                mes = 0
                dia = 0
                semanas = 0
                minutos = 0
                horas = 0
                date_v
            elif (dia > 0):
                date_v = f'{dia} dia(s)'
                ano = 0
                mes = 0
                dia = 0
                semanas = 0
                minutos = 0
                horas = 0
                
            elif horas > 0:
                date_v = f'{horas} hora(s)'
                ano = 0
                mes = 0
                dia = 0
                semanas = 0
                minutos = 0
                horas = 0
                
            elif minutos > 0:
                date_v = f'{minutos} minuto(s)'
                ano = 0
                mes = 0
                dia = 0
                semanas = 0
                minutos = 0
                horas = 0
            elif (minutos == 0) and (segundos == 0):
                date_v = '1 minuto'
            return date_v
        else:
            None
    #se tudo der errado, a função simplemente retorna a data de expiração da mesma forma que o navegador retorna
    except:
        try:
            dt = time.strftime(r'%d/%m/%Y %H:%M:%S', time.localtime(t))
            return dt
        except:
            return t
        
#função para capturar os cookies dos links, essa função será usada para o multiprocessamento
def captura_cookies(link):
    #abre um novo webdriver que herda as option estabelecidas anteriormente
    c = []
    nav = webdriver.Chrome(options=options)
    #entra no link
    print(f'\n\nAcessando: {link}...')
    try:
        nav.get(link)
        #pega cada cookie
        for a in nav.get_cookies():
            
            #procura a chave 'expiry' no dict do cookie e se encontrar, pega esse valor e envia para a função que calcula a diferença
            # e cria uma nova chave 'Retention' onde será armazenado o tempo de retenção desse cookie
            if a.get('expiry'):
                a['Retention'] = calcula_exp(a['expiry'])
            else:
                a['expiry'] = None
                a['Retention'] = None
            #adiciona o cookie na lista de cookies da função scan_cookies
            c.append(a)
            with open('cookies.json', 'a') as cookieJson:
                cookieJson.write(f"\n{a}")
        #sai do navegador
        nav.quit()

        return c
    except:
        #escrevendo os links que não puderam ser acessados
        with open('temp_links.txt', 'a') as temFile:
            temFile.write(f"\n{link}")
    

def scan_cookies(site):
    translator = Translator()
    
    #extraindo o dominio do site e scheme do site
    domain = urlparse(site).netloc
    scheme = urlparse(site).scheme
    #iniciando o webdriver
    driver = webdriver.Chrome(options=options)
    #acessando o site
    driver.get(site)
    #pegando os cookies da primeira pagina e salvando em uma lista
    cookies = []
    for i in driver.get_cookies():
        if i.get('expiry'):
            i['Retention'] = calcula_exp(i['expiry'])
        else:
            i['expiry'] = None
            i['Retention'] = None
        cookies.append(i)
        with open('cookies.json', 'a') as cookieJson:
                cookieJson.write(f"\n{i}")

    #pegando todos os links da pagina principal
    links = [i.get_attribute('href') for i in driver.find_elements(By.TAG_NAME, 'a')]
    #retirando os links invalidos e os links com extensão de arquivos, para evitar acessar links de download
    links = [i for i in links if (i != None) and (i != '') and (scheme in i) and (i.endswith('pdf') == False) and (i.endswith('jpg') == False) \
        and (i.endswith('odt') == False) and (i.endswith('png') == False) and (i.endswith('xlsx') == False) and (i.endswith('docx') == False) \
            and (i.endswith('pptx') == False) and (i.endswith('txt') == False) and ('editais' not in i)]

    #acessando os links da lista e se o link for do mesmo dominio do site, pega todo os links desse link. Se o dominio for diferente, 
    #adiciona o link em uma lista diferente que depois irá ser anexada a lista de links
    url = []
    links_externos = []
    for i in links:
        try:
            driver.get(i)
            if urlparse(i).netloc == domain:
                url.append([x.get_attribute('href') for x in driver.find_elements(By.TAG_NAME, 'a')])
            else:
                """for a in driver.get_cookies():
                    if a.get('expiry'):
                        a['Retention'] = calcula_exp(a['expiry'])
                    else:
                        a['expiry'] = None
                    cookies.append(a)"""
                links_externos.append(i)
        except:
            with open('temp_links.txt', 'a') as temFile:
                temFile.write(f"\n{i}")

    #como todos os links ja foram coletados, fecha o navegador
    driver.quit()
    #junta a lista gerada acima com a lista de links
    links.append(url)
    links.append(links_externos)
    #unidimensiona a lista de links
    links = list(flatten(links))
    #retirando os links invalidos e os links com extensão de arquivos, para evitar acessar links de download
    links = [i for i in links if (i != None) and (i != '') and (scheme in i) and (i.endswith('pdf') == False) and (i.endswith('jpg') == False) \
        and (i.endswith('odt') == False) and (i.endswith('png') == False) and (i.endswith('xlsx') == False) and (i.endswith('docx') == False) \
            and (i.endswith('pptx') == False) and (i.endswith('txt') == False) and ('editais' not in i)]
    #removendo links duplicados
    links = list(set(links))

    print(f"Quantidade de links: {len(links)}")
    print(f"\nTempo estimado: {(15 * len(links))/240} Minutos")

    #entrando em cada link e coletando os cookies e armazenando cada um na lista [cookies]
    """for x in links:
        driver.get(x)
        for a in driver.get_cookies():
            if a.get('expiry'):
                a['Retention'] = calcula_exp(a['expiry'])
            else:
                a['expiry'] = None
            
            cookies.append(a)"""


    #realizando o multiprocessing, o -1 indica o uso de todos os nucleos disponiveis
    #a função captura_cookies() é executada simultaneamente de acordo com a quantiade de nucloes
    #se houverem 4 nucloes, ela pega 4 links da lista e atribui um para cada função que esta sendo executada
    #o verbose > 10 indica que todas mensagens geradas devem ser apresentadas, para retirar basta tirar o parametro ou colocar =0
    #verificar documentação da biblioteca para mais esclarecimentos https://joblib.readthedocs.io/en/latest/parallel.html

    multiprocess = Parallel(n_jobs=-1, backend='loky', verbose=11)(delayed(captura_cookies)(i) for i in links)

    multiprocess = [i for i in multiprocess if (type(i) != type(None)) and (len(i)>0) and (i != None)]

    #escrevendo os links do multiprocess em um txt
    """try:
        with open('multprocess.txt', 'a') as processFile:
            processFile.write(multiprocess)
    except:
        None"""

    #adcionando os resultados do processamento paralelo na lista de cookies
    for cookie in chain.from_iterable(multiprocess):
        cookies.append(cookie)
    

    #limpando o link do site para gerar um nome para o arquivo de saida
    nameFile = domain.replace('www.', '').replace('https://', '').replace('http://', '').split('.com')[0]
    #nameFile = site.replace(".", "").replace(":", "").replace("/", "")
    #path = os.path.dirname(os.path.abspath(__file__)) + '/temp'

    #Cria um dataframe com os cookies encontrados, remove os cookies duplicados com base no 'domain' e 'name'.
    #coleta uma base de cookies localizada no github, faz um merge entre o resultados do scan e a base para obter mais informações sobre os cookies encontrados
    df = DataFrame(cookies).drop_duplicates(['domain','name']).reset_index(drop=True)\
        .merge(read_csv('https://raw.githubusercontent.com/jkwakman/Open-Cookie-Database/master/open-cookie-database.csv',
    usecols=['Platform','Category', 'Domain', 'Description', 'Retention period', 'Data Controller', 'User Privacy & GDPR Rights Portals','Cookie / Data Key name']),
    how='left', left_on='name', right_on='Cookie / Data Key name')

    #definindo se o cookie é first-party ou third-party de acordo com o dominio
    cookie_type = []
    for d in df.domain:
        if (domain in d) and (d in domain):
            cookie_type.append('First-party')
        else:
            cookie_type.append('Third-party')

    #adicionando o uma coluna ao dataframe com o tipo do cookie
    df['Cookie type'] = cookie_type

    #pega o valor de expiração que o navegador retorna, transforma em um formato legivel
    #se não for possivel realizar esse calculo, 99% das vezes é porque o valor não foi econtrado, então o cookie expira com a sessão
    expiration = []
    for d in df.expiry:
        try:
            expiration.append(time.strftime(r'%d/%m/%Y %H:%M:%S', time.localtime(d)))
        except:
            expiration.append('Session')
    #adicionando a coluna 'Expiration' no df
    df['Expiration'] = expiration
    #preenchendo os valores vazios da coluna 'Retention' com Session
    df['Retention'] = df['Retention'].fillna('Session')
    #traduzindo a descrição do cookie, usando a api do google
    df['Descrição'] = [translator.translate(text=i, src='en', dest='pt').text for i in df['Description'].to_list()]
    
    ponto = []
    for i in df['Descrição'].to_list():
        if len(i)>0:
            if i[-1] != '.':
                i = i + '.'
                ponto.append(i)
            else:
                ponto.append(i)
        else:
                ponto.append(i)
    
    df['Descrição'] = ponto

    #Definindo quais colunas serão utilizadas
    df = df[['name', 'domain', 'Cookie type','Retention','Expiration','Category','Descrição', 'Data Controller', 'User Privacy & GDPR Rights Portals']]
    #Limpando valores invalidos restantes
    df = df.fillna('').replace('Nan', '').replace('Nan.', '')
    #df.to_excel(f'{nameFile}.xlsx', index=False)
    return df

#importante chamar a função passando o schema(https ou http) no link 
scan_cookies('https://www.site.com')
