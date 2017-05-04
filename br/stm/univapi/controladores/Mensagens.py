from bs4 import BeautifulSoup

from br.stm.univapi.modelos.Mensagem import Mensagem


class Mensagens(object):
    def __init__(self, aluno):
        self.aluno = aluno

    '''
       Retorna uma lista de objetos Mensagem com
       as mensagens do aluno.
       '''

    def lista(self):
        mensagens = []
        url = 'http://www.siu.univale.br/SIU-PortalAluno/CaixaPostal/CaixaPostal.aspx'
        categorias = ['ctl00$ContentPlaceHolder1$lkbCaixaEntrada', 'ctl00$ContentPlaceHolder1$lkbLidas']
        pedido_get = self.aluno.sessao.get(url)
        soup = BeautifulSoup(pedido_get.content.decode('utf-8'), 'html5lib')
        parametros = {
            '__VIEWSTATEENCRYPTED': '',
            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
        }
        for categoria in categorias:
            parametros['__EVENTTARGET'] = categoria
            pedido_post = self.aluno.sessao.post(url, data=parametros)
            soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

            parametros.update({
                '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
                '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value']
            })
            for msg in soup.find(id=lambda x: x and '_gvMensagem' in x).find_all('tr', {
                    'class': lambda x: x and 'ItemGrid' in x}):
                remetente = msg.find('a', id=lambda x: x and '_lkbDe' in x).contents[0]
                data = msg.find('a', id=lambda x: x and '_lkbData' in x).contents[0]

                tag_assunto = msg.find('a', id=lambda x: x and '_lkbAssunto' in x)
                assunto = ' '.join(tag_assunto.contents[0].split())

                link_mensagem = tag_assunto['href'].split('(\'')[1].split('\',')[0]
                parametros['__EVENTTARGET'] = link_mensagem
                pedido_post = self.aluno.sessao.post(url, data=parametros)
                soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

                conteudo = soup.find('div', id='Corpo').contents[4]
                mensagens.append(Mensagem(remetente, data, assunto, conteudo))

        return mensagens
