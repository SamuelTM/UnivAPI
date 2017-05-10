import time
from datetime import datetime


class Mensagem(object):
    def __init__(self, remetente, data, assunto, mensagem):
        self.remetente = remetente
        self.data = data
        self.assunto = assunto
        self.mensagem = mensagem

    '''
    Retorna a data de envio no formato de data do Python.
    Assim é mais fácil utilizá-la para cálculos posteriores.
    '''

    def data_envio(self):
        # Primeiro convertemos a string para uma estrutura de tempo reconhecível pelo Python
        time_struct = time.strptime(self.data, '%d/%m/%Y %H:%M:%S')
        # Então convertemos de estrutura para objeto
        return datetime.fromtimestamp(time.mktime(time_struct))
