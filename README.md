# Cookie_Scanner
 Um scanner de cookies desenvolvido com python utilizando selenium para navegar pelos links da pagina e coletar os cookies identificados pelo navegador.
 
 #### Funcionamento
 * **coleta dos links**

 Ao passar o link do site para a função, preferencialmente o link da home page, o scanner coleta os cookies e todos os links dessa pagina. A seguir, scanner entra em todos esses links, e se o dominio do link for o mesmo, os links são novamente coletados, caso o dominio não seja o mesmo, somente o link da pagina é armazenado.
 
 * **limpeza dos links**
 
 Todos os links coletados são armazenados em listas, depois essas listas são unificadas e unidimensionadas. A partir disso, é feito a limpeza de links invalidos e links que possam direcionar para algum download, como o de algum PDF. E claro, também são removidos os links duplicados.
 
* **coleta dos cookies**

 Depois de coletar todos os links e limpa-los, começa a parte de coleta dos cookies. Os links que estão armazenados em uma lista, vão ser acessados e será utilizado a função get_cookies() do selenium para coletar os cookies e armazena-los. 
 
 * **tratamento nos cookies coletados**

Os cookies coletados são inseridos em um DataFrame do pandas, para que estes possam ser tratados. Após o armazenamento nesse DF, é feito um join entre esse DF e uma base
com informações sobre cookies, nessa base é possivel encontrar a categoria, descrição e o responsável por diversos cookies.

[Clique aqui para acessar a base](https://github.com/jkwakman/Open-Cookie-Database/)
 
 Alem disso, como o formato de tempo de expiração que o navegador retorna não segue um padrão legivel por humanos, essas datas passam por um tratamento. Assim, alem dessa transformação, tambem é calculado o tempo restante para a expiração do cookie, fazendo uma requisição no site https://www.calcule.net/calendario/calculadora-de-datas-calcular-dias-meses-semanas-horas/
 
 E algumas informações que o navegador retorna, são removidas, pois não são de interesse. Mas claro, isso pode ser personalizado no script do scanner. Bem como, também são retirados os cookies duplicados com base no nome do cookie e no dominio no qual foi encontrado.
 
 Também são traduzidas as descrições que a base de cookies disponibiliza, utilizando uma API de tradução do google a partir da biblioteca. [Veja mais aqui](https://pypi.org/project/googletrans/)
 
 Também é definido se o cookie é First-party ou Third-part, com base no dominio do cookie.
 
 * Resultado

O resultado do scan é um arquivo json onde se encontram todos os cookies coletados e tratados, é possivel mudar formato de saida para excel, csv e outros, basta mudar a forma de salvamento do DF na linha 304.
 
 ## Obervações
 Como muitas vezes, a quantidade de links a serem analisados é muito grande, foi utilizado um recurso de computação paralela para acelerar o processo que algumas vezes
 levava mais de uma hora. O scanner está configurado para utilizar todos os processadores disponiveis no computador, por isso seu computador pode ficar bem lento durante a execução.
 
 Para mudar o numero de processadores utilizados, encontra a função Parallel e mude o parametro n_jobs para o numero de processadores que serão utilizados, esta função se encontra na linha 253.
 
 
 
