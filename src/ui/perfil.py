import customtkinter as ctk
from src.database import MedDatabase

class PerfilWindow(ctk.CTkFrame):
    def __init__(self, master, ir_para_tela_principal):
        super().__init__(master)
        self.db = MedDatabase()
        self.ir_para_tela_principal = ir_para_tela_principal

        self.label = ctk.CTkLabel(self, text="Cadastro de Perfil", font=("Arial", 20))
        self.label.pack(pady=20)

        self.entry_nome = ctk.CTkEntry(self, placeholder_text="Nome do Paciente")
        self.entry_nome.pack(pady=10)

        self.entry_idade = ctk.CTkEntry(self, placeholder_text="Idade")
        self.entry_idade.pack(pady=10)

        self.entry_cuidadores = ctk.CTkEntry(self, placeholder_text="Cuidadores/Responsáveis")
        self.entry_cuidadores.pack(pady=10)
        
        self.btn = ctk.CTkButton(self, text="Salvar Perfil", command=self.salvar)
        self.btn.pack(pady=20)

    def salvar(self):
        nome = self.entry_nome.get()
        idade = self.entry_idade.get()
        cuidadores = self.entry_cuidadores.get()
        
        self.db.salvar_perfil(nome, idade, cuidadores)
        

        self.ir_para_tela_principal()