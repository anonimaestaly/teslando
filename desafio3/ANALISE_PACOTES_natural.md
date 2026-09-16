## Desafio 03.1

Escolhi o requests e o pandas porque foram os pacotes que eu já tinha usado no Desafio 03. Fiquei com eles porque ia ser mais fácil entender e explicar algo que eu já tinha mexido, do que pegar uma biblioteca nova do zero.

## requests

O requests é o pacote que uso pra falar com a API. Ele serve pra fazer as requisições HTTP, tipo GET, POST, PUT, DELETE. No meu caso eu só uso o GET mesmo, que é pra buscar informação.

Um exemplo bem simples de como ele funciona:

```python
resposta = requests.get("https://api.exemplo.com/dados")
print(resposta.status_code)
print(resposta.json())
```

No script, ele é usado pra pegar a lista de usuários da API reqres.in. Só que essa API divide os usuários em várias páginas, então o código fica repetindo a busca até não ter mais página pra pegar.

Uma coisa que usei foi a Session:

```python
with requests.Session() as conexao:
```

Ela serve pra não precisar ficar mandando a chave da API de novo a cada requisição. Configuro ela uma vez só no começo e continua valendo pras próximas buscas.

Da resposta que volta da API, eu uso principalmente duas coisas: o status_code, que mostra se deu certo, e o .json(), que transforma o que veio da API em algo que dá pra usar no Python (tipo uma lista ou um dicionário).

Fui dar uma olhada rápida no repositório do requests só pra entender melhor. Tem um arquivo chamado sessions.py que é onde fica a Session, um api.py com as funções tipo get e post, e um models.py que cuida da parte de request e response. Não mexi em nada disso, só fui olhar pra entender melhor o que a biblioteca faz por trás.

## pandas

O pandas eu uso depois que já tenho os dados da API, pra organizar tudo em formato de tabela. Primeiro eu transformo a lista de usuários numa tabela assim:

```python
tabela = pd.DataFrame(usuarios)
```

Depois pego a coluna do email, separo pelo @ pra ficar só com o domínio, e conto quantos usuários tem em cada domínio:

```python
dominios = tabela["email"].str.split("@").str[1]
return dominios.value_counts()
```

Pra ficar mais claro, se os emails fossem esses aqui:

```text
maria@gmail.com
joao@gmail.com
ana@hotmail.com
```

o resultado ia ser:

```text
gmail.com       2
hotmail.com     1
```

O .str é o que deixa eu mexer no texto de uma coluna (foi ele que usei pra separar o email pelo @), e o value_counts() já conta tudo pra mim, então não precisei ficar fazendo um for com contador manual, que ia dar bem mais trabalho.

Olhando por cima o repositório do pandas, os arquivos que mais tem a ver com o que usei são o frame.py, que é onde fica o DataFrame, e o algorithms.py, que deve ser onde fica implementado o value_counts e outras funções parecidas.
