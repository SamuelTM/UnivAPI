import time
from datetime import datetime


class Aps:
    def __init__(self, data_lancamento, titulo, prazo_entrega, descricao, postado):
        self.data_lancamento = data_lancamento
        self.titulo = titulo
        self.prazo_entrega = prazo_entrega
        self.descricao = descricao
        self.postado = postado

    '''
    Retorna o prazo para entrega no formato de data
    do Python. Assim é mais fácil utilizá-lo para cálculos
    posteriores.
    '''

    def prazo(self):
        # Primeiro convertemos a string para uma estrutura de tempo reconhecível pelo Python
        time_struct = time.strptime(self.prazo_entrega, '%d/%m/%Y %H:%M:%S')
        # Então convertemos de estrutura para objeto
        return datetime.fromtimestamp(time.mktime(time_struct))

    '''
    Retorna o tempo restante para entrega
    da APS em dias, horas e minutos
    '''

    def tempo_restante(self):
        segundos = (self.prazo() - datetime.now()).total_seconds()
        if segundos > 0:
            m, s = divmod(segundos, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            return '{:g}d, {:02g}h, {:02g}m'.format(d, h, m)
        else:
            return '0'
