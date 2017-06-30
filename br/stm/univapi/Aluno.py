import platform

import requests
from bs4 import BeautifulSoup

from br.stm.univapi.auxiliares import Paginas
from br.stm.univapi.auxiliares.Paginas import Pagina
from br.stm.univapi.controladores.Boletos import Boletos
from br.stm.univapi.controladores.Perfil import Perfil
from br.stm.univapi.controladores.Disciplinas import Disciplinas
from br.stm.univapi.controladores.Horarios import Horarios
from br.stm.univapi.controladores.Mensagens import Mensagens


class Aluno(object):
    def __init__(self, matricula, senha):
        self.matricula = matricula
        self.senha = senha
        self.sessao = requests.Session()
        # Alteramos os cabeçalhos dos nossos pedidos para não sermos confundidos com robôs
        self.sessao.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3'
        })

        self.disciplinas = Disciplinas(self)
        self.boletos = Boletos(self)
        self.mensagens = Mensagens(self)
        self.horarios = Horarios(self)
        self.perfil = Perfil(self)

    '''
    Inicia uma sessão no portal. Sem este
    método, os outros não funcionam.
    '''

    def autenticar(self):
        url_login = Paginas.get_url(Pagina.login, False)

        pedido_get = self.sessao.get(url_login)

        if pedido_get.status_code == 200:
            # Pegamos os parâmetros necessários para autenticar
            soup = BeautifulSoup(pedido_get.content.decode('utf-8'), 'html5lib')
            parametros = {
                'ctl00$ContentPlaceHolder1$btnLogar': 'OK',
                'ctl00$ContentPlaceHolder1$txtMatricula': self.matricula,
                'ctl00$ContentPlaceHolder1$txtSenha': self.senha,
                'ctl00$ScriptManager1': 'ctl00$UpdatePanel1|ctl00$ContentPlaceHolder1$btnLogar',
                '__VIEWSTATEENCRYPTED': '',
                '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
                '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
            }

            # Mandamos um pedido POST com os parâmetros para a página de login

            # Por alguma razão, os parâmetros só são enviados
            # corretamente em sistemas Windows se são passados
            # como "data" ao invés de "params"

            windows = 'Windows' in platform.system()
            pedido_post = self.sessao.post(url_login, data=parametros) if windows else self.sessao.post(
                url_login, params=parametros)

            # Se conseguimos autenticar com sucesso
            if pedido_post.status_code == 200 and 'novamente' not in pedido_post.text:

                # Se já fomos redirecionados para o portal automaticamente
                if 'Desconectar' in pedido_post.text:
                    return True
                else:
                    # Senão, sabemos que temos que selecionar o curso,
                    # então chamamos a página de cursos
                    url_cursos = Paginas.get_url(Pagina.cursos, True) + '?M=' + self.matricula
                    pedido_get = self.sessao.get(url_cursos)
                    soup = BeautifulSoup(pedido_get.content.decode('utf-8'), 'html5lib')

                    # Buscamos os cursos disponíveis na tabela
                    cursos = soup.find(id=lambda x: x and 'grdCursos' in x)
                    # Se existe algum curso na tabela
                    if cursos:
                        for curso in cursos.find_all('tr', {'class': lambda x: x and 'ItemGrid' in x}):
                            situacao = curso.find_all('td')[2].contents[0]

                            # Buscamos o curso que tem a situação "Frequente"
                            if situacao.startswith('Frequente'):
                                tag_link = curso.find('a')
                                link = tag_link['href'].split('(\'')[1].split('\',')[0]
                                # Mandamos o pedido para sermos redirecionados à página principal do curso selecionado
                                parametros = {
                                    '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                                    '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})[
                                        'value'],
                                    '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
                                    '__VIEWSTATEENCRYPTED': '',
                                    '__EVENTTARGET': link,
                                    'ctl00$ScriptManager1': 'ctl00$UpdatePanel1|' + link
                                }
                                pedido_post = self.sessao.post(url_cursos, data=parametros)
                                # Se tudo der certo esta função retorna True
                                return pedido_post.status_code == 200
        return False

    '''
    Retorna o coeficiente de desempenho acadêmico
    do aluno. O valor está compreendido entre 0 e 1,
    quanto maior o valor, melhor o desempenho.
    '''

    @staticmethod
    def desempenho(lst_disciplinas):
        total_ganho = 0
        total_distribuido = 1
        for disciplina in lst_disciplinas:
            total_ganho += disciplina.pontos_ganhos()
            total_distribuido += disciplina.pontos_distribuidos()
        return total_ganho / total_distribuido
