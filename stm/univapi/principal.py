from flask import Flask, Response, request

from stm.univapi import Aluno

app = Flask(__name__)


@app.route('/')
def index():
    return 'Página principal'


@app.route('/perfil', methods=['POST'])
def perfil():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario and senha:
        aluno = Aluno(usuario, senha)
        if aluno.autenticar():
            return Response(aluno.perfil.to_json(), mimetype='application/json')
        else:
            return Response('Erro na autenticação', mimetype='text/html')
    else:
        return Response('Parâmetros inválidos', mimetype='text/html')


if __name__ == '__main__':
    app.run(debug=True)
