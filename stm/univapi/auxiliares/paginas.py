from enum import Enum


class Pagina(Enum):
    login = 1,
    principal = 2,
    disciplina = 3,
    mensagens = 4,
    boletos = 5,
    horarios = 6,
    cursos = 7,
    boletim = 8


'''
Uma forma mais organizada de gerenciar as
URLs utilizadas pela API. Caso seja necessário
alterar alguma URL, basta alterar esta função.
'''


def get_url(pagina: Pagina, https: bool) -> str:
    url = 'https://siu.univale.br/SIU-PortalAluno/' if https else 'http://siu.univale.br/SIU-PortalAluno/'

    if pagina == Pagina.login:
        url = url + 'Login.aspx'
    elif pagina == Pagina.principal:
        url = url + 'Default.aspx'
    elif pagina == Pagina.disciplina:
        url = url + 'OpcoesDisciplinas.aspx'
    elif pagina == Pagina.mensagens:
        url = url + 'CaixaPostal/CaixaPostal.aspx'
    elif pagina == Pagina.boletos:
        url = url + 'Financeiro/Titulos.aspx'
    elif pagina == Pagina.horarios:
        url = url + 'HorarioAulas/Horario.aspx'
    elif pagina == Pagina.cursos:
        url = url + 'Curso.aspx'
    elif pagina == Pagina.boletim:
        url = url + 'Boletim/Boletim.aspx'
    return url
