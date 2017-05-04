from bs4 import BeautifulSoup

from br.stm.univapi.modelos.Boleto import Boleto


class Boletos(object):
    def __init__(self, aluno):
        self.aluno = aluno

    '''
     Retorna uma lista de objetos Boleto com
     os boletos do aluno
     '''

    def lista(self):
        url = 'http://www.siu.univale.br/SIU-PortalAluno/Financeiro/Titulos.aspx'
        pagina_boleto = self.aluno.sessao.get(url)
        soup = BeautifulSoup(pagina_boleto.content.decode('utf-8'), 'html5lib')
        boletos = []
        numero_paginas = len(soup.find('tr', {'class': 'BarrDataControls'}).find('td').find_all('td'))

        # Como já estamos na primeira página, é mais eficiente pegar as informações dela separada das outras
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

            boletos.append(Boleto(ano_mes, vencimento, mensalidade, dependencia, desconto, liquido, situacao))

        # Agora sim pegamos as informações do resto das páginas
        parametros = {
            '__VIEWSTATEENCRYPTED': '',
            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$GridView1',
        }

        # Percorremos cada página
        for i in range(2, numero_paginas + 1):
            parametros['__EVENTARGUMENT'] = 'Page$' + str(i)
            pagina_boleto = self.aluno.sessao.post(url, data=parametros)
            soup = BeautifulSoup(pagina_boleto.content.decode('utf-8'), 'html5lib')

            # Coletamos as informações de cada boleto na tabela
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

                # Adicionamos os dados em um único objeto e então o adicionamos à lista
                boletos.append(Boleto(ano_mes, vencimento, mensalidade, dependencia, desconto, liquido, situacao))
        return boletos
