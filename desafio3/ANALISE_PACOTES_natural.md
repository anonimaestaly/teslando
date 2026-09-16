Desafio 03.1 — Análise dos Pacotes Requests e Pandas

Introdução
Neste desafio, escolhi analisar os pacotes requests e pandas, porque foram os dois que eu já tinha usado no Desafio 03. Preferi trabalhar com algo que eu já conhecia um pouco, porque assim ficou mais fácil entender o funcionamento e também explicar o que estava acontecendo no código.
O requests foi usado na parte de comunicação com a API, enquanto o pandas foi usado depois, para organizar e analisar os dados que foram recebidos.

Requests
O requests é uma biblioteca do Python usada para fazer requisições HTTP. Basicamente, ela permite que o programa se comunique com sites e APIs para enviar ou receber informações.
Existem vários tipos de requisições, como:
GET — usado para buscar informações;
POST — usado para enviar informações;
PUT — usado para atualizar informações;
DELETE — usado para excluir informações.
No meu projeto, usei principalmente o GET, porque precisava buscar os usuários disponíveis na API.
Um exemplo simples seria:
resposta = requests.get("https://api.exemplo.com/dados")

print(resposta.status_code)
print(resposta.json())
Nesse exemplo, o requests.get() faz a requisição para o endereço da API.
Depois, o status_code mostra o resultado da requisição. Por exemplo, o código 200 normalmente significa que a requisição deu certo.
Já o .json() pega os dados que vieram da API em formato JSON e transforma esses dados em estruturas que o Python consegue trabalhar, como listas e dicionários.
Como usei o requests no meu projeto
No meu script, o requests é usado para consultar a API do reqres.in e pegar a lista de usuários.
A API divide os usuários em páginas. Por isso, o programa precisa fazer mais de uma requisição quando existem outras páginas disponíveis.
A lógica fica mais ou menos assim:
Fazer uma requisição para a API;
Pegar os usuários daquela página;
Adicionar esses usuários à lista;
Verificar se existe outra página;
Repetir o processo até não existir mais nenhuma página.
Dessa forma, o programa consegue juntar os usuários de todas as páginas em uma única lista.

Session
Uma parte do requests que achei interessante foi o Session.
No meu código, uso:
with requests.Session() as conexao:
A Session permite manter algumas configurações entre várias requisições.
No meu caso, ela é útil porque configurei a chave da API uma vez e posso continuar usando essa configuração nas próximas requisições, em vez de ficar repetindo a mesma informação toda hora.
Então, em vez de pensar em cada requisição como algo totalmente separado, a Session funciona como uma conexão que mantém algumas configurações enquanto estou fazendo as consultas.
Isso deixa o código mais organizado e evita repetição.

O que acontece com a resposta da API
Depois que o requests faz a requisição, eu preciso verificar o que a API respondeu.
As duas partes que mais uso são:
resposta.status_code
e:
resposta.json()
O status_code serve para verificar se a requisição funcionou.
Já o .json() serve para acessar os dados retornados pela API.
Por exemplo, a resposta pode trazer informações como nome, email e outros dados dos usuários.
Então, resumindo essa parte:
requests → faz a comunicação com a API → recebe os dados → entrega esses dados para o Python trabalhar.

Conhecendo o código do Requests
Também fui dar uma olhada rápida no repositório do requests para entender melhor como a biblioteca é organizada por dentro.
Não alterei esses arquivos. A ideia foi apenas olhar para entender melhor o funcionamento da biblioteca.
Alguns arquivos que chamaram minha atenção foram:
sessions.py — relacionado ao funcionamento das Sessions;
api.py — possui funções usadas para fazer requisições, como GET e POST;
models.py — trabalha com partes relacionadas às requisições e respostas.
Isso me ajudou a perceber que uma biblioteca que parece simples quando usamos no nosso código possui várias partes funcionando por trás.
Eu não precisei entender todo o código interno da biblioteca para usar o requests, mas olhar sua estrutura ajudou a entender de onde algumas funcionalidades vêm.

Pandas
O pandas é uma biblioteca do Python muito usada para trabalhar com dados.
No meu projeto, eu uso o pandas depois que os dados dos usuários já foram buscados pela API.
A ideia é pegar os dados que estão em uma lista e organizar em formato de tabela.
Para isso, uso:
tabela = pd.DataFrame(usuarios)
O DataFrame é uma das principais estruturas do pandas.
Ele funciona de uma forma parecida com uma tabela, com linhas e colunas.
Por exemplo, se eu tiver alguns usuários:
Nome       Email
Maria      maria@gmail.com
João       joao@gmail.com
Ana        ana@hotmail.com
O pandas consegue organizar essas informações em colunas, o que facilita bastante para fazer consultas e análises.

Analisando os emails
Depois de organizar os usuários em uma tabela, uso o pandas para analisar os emails.
No meu código, faço:
dominios = tabela["email"].str.split("@").str[1]

return dominios.value_counts()
Primeiro:
tabela["email"]
significa que estou pegando somente a coluna de emails da tabela.
Depois uso:
.str.split("@")
para separar cada email no símbolo @.
Por exemplo:
maria@gmail.com
fica separado em:
maria
gmail.com
O .str[1] pega a segunda parte, que nesse caso é:
gmail.com
Então consigo ficar somente com os domínios dos emails.

Contando os domínios
Depois disso, uso:
value_counts()
Essa função conta quantas vezes cada valor aparece.
Por exemplo, se eu tiver:
maria@gmail.com
joao@gmail.com
ana@hotmail.com
Depois de separar os domínios, vou ter:
gmail.com
gmail.com
hotmail.com
E o value_counts() consegue contar automaticamente:
gmail.com       2
hotmail.com     1
Isso facilita bastante porque eu não precisei criar um for e fazer um contador manualmente.
Eu poderia fazer essa contagem de outra forma usando estruturas básicas do Python, mas o pandas já possui uma função pronta para esse tipo de análise.

O que significa o .str
Uma coisa que aprendi usando o pandas foi o .str.
Ele permite fazer operações com textos que estão dentro de uma coluna.
No meu caso, usei:
.str.split("@")
para separar os emails.
Então, de forma simples:
.str → permite trabalhar com textos de uma coluna.
E:
.split("@") → separa o texto usando o @ como referência.

Conhecendo o código do Pandas
Também olhei por cima o repositório do pandas para entender como algumas dessas funcionalidades são organizadas internamente.
Um arquivo que tem relação com o que usei é o frame.py, que está relacionado ao funcionamento do DataFrame.
Também encontrei o algorithms.py, que possui implementações relacionadas a operações de análise e contagem de dados.
Assim como no requests, não precisei modificar esses arquivos nem entender todo o código interno.
O objetivo foi conhecer um pouco melhor o que existe por trás das funções que normalmente usamos de forma simples no nosso próprio código.

Como os dois pacotes trabalham juntos
No meu projeto, o requests e o pandas têm funções diferentes, mas trabalham em sequência.
Primeiro uso o requests para buscar os dados:
API
 ↓
requests
 ↓
dados dos usuários
Depois uso o pandas para organizar e analisar esses dados:
dados dos usuários
 ↓
pandas
 ↓
tabela
 ↓
análise dos emails
 ↓
contagem dos domínios
Então posso resumir o funcionamento do projeto dessa forma:
Requests busca os dados.
Pandas organiza e analisa os dados.
Foi justamente por já ter usado essas duas bibliotecas no Desafio 03 que escolhi elas para essa análise. Assim consegui estudar não só como usar as funções, mas também entender um pouco melhor o que as bibliotecas fazem por trás do código.

Conclusão
Com esse desafio, consegui entender melhor duas bibliotecas que já estavam presentes no meu projeto.
O requests ficou responsável pela comunicação com a API e pela busca dos usuários. Aprendi também um pouco mais sobre requisições HTTP, status_code, .json() e Session.
Já o pandas foi usado para organizar os dados em um DataFrame e fazer uma análise simples dos emails. Com ele, consegui separar os domínios e contar quantas vezes cada um aparecia usando value_counts().
Além de usar as bibliotecas, também achei interessante olhar um pouco seus repositórios. Isso mostrou que funções que parecem simples quando usamos no nosso código fazem parte de uma estrutura bem maior.
No final, o principal aprendizado foi entender melhor o que cada pacote faz, por que ele foi usado no projeto e como as duas partes se encaixam no funcionamento do programa.


