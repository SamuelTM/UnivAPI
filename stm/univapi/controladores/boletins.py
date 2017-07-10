import json

from bs4 import BeautifulSoup
from urllib3.exceptions import ProtocolError

from stm.univapi.auxiliares import paginas
from stm.univapi.auxiliares.controlador import Controlador
from stm.univapi.auxiliares.paginas import Pagina
from stm.univapi.auxiliares.serializador import Serializador
from stm.univapi.modelos.boletim import Boletim
from stm.univapi.modelos.nota_final import NotaFinal


class Boletins(Controlador):
    def __init__(self, aluno):
        self.aluno = aluno

    @staticmethod
    def __obter_notas(soup: BeautifulSoup) -> list:
        notas = []
        try:
            tabela = soup.find_all(class_=lambda x: x and 'ItemGrid' in x)
            for linha_tabela in tabela:
                info_disciplina = linha_tabela.find_all('span')

                disciplina = info_disciplina[0].text.strip()
                turma = info_disciplina[1].text.strip()
                ta = info_disciplina[2].text.strip()
                es = info_disciplina[3].text.strip()
                total = info_disciplina[4].text.strip()
                faltas_teoricas = info_disciplina[5].text.strip()
                faltas_praticas = info_disciplina[6].text.strip()
                situacao = info_disciplina[7].text.strip()

                notas.append(NotaFinal(disciplina, turma, ta, es, total, faltas_teoricas, faltas_praticas, situacao))
        except (AttributeError, IOError, ConnectionError, ProtocolError):
            notas.clear()
        return notas

    def lista(self):
        boletins = []
        url = paginas.get_url(Pagina.boletim, True)
        pagina_boletim = self.aluno.sessao.get(url)
        soup = BeautifulSoup(pagina_boletim.content.decode('utf-8'), 'html5lib')
        anos = [tag.text for tag in soup.find(id=lambda x: x and '_dlistAno' in x).find_all('option') if
                '>' not in tag.text]
        parametros = {
            '__VIEWSTATEENCRYPTED': '',
            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
            'ctl00$ContentPlaceHolder1$btnGerarBoletim': 'Ok'
        }

        for ano in anos:
            parametros['ctl00$ContentPlaceHolder1$dlistAno'] = ano
            for i in range(1, 3):
                parametros['ctl00$ContentPlaceHolder1$DlistSemestre'] = str(i)
                pedido_post = self.aluno.sessao.post(url, data=parametros)
                soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

                if 'notas nesse' not in str(soup):
                    boletins.append(Boletim(ano, str(i), self.__obter_notas(soup)))

        return boletins

    def to_json(self):
        return json.dumps([boletim.__dict__ for boletim in self.lista()], ensure_ascii=False, cls=Serializador)
