# UnivAPI

API para o [Portal do Aluno](https://siu.univale.br/siu-portalaluno/login.aspx "Portal do Aluno - UNIVALE") da Universidade Vale do Rio Doce - UNIVALE

Criei este projeto no intuito de haver uma forma mais prática de se obter os dados de um aluno pelo Portal, uma vez que a universidade não possui API própria.

Com esta API, é possível autenticar-se e obter diversos tipos de informações sobre o aluno autenticado, tais como nome, e-mail, notas, entre outros.

Utiliza-se uma técnica conhecida como "web scraping", que consiste em extrair as informações desejadas de uma página através de seu código-fonte, filtrando as partes desnecessárias.

Este projeto está licensiado sob a Licença do MIT.

# Como utilizar
A API está hospedada e pronta para uso em https://univapi.herokuapp.com/

O site é dividido nas seguintes sessões:
* /perfil
* /mensagens
* /horarios
* /disciplinas
* /boletos
* /boletins

Para cada sessão é possível enviar um pedido POST com o usuário e senha desejados como parâmetros. O servidor irá então retornar uma resposta em JSON com os dados da sessão especificada.

## Exemplo em Python
```python 
pedido = requests.post('http://univapi.herokuapp.com/perfil', data={'usuario': '72193', 'senha': 'minhasenha'})
print(pedido.text)
```

Isso imprimiria:
`
{"nome": "Nome do Aluno", "email": "email@exemplo.com", "curso": "Curso do Aluno"}
`
