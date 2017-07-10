class Boleto(object):
    def __init__(self, ano_mes, vencimento, mensalidade, dependencia, desconto, liquido, situacao):
        self.ano_mes = ano_mes
        self.vencimento = vencimento
        self.mensalidade = mensalidade
        self.dependencia = dependencia
        self.desconto = desconto
        self.liquido = liquido
        self.situacao = situacao
