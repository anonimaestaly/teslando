from db import conectar


def criar_usuario(nome, email):
    conexao = conectar()
    if not conexao:
        return

    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO usuario (nome, email) VALUES (%s, %s)",
        (nome, email),
    )
    conexao.commit()
    print("Usuário criado, id:", cursor.lastrowid)

    cursor.close()
    conexao.close()


def listar_usuarios():
    conexao = conectar()
    if not conexao:
        return

    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuario ORDER BY id")
    usuarios = cursor.fetchall()

    if not usuarios:
        print("Ainda não tem nenhum usuário cadastrado.")

    for u in usuarios:
        print(f"#{u['id']} - {u['nome']} ({u['email']})")

    cursor.close()
    conexao.close()