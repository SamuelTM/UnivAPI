import requests
from bs4 import BeautifulSoup

from stm.univapi.auxiliares import paginas
from stm.univapi.auxiliares.paginas import Pagina
from stm.univapi.controladores.boletins import Boletins
from stm.univapi.controladores.boletos import Boletos
from stm.univapi.controladores.disciplinas import Disciplinas
from stm.univapi.controladores.horarios import Horarios
from stm.univapi.controladores.mensagens import Mensagens
from stm.univapi.controladores.perfil import Perfil


class Aluno:
    def __init__(self, matricula, senha):
        self.matricula = matricula
        self.senha = senha
        self.sessao = requests.Session()

        # Alteramos os cabeçalhos dos nossos pedidos para não sermos confundidos com robôs
        self.sessao.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3'
        })

        self.disciplinas = Disciplinas(self)
        self.boletos = Boletos(self)
        self.mensagens = Mensagens(self)
        self.horarios = Horarios(self)
        self.perfil = Perfil(self)
        self.boletins = Boletins(self)

    '''
    Inicia uma sessão no portal. Sem este
    método, os outros não funcionam.
    '''

    def autenticar(self):
        url_login = paginas.get_url(Pagina.login, False)

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
            pedido_post = self.sessao.post(url_login, params=parametros)

            # Se conseguimos autenticar com sucesso
            if pedido_post.status_code == 200 and 'novamente' not in pedido_post.text:

                # Se já fomos redirecionados para o portal automaticamente
                if 'Desconectar' in pedido_post.text:
                    return True
                else:
                    # Senão, sabemos que temos que selecionar o curso primeiro
                    soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')
                    url_cursos = paginas.get_url(Pagina.cursos, True) + '?M=' + self.matricula

                    # Buscamos os cursos disponíveis na tabela
                    cursos = soup.find(id=lambda x: x and 'grdCursos' in x)

                    # Se existe algum curso na tabela
                    if cursos:

                        # Procuramos por algum curso, dando preferência ao
                        # curso que for frequente. Caso não haja um curso frequente,
                        # procuramos por um indefinido, se este também não existir,
                        # escolhemos qualquer um

                        curso_atual = ['', '']

                        for curso in cursos.find_all('tr', {'class': lambda x: x and 'ItemGrid' in x}):
                            situacao = curso.find_all('td')[2].contents[0]
                            link_curso = curso.find('a')['href'].split('(\'')[1].split('\',')[0]

                            if curso_atual[0] == 'Frequente':
                                break
                            elif curso_atual[0] != 'Indefinido' or situacao == 'Frequente':
                                curso_atual[0] = situacao
                                curso_atual[1] = link_curso

                        # Mandamos o pedido para sermos redirecionados à página principal do curso selecionado
                        parametros = {
                            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})[
                                'value'],
                            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
                            '__VIEWSTATEENCRYPTED': '',
                            '__EVENTTARGET': curso_atual[1],
                            'ctl00$ScriptManager1': 'ctl00$UpdatePanel1|' + curso_atual[1]
                        }
                        pedido_post = self.sessao.post(url_cursos, data=parametros)

                        # Se tudo der certo esta função retorna True
                        return 'Desconectar' in pedido_post.text
        return False
