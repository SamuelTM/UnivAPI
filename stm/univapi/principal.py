from flask import Flask, Response, request

from stm.univapi.aluno import Aluno

app = Flask(__name__)


@app.route('/')
def index():
    return 'UnivAPI - API para o Portal do Aluno da Universidade Vale do Rio Doce - UNIVALE'


@app.route('/perfil', methods=['POST'])
def perfil():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario and senha:
        aluno = Aluno(usuario, senha)
        if aluno.autenticar():
            return Response(aluno.perfil.to_json(), mimetype='application/json')
        else:
            return Response('Authentication error', mimetype='text/html')
    else:
        return Response('Invalid parameters', mimetype='text/html')


@app.route('/mensagens', methods=['POST'])
def mensagens():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario and senha:
        aluno = Aluno(usuario, senha)
        if aluno.autenticar():
            return Response(aluno.mensagens.to_json(), mimetype='application/json')
        else:
            return Response('Authentication error', mimetype='text/html')
    else:
        return Response('Invalid parameters', mimetype='text/html')


@app.route('/horarios', methods=['POST'])
def horarios():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario and senha:
        aluno = Aluno(usuario, senha)
        if aluno.autenticar():
            return Response(aluno.horarios.to_json(), mimetype='application/json')
        else:
            return Response('Authentication error', mimetype='text/html')
    else:
        return Response('Invalid parameters', mimetype='text/html')


@app.route('/disciplinas', methods=['POST'])
def disciplinas():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario and senha:
        aluno = Aluno(usuario, senha)
        if aluno.autenticar():
            return Response(aluno.disciplinas.to_json(), mimetype='application/json')
        else:
            return Response('Authentication error', mimetype='text/html')
    else:
        return Response('Invalid parameters', mimetype='text/html')


@app.route('/boletos', methods=['POST'])
def boletos():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario and senha:
        aluno = Aluno(usuario, senha)
        if aluno.autenticar():
            return Response(aluno.boletos.to_json(), mimetype='application/json')
        else:
            return Response('Authentication error', mimetype='text/html')
    else:
        return Response('Invalid parameters', mimetype='text/html')


@app.route('/boletins', methods=['POST'])
def boletins():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario and senha:
        aluno = Aluno(usuario, senha)
        if aluno.autenticar():
            return Response(aluno.boletins.to_json(), mimetype='application/json')
        else:
            return Response('Authentication error', mimetype='text/html')
    else:
        return Response('Invalid parameters', mimetype='text/html')


if __name__ == '__main__':
    app.run()
