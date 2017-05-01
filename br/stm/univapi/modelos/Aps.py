import time
from datetime import datetime


class Aps(object):
    def __init__(self, data_lancamento, titulo, prazo_entrega, descricao):
        self.data_lancamento = data_lancamento
        self.titulo = titulo
        self.prazo_entrega = prazo_entrega
        self.descricao = descricao

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
    da APS em formato hh:mm:ss
    '''

    def tempo_restante(self):
        tempo_atual = datetime.now()
        segundos = (self.prazo() - tempo_atual).total_seconds()
        m, s = divmod(segundos, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)
