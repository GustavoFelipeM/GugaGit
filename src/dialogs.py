import customtkinter as ctk

from src.config import aplicar_icone


def confirmar(parent, titulo, mensagem):
    janela = ctk.CTkToplevel(parent)

    aplicar_icone(janela)

    janela.title(titulo)
    janela.geometry("400x200")

    resultado = {"confirmado": False}

    def confirmar_acao():
        resultado["confirmado"] = True
        janela.destroy()

    def cancelar():
        janela.destroy()

    label = ctk.CTkLabel(
        janela,
        text=mensagem,
        wraplength=350
    )
    label.pack(pady=30)

    frame = ctk.CTkFrame(janela)
    frame.pack()

    ctk.CTkButton(
        frame,
        text="Cancelar",
        command=cancelar
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        frame,
        text="Confirmar",
        command=confirmar_acao
    ).pack(side="left", padx=10)

    janela.grab_set()
    parent.wait_window(janela)

    return resultado["confirmado"]