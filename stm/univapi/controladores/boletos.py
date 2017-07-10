import json

from bs4 import BeautifulSoup
from urllib3.exceptions import ProtocolError

from stm.univapi.auxiliares import paginas
from stm.univapi.auxiliares.controlador import Controlador
from stm.univapi.auxiliares.paginas import Pagina
from stm.univapi.modelos.boleto import Boleto


class Boletos(Controlador):
    def __init__(self, aluno):
        self.aluno = aluno

    @staticmethod
    def __adicionar_boletos(soup, lista_boletos):
        for linha in soup.find(id='ctl00_ContentPlaceHolder1_GridView1').find_all(
                'tr', {'class': lambda x: x and 'ItemGrid' in x}):
            tags = linha.find_all('td')

            ano_mes = tags[0].contents[0]
            vencimento = tags[1].contents[0]
            mensalidade = tags[2].contents[0]
            dependencia = tags[3].contents[0]
            desconto = tags[4].contents[0]
            liquido = tags[5].contents[0]
            situacao = ' '.join(tags[6].contents[0].split())

            lista_boletos.append(Boleto(ano_mes, vencimento, mensalidade, dependencia, desconto, liquido, situacao))

    '''
     Retorna uma lista de objetos Boleto com
     os boletos do aluno
     '''

    def lista(self):
        boletos = []
        try:
            url = paginas.get_url(Pagina.boletos, True)
            pagina_boleto = self.aluno.sessao.get(url)
            soup = BeautifulSoup(pagina_boleto.content.decode('utf-8'), 'html5lib')
            numero_paginas = len(soup.find('tr', {'class': 'BarrDataControls'}).find('td').find_all('td'))

            # Como já estamos na primeira página, é mais eficiente pegar as informações dela separada das outras
            self.__adicionar_boletos(soup, boletos)

            # Agora sim pegamos as informações do resto das páginas
            parametros = {
                '__VIEWSTATEENCRYPTED': '',
                '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
                '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$GridView1',
            }

            # Se existir mais do que uma página
            if numero_paginas > 1:
                # Percorremos cada página
                for i in range(2, numero_paginas + 1):
                    parametros['__EVENTARGUMENT'] = 'Page$' + str(i)
                    pagina_boleto = self.aluno.sessao.post(url, data=parametros)
                    soup = BeautifulSoup(pagina_boleto.content.decode('utf-8'), 'html5lib')

                    # Coletamos as informações de cada boleto na tabela
                    self.__adicionar_boletos(soup, boletos)
        except (AttributeError, IOError, ConnectionError, ProtocolError):
            boletos.clear()
        return boletos

    '''
    Retorna todos os boletos em formato JSON
    '''

    def to_json(self):
        return json.dumps([boleto.__dict__ for boleto in self.lista()], ensure_ascii=False)
