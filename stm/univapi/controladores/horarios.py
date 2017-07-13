import json

from bs4 import BeautifulSoup
from urllib3.exceptions import ProtocolError

from stm.univapi.auxiliares import paginas
from stm.univapi.auxiliares.controlador import Controlador
from stm.univapi.auxiliares.paginas import Pagina
from stm.univapi.modelos.horario import Horario


class Horarios(Controlador):
    def __init__(self, aluno):
        self.aluno = aluno

    '''
    Retorna uma lista de objetos Horario com
    os horários do aluno
    '''

    def lista(self):
        hrs = []
        try:
            pedido_get = self.aluno.sessao.get(paginas.get_url(Pagina.horarios, True))
            soup = BeautifulSoup(pedido_get.content.decode('utf-8'), 'html5lib')

            turnos = ['_grdMatutino', '_grdVespertino', '_grdNoturno']

            # Procuramos pelos horários de todos os turnos
            for turno in turnos:
                tabela_tag = soup.find(id=lambda x: x and turno in x)

                # Se o turno atual possui horários
                if tabela_tag:
                    nome_turno = turno[4:]
                    for tabela in tabela_tag.find_all('tr', {'class': lambda x: x and 'ItemGrid' in x}):
                        hora_inicio_tag = tabela.find(id=lambda x: x and 'lbHrIni' in x)

                        # Se a célula que estamos verificando é uma célula que mostra um horário
                        if hora_inicio_tag:
                            hora_termino = tabela.find(id=lambda x: x and 'lbHrTerm' in x).contents[0]
                            hora_inicio = hora_inicio_tag.contents[0]

                            # Pegamos cada célula da tabela
                            celulas = tabela.find_all('table', id=lambda x: x and '_grdProfs' in x)
                            for celula in celulas:

                                professor = ''
                                professor_tag = celula.find('a', style='text-decoration:none')

                                if professor_tag and professor_tag.contents:
                                    professor = professor_tag.contents[0]
                                else:
                                    alt_prof = celula.find(id=lambda x: x and 'lbProf' in x)
                                    if alt_prof and alt_prof.contents:
                                        professor = alt_prof.contents[0]

                                disciplina = celula.find(id=lambda x: x and '_lbDisciplina' in x).contents[0]
                                sala = celula.find(id=lambda x: x and '_lbSala' in x).contents[0]
                                dia = celula.get('id').split('grdProfs')[1]

                                # Adicionamos o horário à lista
                                hrs.append(
                                    Horario(hora_inicio, hora_termino, professor, disciplina, sala, dia, nome_turno))
        except (AttributeError, IOError, ConnectionError, ProtocolError):
            hrs.clear()
        return hrs

    '''
    Retorna todos os horários em formato JSON
    '''

    def to_json(self):
        return json.dumps([horario.__dict__ for horario in self.lista()], ensure_ascii=False)
