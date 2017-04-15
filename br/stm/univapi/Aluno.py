import requests
from bs4 import BeautifulSoup

from br.stm.univapi.modelos.Aps import Aps
from br.stm.univapi.modelos.Boleto import Boleto
from br.stm.univapi.modelos.Disciplina import Disciplina
from br.stm.univapi.modelos.Falta import Falta
from br.stm.univapi.modelos.Mensagem import Mensagem
from br.stm.univapi.modelos.Nota import Nota


class Aluno(object):
    def __init__(self, matricula, senha):
        self.matricula = matricula
        self.senha = senha
        self.sessao = requests.Session()
        # Alteramos os cabeçalhos dos nossos pedidos para não sermos confundidos com robôs
        self.sessao.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3'
        })

    def autenticar(self):
        url_login = 'http://www.siu.univale.br/SIU-PortalAluno/Login.aspx'
        pedido_get = self.sessao.get(url_login)

        if pedido_get.status_code == 200:
            # Pegamos os parâmetros necessários para autenticar
            soup = BeautifulSoup(pedido_get.content.decode('utf-8'), 'html5lib')
            parametros = {
                'ctl00$ContentPlaceHolder1$btnLogar': 'OK',
                'ctl00$ContentPlaceHolder1$txtMatricula': self.matricula,
                'ctl00$ContentPlaceHolder1$txtSenha': self.senha,
                'ctl00$ScriptManager1': 'ctl00$UpdatePanel1|ctl00$ContentPlaceHolder1$btnLogar',
                '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
                '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
            }
            # Mandamos um pedido POST com os parâmetros para a página de login
            pedido_post = self.sessao.post(url_login, data=parametros)

            # Se conseguimos autenticar com sucesso
            if pedido_post.status_code == 200 and 'novamente' not in pedido_post.text:
                # Chamamos a página que exibe os cursos do aluno
                url_cursos = 'http://www.siu.univale.br/SIU-PortalAluno/Curso.aspx?M=' + self.matricula
                pedido_get = self.sessao.get(url_cursos)
                soup = BeautifulSoup(pedido_get.content.decode('utf-8'), 'html5lib')
                # Percorremos cada curso exibido na tabela
                for curso in soup.find(id=lambda x: x and 'grdCursos' in x).find_all(
                        'tr', {'class': lambda x: x and 'ItemGrid' in x}):
                    situacao = curso.find_all('td')[2].contents[0]

                    # Buscamos o curso que tem a situação "Frequente"
                    if situacao.startswith('Frequente'):
                        tag_link = curso.find('a')
                        link = tag_link['href'].split('(\'')[1].split('\',')[0]
                        # Mandamos o pedido para sermos redirecionados à página principal do curso selecionado
                        parametros = {
                            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
                            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
                            '__VIEWSTATEENCRYPTED': '',
                            '__EVENTTARGET': link,
                            'ctl00$ScriptManager1': 'ctl00$UpdatePanel1|' + link
                        }
                        pedido_post = self.sessao.post(url_cursos, data=parametros)
                        # Se tudo der certo esta função retorna True
                        return pedido_post.status_code == 200

    def nome(self):
        pagina_principal = self.sessao.get('http://www.siu.univale.br/siu-portalaluno/Default.aspx')
        soup = BeautifulSoup(pagina_principal.content.decode('utf-8'), 'html5lib')
        return soup.find(id='ctl00_ContentPlaceHolder1_Aluno1_lbNomeAluno').contents[0].strip()

    def curso(self):
        pagina_principal = self.sessao.get('http://www.siu.univale.br/siu-portalaluno/Default.aspx')
        soup = BeautifulSoup(pagina_principal.content.decode('utf-8'), 'html5lib')
        # Por alguma razão a string do curso vem com espaços demais, então conserto isso assim
        return ' '.join(soup.find(id='ctl00_ContentPlaceHolder1_Aluno1_lbInfoCurso').contents[0].split())

    def email(self):
        pagina_principal = self.sessao.get('http://www.siu.univale.br/siu-portalaluno/Default.aspx')
        soup = BeautifulSoup(pagina_principal.content.decode('utf-8'), 'html5lib')
        return soup.find(id='ctl00_ContentPlaceHolder1_Aluno1_lbEmailAluno').contents[0].strip()

    def url_avatar(self):
        return 'http://www.siu.univale.br/_Fotos/alunos/' + str(self.matricula) + '.jpg'

    def disciplinas(self):
        disciplinas = []
        url_principal = 'http://www.siu.univale.br/siu-portalaluno/Default.aspx'

        # Pegamos os links para as páginas de todas as matérias
        pedido_post = self.sessao.get(url_principal)
        soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')
        links_disciplinas = []
        for a in soup.find(id=lambda x: x and '_grdDisciplinasEmCurso' in x).find_all(href=True):
            links_disciplinas.append(a['href'].split('(\'')[1].split('\',')[0])

        # Acessamos cada página individualmente para coletarmos as informações
        parametros = {
            '__VIEWSTATEENCRYPTED': '',
            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value']
        }
        for link_disciplina in links_disciplinas:
            parametros['__EVENTTARGET'] = link_disciplina
            pedido_post = self.sessao.post(url_principal, data=parametros)
            soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

            nome = soup.find(id=lambda x: x and '_lbDisciplina' in x).contents[0]
            professor = soup.find(id=lambda x: x and '_lbProfessores' in x).contents[0]
            situacao = soup.find(id=lambda x: x and '_lbSituacaoDisciplina' in x).contents[0]

            # Pegamos os links de todas as APS
            links_aps = []
            for a in soup.find(id=lambda x: x and '_gdvAPS' in x).find_all('input'):
                links_aps.append(a['name'])

            # Pegamos as informações de cada APS individualmente
            parametros_aps = {
                '__VIEWSTATEENCRYPTED': '',
                '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
                '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
                '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value']
            }
            aps = []
            for link in links_aps:
                # Adicionamos o parâmetro necessário para abrir a página da APS
                parametros_aps[link] = 'Visualizar'

                pedido_post = self.sessao.post('http://www.siu.univale.br/SIU-PortalAluno/OpcoesDisciplinas.aspx',
                                               data=parametros_aps)
                soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')
                titulo = soup.find(id=lambda x: x and '_lblTituloAPS' in x).contents[0]
                lancamento = soup.find(id=lambda x: x and '_lblLancamentoAPS' in x).contents[0]
                prazo = soup.find(id=lambda x: x and '_lblDataRespostaAPS' in x).contents[0]
                descricao = ' '.join(
                    soup.find('div', attrs={'style': 'float: left; max-width: 90%;'}).contents[0].split())
                # Adicionamos a APS à lista
                aps.append(Aps(lancamento, titulo, prazo, descricao))

            # Adicionamos as notas
            notas = []
            for t in soup.find_all('table', border='0', cellpadding='2', cellspacing='0'):
                nota = t.find(id=lambda x: x and '_lbNota' in x)
                if nota:
                    descricao = t.find(id=lambda x: x and '_lbTitulo' in x).contents[0]
                    data = t.find(id=lambda x: x and '_lbData' in x).contents[0]
                    valor = t.find(id=lambda x: x and '_lbValor' in x).contents[0].replace(',', '.')
                    nota = nota.contents[0].replace(',', '.')
                    notas.append(Nota(descricao, data, float(valor), float(nota)))

            # Adicionamos as faltas de aulas
            faltas = []
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

            # Juntamos tudo em um único objeto e adicionamos à lista de disciplinas
            disciplinas.append(Disciplina(nome, professor, situacao, notas, faltas, aps))
        return disciplinas

    def boletos(self):
        url = 'http://www.siu.univale.br/SIU-PortalAluno/Financeiro/Titulos.aspx'
        pagina_boleto = self.sessao.get(url)
        soup = BeautifulSoup(pagina_boleto.content.decode('utf-8'), 'html5lib')
        boletos = []
        numero_paginas = len(soup.find('tr', {'class': 'BarrDataControls'}).find('td').find_all('td'))

        # Como já estamos na primeira página, é mais eficiente pegar as informações dela separada das outras
        for linha in soup.find(id='ctl00_ContentPlaceHolder1_GridView1').find_all(
                'tr', {'class': lambda x: x and 'ItemGrid' in x}):
            tags = linha.find_all('td')

            ano_mes = tags[0].contents[0]
            vencimento = tags[1].contents[0]
            mensalidade = tags[2].contents[0]
            dependencia = tags[3].contents[0]
            desconto = tags[4].contents[0]
            liquido = tags[5].contents[0]
            situacao = ' '.join(tags[6].contents[0].split())

            boletos.append(Boleto(ano_mes, vencimento, mensalidade, dependencia, desconto, liquido, situacao))

        # Agora sim pegamos as informações do resto das páginas
        parametros = {
            '__VIEWSTATEENCRYPTED': '',
            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$GridView1',
        }

        # Percorremos cada página
        for i in range(2, numero_paginas + 1):
            parametros['__EVENTARGUMENT'] = 'Page$' + str(i)
            pagina_boleto = self.sessao.post(url, data=parametros)
            soup = BeautifulSoup(pagina_boleto.content.decode('utf-8'), 'html5lib')

            # Coletamos as informações de cada boleto na tabela
            for linha in soup.find(id='ctl00_ContentPlaceHolder1_GridView1').find_all(
                    'tr', {'class': lambda x: x and 'ItemGrid' in x}):
                tags = linha.find_all('td')

                ano_mes = tags[0].contents[0]
                vencimento = tags[1].contents[0]
                mensalidade = tags[2].contents[0]
                dependencia = tags[3].contents[0]
                desconto = tags[4].contents[0]
                liquido = tags[5].contents[0]
                situacao = ' '.join(tags[6].contents[0].split())

                # Adicionamos os dados em um único objeto e então o adicionamos à lista
                boletos.append(Boleto(ano_mes, vencimento, mensalidade, dependencia, desconto, liquido, situacao))
        return boletos

    def mensagens(self):
        mensagens = []
        url = 'http://www.siu.univale.br/SIU-PortalAluno/CaixaPostal/CaixaPostal.aspx'
        pedido_get = self.sessao.get(url)
        soup = BeautifulSoup(pedido_get.content.decode('utf-8'), 'html5lib')
        parametros = {
            '__VIEWSTATEENCRYPTED': '',
            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value'],
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$lkbLidas'
        }
        pedido_post = self.sessao.post(url, data=parametros)
        soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

        parametros.update({
            '__VIEWSTATE': soup.find('input', {'name': '__VIEWSTATE'})['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value'],
            '__EVENTVALIDATION': soup.find('input', {'name': '__EVENTVALIDATION'})['value']
        })
        for a in soup.find(id=lambda x: x and '_gvMensagem' in x).find_all('tr',
                                                                           {'class': lambda x: x and 'ItemGrid' in x}):
            remetente = a.find('a', id=lambda x: x and '_lkbDe' in x).contents[0]
            data = a.find('a', id=lambda x: x and '_lkbData' in x).contents[0]

            tag_assunto = a.find('a', id=lambda x: x and '_lkbAssunto' in x)
            assunto = ' '.join(tag_assunto.contents[0].split())

            link_mensagem = tag_assunto['href'].split('(\'')[1].split('\',')[0]
            parametros['__EVENTTARGET'] = link_mensagem
            pedido_post = self.sessao.post(url, data=parametros)
            soup = BeautifulSoup(pedido_post.content.decode('utf-8'), 'html5lib')

            mensagem = soup.find('div', id='Corpo').contents[4]
            mensagens.append(Mensagem(str(remetente), str(data), str(assunto), str(mensagem)))

        return mensagens
