import json

from bs4 import BeautifulSoup

from br.stm.univapi.auxiliares import Paginas
from br.stm.univapi.auxiliares.Paginas import Pagina
from br.stm.univapi.modelos.Mensagem import Mensagem


class Mensagens(object):
    def __init__(self, aluno):
        self.aluno = aluno

    '''
    Itera sobre cada mensagem da página fornecida,
    adicionando a mensagem à lista especificada
    '''

    def __get_mensagens(self, soup, lista, parametros, url):
        for msg in soup.find(
                id=lambda x: x and '_gvMensagem' in x).find_all('tr', {'class': lambda x: x and 'ItemGrid' in x}):
            remetente = msg.find('a', id=lambda x: x and '_lkbDe' in x).contents[0]
            data = msg.find('a', id=lambda x: x and '_lkbData' in x).contents[0]

            tag_assunto = msg.find('a', id=lambda x: x and '_lkbAssunto' in x)
            assunto = ' '.join(tag_assunto.contents[0].split())

            link_mensagem = tag_assunto['href'].split('(\'')[1].split('\',')[0]
            parametros['__EVENTTARGET'] = link_mensagem

            pedido_post = self.aluno.sessao.post(url, data=parametros)
            soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

            conteudo = ' '.join(soup.find('div', id='Corpo').contents[4].replace('\n', ' ').split())
            lista.append(Mensagem(remetente, data, assunto, conteudo))

    '''
    Retorna uma lista de objetos Mensagem com
    as mensagens do aluno.
    '''

    def lista(self):
        mensagens = []
        try:
            url = Paginas.get_url(Pagina.mensagens, True)
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
            self.__get_mensagens(soup, mensagens, parametros, url)

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
            self.__get_mensagens(soup, mensagens, parametros, url)
        except AttributeError:
            pass
        return mensagens

    '''
    Retorna todas as mensagens em formato JSON
    '''

    def to_json(self):
        return json.dumps([mensagem.__dict__ for mensagem in self.lista()], ensure_ascii=False)
