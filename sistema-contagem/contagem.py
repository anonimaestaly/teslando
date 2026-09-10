
import tkinter as tk
from tkinter import messagebox
import winsound


FUNDO = "#080914"
PAINEL = "#111329"
ROXO = "#746cff"
BRANCO = "#ffffff"
VERDE = "#65ff7a"


def iniciar():
    try:
        inicio = int(campo_inicio.get())
        fim = int(campo_fim.get())
        passo = int(campo_passo.get())
    except ValueError:
        messagebox.showerror("Erro", "Digite somente números.")
        return

    if passo <= 0:
        messagebox.showerror("Erro", "O incremento deve ser maior que zero.")
        return

    if inicio > fim:
        messagebox.showerror("Erro", "O início não pode ser maior que o final.")
        return

    caixa_resultado.delete("1.0", tk.END)

    caixa_resultado.insert(
        tk.END,
        ">>> CONTAGEM INICIADA <<<\n\n"
    )

    status.config(text="STATUS: CONTANDO...")

    numero = inicio

    while numero <= fim:
        caixa_resultado.insert(
            tk.END,
            str(numero) + "\n"
        )

        numero_atual.config(text=str(numero))

        janela.update()

        winsound.MessageBeep(
            winsound.MB_ICONASTERISK
        )

        janela.after(120)

        numero = numero + passo

    caixa_resultado.insert(
        tk.END,
        "\n>>> MISSÃO CONCLUÍDA <<<"
    )

    status.config(text="STATUS: CONCLUÍDO")

    winsound.MessageBeep(
        winsound.MB_ICONASTERISK
    )


def limpar():
    campo_inicio.delete(0, tk.END)
    campo_fim.delete(0, tk.END)
    campo_passo.delete(0, tk.END)

    caixa_resultado.delete("1.0", tk.END)

    numero_atual.config(text="0")
    status.config(text="STATUS: PRONTO")


janela = tk.Tk()
janela.title("Sistema de Contagem")
janela.geometry("1000x650")
janela.configure(bg=FUNDO)


titulo = tk.Label(
    janela,
    text="SISTEMA DE CONTAGEM",
    font=("Arial", 28, "bold"),
    fg=BRANCO,
    bg=FUNDO
)

titulo.pack(pady=30)


area = tk.Frame(
    janela,
    bg=FUNDO
)

area.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=10
)


painel = tk.Frame(
    area,
    bg=PAINEL,
    padx=25,
    pady=20
)

painel.pack(
    side="left",
    fill="y",
    padx=(0, 15)
)


tk.Label(
    painel,
    text="NÚMERO INICIAL",
    font=("Arial", 12, "bold"),
    fg=BRANCO,
    bg=PAINEL
).pack(
    anchor="w",
    pady=(10, 5)
)


campo_inicio = tk.Entry(
    painel,
    font=("Arial", 18),
    justify="center",
    bg=FUNDO,
    fg=BRANCO,
    insertbackground=BRANCO
)

campo_inicio.pack(
    pady=(0, 15),
    ipady=8
)

campo_inicio.insert(0, "1")


tk.Label(
    painel,
    text="NÚMERO FINAL",
    font=("Arial", 12, "bold"),
    fg=BRANCO,
    bg=PAINEL
).pack(
    anchor="w",
    pady=(10, 5)
)


campo_fim = tk.Entry(
    painel,
    font=("Arial", 18),
    justify="center",
    bg=FUNDO,
    fg=BRANCO,
    insertbackground=BRANCO
)

campo_fim.pack(
    pady=(0, 15),
    ipady=8
)

campo_fim.insert(0, "20")


tk.Label(
    painel,
    text="INCREMENTO",
    font=("Arial", 12, "bold"),
    fg=BRANCO,
    bg=PAINEL
).pack(
    anchor="w",
    pady=(10, 5)
)


campo_passo = tk.Entry(
    painel,
    font=("Arial", 18),
    justify="center",
    bg=FUNDO,
    fg=BRANCO,
    insertbackground=BRANCO
)

campo_passo.pack(
    pady=(0, 15),
    ipady=8
)

campo_passo.insert(0, "2")


tk.Button(
    painel,
    text="INICIAR CONTAGEM",
    command=iniciar,
    font=("Arial", 12, "bold"),
    bg=ROXO,
    fg=BRANCO,
    relief="flat",
    cursor="hand2"
).pack(
    fill="x",
    pady=8,
    ipady=10
)


tk.Button(
    painel,
    text="LIMPAR DADOS",
    command=limpar,
    font=("Arial", 12, "bold"),
    bg=ROXO,
    fg=BRANCO,
    relief="flat",
    cursor="hand2"
).pack(
    fill="x",
    pady=8,
    ipady=10
)


resultado = tk.Frame(
    area,
    bg=PAINEL,
    padx=20,
    pady=20
)

resultado.pack(
    side="left",
    fill="both",
    expand=True
)


tk.Label(
    resultado,
    text="NÚMERO ATUAL",
    font=("Arial", 11, "bold"),
    fg=BRANCO,
    bg=PAINEL
).pack(
    pady=(0, 5)
)


numero_atual = tk.Label(
    resultado,
    text="0",
       font=("Arial", 30, "bold"),
    fg=VERDE,
    bg=PAINEL
)

numero_atual.pack(
    pady=(0, 15)
)


tk.Label(
    resultado,
    text="RESULTADO",
    font=("Arial", 18, "bold"),
    fg=BRANCO,
    bg=PAINEL
).pack(
    pady=(0, 15)
)


caixa_resultado = tk.Text(
    resultado,
    font=("Consolas", 14),
    bg=FUNDO,
    fg=VERDE,
    relief="flat",
    padx=15,
    pady=15
)

caixa_resultado.pack(
    fill="both",
    expand=True
)


status = tk.Label(
    janela,
    text="STATUS: PRONTO",
    font=("Consolas", 10),
    fg=VERDE,
    bg=FUNDO
)

status.pack(
    pady=10
)


janela.bind(
    "<Return>",
    lambda evento: iniciar()
)


janela.mainloop()