from datetime import datetime


class Disciplina(object):
    def __init__(self, nome, professor, situacao, notas, faltas, aps):
        self.nome = nome
        self.professor = professor
        self.situacao = situacao
        self.notas = notas
        self.faltas = faltas
        self.aps = aps

    '''
    Retorna o total de pontos ganhos na disciplina
    '''

    def pontos_ganhos(self):
        return sum(float(n.nota) for n in self.notas)

    '''
    Retorna o total de pontos distribuídos na disciplina
    '''

    def pontos_distribuidos(self):
        return sum(float(n.valor) for n in self.notas if float(n.nota) > 0)

    '''
    Retorna a porcentagem dos pontos ganhos
    '''

    def porcentagem_pontos(self):
        pontos_distribuidos = self.pontos_distribuidos()
        return self.pontos_ganhos() / pontos_distribuidos * 100 if pontos_distribuidos > 0 else 100

    '''
    Retorna uma lista com todas as APS pendentes
    a partir da data atual
    '''

    def aps_pendentes(self):
        tempo_atual = datetime.now()
        return [a for a in self.aps if tempo_atual < a.prazo()]

    '''
    Retorna a pontuação da disciplina para
    o coeficiente de desempenho acadêmico
    '''

    def pontuacao(self, distribuicao):
        return self.porcentagem_pontos() * distribuicao / 100
