import json
from threading import Thread

from bs4 import BeautifulSoup

from br.stm.univapi.Serializador import Serializador
from br.stm.univapi.modelos.Aps import Aps
from br.stm.univapi.modelos.Disciplina import Disciplina
from br.stm.univapi.modelos.Falta import Falta
from br.stm.univapi.modelos.Nota import Nota


class Disciplinas(object):
    def __init__(self, aluno):
        self.aluno = aluno

    '''
    Retorna um dict (chave/valor) com os nomes das disciplinas e os respectivos 
    links para elas. Caso params não seja nulo, ele será usado para guardar
    os parâmetros da página que acabamos de carregar neste método. Isso vai
    poupar tempo mais tarde.
    '''

    def __nomes(self, parametros):
        disciplinas = {}

        pedido_get = self.aluno.sessao.get('http://www.siu.univale.br/siu-portalaluno/Default.aspx')
        soup = BeautifulSoup(pedido_get.content.decode('utf-8'), 'html5lib')
        for d in soup.find(id=lambda x: x and '_grdDisciplinasEmCurso' in x).find_all(href=True):
            disciplinas[d.contents[0]] = d['href'].split('(\'')[1].split('\',')[0]

        if parametros is not None:
            parametros.update({
                '__VIEWSTATEENCRYPTED': '',
                '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
                '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value']
            })
        return disciplinas

    def __obter_aps(self, soup):
        links_aps = []
        for a in soup.find(id=lambda x: x and '_gdvAPS' in x).find_all('input'):
            links_aps.append(a['name'])

        # Pegamos as informações de cada APS individualmente, para isso,
        # precisamos visitar a página de cada APS individualmente, logo,
        # temos que obter um novo conjunto de parâmetros
        parametros_aps = {
            '__VIEWSTATEENCRYPTED': '',
            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value']
        }
        aps = []
        for link_pagina in links_aps:
            # Adicionamos o parâmetro necessário para abrir a página da APS
            parametros_aps[link_pagina] = 'Visualizar'

            pedido_post = self.aluno.sessao.post('http://www.siu.univale.br/SIU-PortalAluno/OpcoesDisciplinas.aspx',
                                                 data=parametros_aps)
            soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')
            tag_titulo = soup.find(id=lambda x: x and '_lblTituloAPS' in x)

            # Verificação para o caso da disciplina não possuir APS registrada
            if tag_titulo:
                titulo = tag_titulo.contents[0]
                lancamento = soup.find(id=lambda x: x and '_lblLancamentoAPS' in x).contents[0]
                prazo = soup.find(id=lambda x: x and '_lblDataRespostaAPS' in x).contents[0]
                descricao = ' '.join(
                    soup.find('div', attrs={'style': 'float: left; max-width: 90%;'}).contents[0].split())

                # Adicionamos a APS à lista

                aps.append(Aps(lancamento, titulo, prazo, descricao))
        return aps

    @staticmethod
    def __obter_notas(soup):
        notas = []
        for t in soup.find_all('table', border='0', cellpadding='2', cellspacing='0'):
            nota = t.find(id=lambda x: x and '_lbNota' in x)

            # Verificamos se lbNota existe. Isso serve para
            # diferenciar uma coluna de nota da coluna do total
            # das notas
            if nota:
                descricao = t.find(id=lambda x: x and '_lbTitulo' in x).contents[0]
                data = t.find(id=lambda x: x and '_lbData' in x).contents[0]
                valor = t.find(id=lambda x: x and '_lbValor' in x).contents[0].replace(',', '.')
                nota = nota.contents[0].replace(',', '.')

                notas.append(Nota(descricao, data, valor, nota))
        return notas

    @staticmethod
    def __obter_faltas(soup):
        faltas = []

        # Adicionamos as faltas de aulas
        tag_faltas = soup.find(id=lambda x: x and '_dlistPresenca' in x)
        if tag_faltas:
            for t in tag_faltas.find_all(
                    'td', style='width:10px;'):
                faltas_horarios = []
                for a in t.find_all(id=lambda x: x and '_pnlPresenca' in x):
                    faltas_horarios.append(0 if 'green' in a.find('img')['src'] else 1)
                dia = t.find(id=lambda x: x and '_lbDtAula' in x).contents[0]

                faltas.append(Falta('Aulas', dia, faltas_horarios))

        # Adicionamos as faltas de APS
        tag_faltas_aps = soup.find(id=lambda x: x and '_dlistPresencaAPS' in x)
        if tag_faltas_aps:
            for t in tag_faltas_aps.find_all(
                    'td', style='width:10px;'):
                faltas_horarios = []
                for a in t.find_all('img', id=lambda x: x and 'dlistHorariosAPS' in x):
                    faltas_horarios.append(0 if 'green' in a['src'] else 1)
                    dia = t.find(id=lambda x: x and 'lbDtAula' in x).contents[0]

                    faltas.append(Falta('APS', dia, faltas_horarios))
        return faltas

    '''
    Retorna um objeto Disciplina com o link especificado.
    Caso params_inicais seja fornecido, usaremos ele para
    carregar a página da disciplina, caso contrário, carregaremos
    os parâmetros necessários na hora.
    '''

    def __disciplina(self, link_pagina, parametros):
        # Adicionamos/alteramos o parâmetro responsável por redirecionar a página
        parametros['__EVENTTARGET'] = link_pagina

        # Enviamos o pedido
        pedido_post = self.aluno.sessao.post('http://www.siu.univale.br/siu-portalaluno/Default.aspx', data=parametros)
        soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

        # Obtemos as informações básicas da disciplina
        nome = soup.find(id=lambda x: x and '_lbDisciplina' in x).contents[0]
        professor = soup.find(id=lambda x: x and '_lbProfessores' in x).contents[0]
        situacao = soup.find(id=lambda x: x and '_lbSituacaoDisciplina' in x).contents[0].strip()

        # Obtemos as APS
        aps = self.__obter_aps(soup)

        # Obtemos as notas
        notas = self.__obter_notas(soup)

        # Obtemos as faltas
        faltas = self.__obter_faltas(soup)

        return Disciplina(nome, professor, situacao, notas, faltas, aps)

    '''
    Adiciona a disciplina com o link especificado à lista
    especificada. A diferença neste método é que a página
    do portal é acessada em uma nova sessão. Este método
    foi criado somente para podermos trabalhar com threads
    e portanto, não é recomendado seu uso externo.
    '''

    def __disciplina_thread(self, link_pagina, params_iniciais, lista_disciplinas, sessao_atual):
        if not sessao_atual:
            from br.stm.univapi.Aluno import Aluno
            aluno = Aluno(self.aluno.matricula, self.aluno.senha)
            if aluno.autenticar():
                lista_disciplinas.append(aluno.disciplinas.__disciplina(link_pagina, params_iniciais))
        else:
            lista_disciplinas.append(self.__disciplina(link_pagina, params_iniciais))

    '''
    Retorna uma lista de objetos Disciplina
    com as disciplinas do aluno
    '''

    def lista(self):
        disciplinas = []
        parametros = {}
        nomes = self.__nomes(parametros)

        # Separamos uma disciplina para ser retornada na sessão atual
        primeiro_nome = nomes.popitem()

        # Criamos uma thread para cada uma do resto das disciplinas
        threads = list(map(
            lambda nome: Thread(target=self.__disciplina_thread, args=(nomes[nome], parametros, disciplinas, False)),
            nomes))

        # Adicionamos a disciplina que separamos anteriormente à lista de threads
        threads.append(Thread(target=self.__disciplina_thread, args=(primeiro_nome[1], parametros, disciplinas, True)))

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        return disciplinas

    '''
    Retorna todas as disciplinas em formato JSON
    '''

    def to_json(self):
        return json.dumps([disciplina.__dict__ for disciplina in self.lista()], ensure_ascii=False, cls=Serializador)
