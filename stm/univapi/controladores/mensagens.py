import json

from bs4 import BeautifulSoup
from urllib3.exceptions import ProtocolError

from stm.univapi.auxiliares import paginas
from stm.univapi.auxiliares.controlador import Controlador
from stm.univapi.auxiliares.paginas import Pagina
from stm.univapi.modelos.mensagem import Mensagem


class Mensagens(Controlador):
    def __init__(self, aluno):
        self.aluno = aluno

    '''
    Itera sobre cada mensagem da página fornecida,
    adicionando a mensagem à lista especificada
    '''

    def __adicionar_mensagens(self, soup, lista, parametros, url):
        for msg in soup.find(id=lambda x: x and '_gvMensagem' in x).find_all(
                'tr', {'class': lambda x: x and 'ItemGrid' in x}):
            # Nome do remetente
            remetente = msg.find('a', id=lambda x: x and '_lkbDe' in x).contents[0]

            # Data de recebimento
            data = msg.find('a', id=lambda x: x and '_lkbData' in x).contents[0]

            tag_assunto = msg.find('a', id=lambda x: x and '_lkbAssunto' in x)

            # Assunto da mensagem
            assunto = ' '.join(tag_assunto.contents[0].split())

            link_mensagem = tag_assunto['href'].split('(\'')[1].split('\',')[0]
            parametros['__EVENTTARGET'] = link_mensagem

            # Abrimos a página da mensagem para ver seu conteúdo
            pedido_post = self.aluno.sessao.post(url, data=parametros)
            soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

            # Conteúdo da mensagem
            conteudo = ' '.join(soup.find('div', id='Corpo').contents[4].replace('\n', ' ').split())

            lista.append(Mensagem(remetente, data, assunto, conteudo))

    '''
    Retorna uma lista de objetos Mensagem com
    as mensagens do aluno.
    '''

    def lista(self):
        mensagens = []
        try:
            url = paginas.get_url(Pagina.mensagens, True)
            pedido_get = self.aluno.sessao.get(url)
            soup = BeautifulSoup(pedido_get.content.decode('utf-8'), 'html5lib')

            parametros = {
                '__VIEWSTATEENCRYPTED': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
                '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
                '__PREVIOUSPAGE': soup.find('input', {'name': '__PREVIOUSPAGE'})['value']
            }

            # Obtemos as mensagens novas
            self.__adicionar_mensagens(soup, mensagens, parametros, url)

            # Mandamos um pedido para abrir a página de mensagens lidas
            parametros['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$lkbLidas'

            pedido_post = self.aluno.sessao.post(url, data=parametros)
            soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

            parametros.update({
                '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
                '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
                '__PREVIOUSPAGE': soup.find('input', {'name': '__PREVIOUSPAGE'})['value']
            })

            # Obtemos as mensagens lidas
            self.__adicionar_mensagens(soup, mensagens, parametros, url)
        except (AttributeError, IOError, ConnectionError, ProtocolError):
            mensagens.clear()
        return mensagens

    '''
    Retorna todas as mensagens em formato JSON
    '''

    def to_json(self):
        return json.dumps([mensagem.__dict__ for mensagem in self.lista()], ensure_ascii=False)
