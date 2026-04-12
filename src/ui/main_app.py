import customtkinter as ctk
from datetime import datetime, timedelta
from src.database import MedDatabase

class MainApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.db = MedDatabase()
        
        self.label = ctk.CTkLabel(self, text="Meus Medicamentos", font=("Arial", 22, "bold"))
        self.label.pack(pady=15)

        # Frame com scroll para a lista
        self.lista_frame = ctk.CTkScrollableFrame(self, width=400, height=350)
        self.lista_frame.pack(pady=10, padx=20)
        
        # Botão para adicionar
        self.btn_mais = ctk.CTkButton(self, text="+ Novo Medicamento", 
                                      command=self.abrir_popup, fg_color="green")
        self.btn_mais.pack(pady=15)
        
        self.carregar_lista()

    def carregar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        
        meds = self.db.buscar_medicamentos()
        for med in meds:
            # Estrutura do banco: id, nome, dose, tipo, qtd, via, intervalo, inicio
            texto = f"{med[1]} | {med[4]} {med[3]} | Via: {med[5]} | De {med[6]} em {med[6]}h"
            card = ctk.CTkLabel(self.lista_frame, text=texto, anchor="w", width=380)
            card.pack(pady=5, padx=5)

    def abrir_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Cadastrar Medicamento")
        popup.geometry("350x550")
        popup.grab_set() # Faz o popup ficar no topo até ser fechado

        # Campos de entrada
        self.entry_nome = ctk.CTkEntry(popup, placeholder_text="Nome do Medicamento")
        self.entry_nome.pack(pady=5, padx=20, fill="x")
        
        self.entry_dose = ctk.CTkEntry(popup, placeholder_text="Dose (ex: 500mg)")
        self.entry_dose.pack(pady=5, padx=20, fill="x")

        self.tipo_menu = ctk.CTkOptionMenu(popup, values=["Comprimido", "Gotas", "Xarope", "Injetável"])
        self.tipo_menu.pack(pady=5, padx=20, fill="x")
        
        self.entry_qtd = ctk.CTkEntry(popup, placeholder_text="Quantidade (ex: 1 ou 20)")
        self.entry_qtd.pack(pady=5, padx=20, fill="x")

        self.via_menu = ctk.CTkOptionMenu(popup, values=["Oral", "Sublingual", "Intramuscular", "Intravenosa", "Tópica", "Inalatória"])
        self.via_menu.pack(pady=5, padx=20, fill="x")

        self.entry_intervalo = ctk.CTkEntry(popup, placeholder_text="Intervalo (horas - ex: 8)")
        self.entry_intervalo.pack(pady=5, padx=20, fill="x")

        self.entry_inicio = ctk.CTkEntry(popup, placeholder_text="Horário de início (HH:MM)")
        self.entry_inicio.pack(pady=5, padx=20, fill="x")

        ctk.CTkButton(popup, text="Salvar Medicamento", command=lambda: self.salvar_med(popup)).pack(pady=20)

    def salvar_med(self, popup):
        try:
            self.db.salvar_medicamento(
                self.entry_nome.get(),
                self.entry_dose.get(),
                self.tipo_menu.get(),
                self.entry_qtd.get(),
                self.via_menu.get(),
                int(self.entry_intervalo.get()),
                self.entry_inicio.get()
            )
            self.carregar_lista()
            popup.destroy()
        except ValueError:
            print("Erro: Verifique se o intervalo é um número!")