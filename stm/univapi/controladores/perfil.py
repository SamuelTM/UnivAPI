import json

from bs4 import BeautifulSoup
from urllib3.exceptions import ProtocolError

from stm.univapi import Pagina
from stm.univapi import paginas


class Perfil(object):
    def __init__(self, aluno):
        self.aluno = aluno

    '''
     Retorna as informações básicas sobre o aluno
     '''

    def lista(self):
        dados = []
        try:
            pagina_principal = self.aluno.sessao.get(paginas.get_url(Pagina.principal, True))
            soup = BeautifulSoup(pagina_principal.content.decode('utf-8'), 'html5lib')

            # Nome do aluno
            dados.append(soup.find(id='ctl00_ContentPlaceHolder1_Aluno1_lbNomeAluno').contents[0].strip())
            # Curso do aluno
            dados.append(' '.join(soup.find(id='ctl00_ContentPlaceHolder1_Aluno1_lbInfoCurso').contents[0].split()))
            # Email do aluno
            dados.append(soup.find(id='ctl00_ContentPlaceHolder1_Aluno1_lbEmailAluno').contents[0].strip())
        except (AttributeError, IOError, ConnectionError, ProtocolError):
            dados.clear()
        return dados

    '''
    Retorna a URL do avatar do aluno. Lembrando
    que se o mesmo não possuir uma foto, a URL
    será inválida.
    '''

    def url_avatar(self):
        return 'https://siu.univale.br/_Fotos/alunos/' + str(self.aluno.matricula) + '.jpg'

    def to_json(self):
        dados = self.lista()
        return json.dumps(dict(nome=dados[0], email=dados[2], curso=dados[1]), ensure_ascii=False)
