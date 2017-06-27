import json

from bs4 import BeautifulSoup


class DadosAluno(object):
    def __init__(self, aluno):
        self.aluno = aluno

    '''
     Retorna as informações básicas sobre o aluno
     '''

    def lista(self):
        dados = []
        pagina_principal = self.aluno.sessao.get('http://siu.univale.br/SIU-PortalAluno/Default.aspx')
        soup = BeautifulSoup(pagina_principal.content.decode('utf-8'), 'html5lib')
        # Nome do aluno
        dados.append(soup.find(id='ctl00_ContentPlaceHolder1_Aluno1_lbNomeAluno').contents[0].strip())
        # Curso do aluno
        dados.append(' '.join(soup.find(id='ctl00_ContentPlaceHolder1_Aluno1_lbInfoCurso').contents[0].split()))
        # Email do aluno
        dados.append(soup.find(id='ctl00_ContentPlaceHolder1_Aluno1_lbEmailAluno').contents[0].strip())
        return dados

    def to_json(self):
        dados = self.lista()
        return json.dumps(dict(nome=dados[0], email=dados[2], curso=dados[1]), ensure_ascii=False)
