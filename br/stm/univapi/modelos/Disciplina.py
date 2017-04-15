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
        return sum(n.nota for n in self.notas)

    '''
    Retorna o total de pontos distribuídos na disciplina
    '''
    def pontos_distribuidos(self):
        return sum(n.valor for n in self.notas)


