import customtkinter as ctk
from datetime import datetime
from src.database import MedDatabase

class MainApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.db = MedDatabase()
        
        # --- Interface ---
        self.label = ctk.CTkLabel(self, text="Meus Medicamentos", font=("Arial", 22, "bold"))
        self.label.pack(pady=15)

        self.lista_frame = ctk.CTkScrollableFrame(self, width=400, height=350)
        self.lista_frame.pack(pady=10, padx=20)
        
        self.btn_mais = ctk.CTkButton(self, text="+ Novo Medicamento", command=self.abrir_popup, fg_color="green")
        self.btn_mais.pack(pady=5)
        
        # Botão Histórico (Agora dentro do __init__)
        self.btn_historico = ctk.CTkButton(self, text="Ver Histórico", command=self.abrir_historico, fg_color="gray")
        self.btn_historico.pack(pady=10)
        
        self.carregar_lista()
        self.verificar_alertas()

    def carregar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        meds = self.db.buscar_medicamentos()
        for med in meds:
            texto = f"{med[1]} | {med[2]} | {med[7]}"
            ctk.CTkLabel(self.lista_frame, text=texto, anchor="w", width=380).pack(pady=5, padx=5)

    def abrir_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Cadastrar")
        popup.geometry("300x400")
        self.entry_nome = ctk.CTkEntry(popup, placeholder_text="Nome")
        self.entry_nome.pack(pady=5, padx=20)
        self.entry_dose = ctk.CTkEntry(popup, placeholder_text="Dose")
        self.entry_dose.pack(pady=5, padx=20)
        self.entry_intervalo = ctk.CTkEntry(popup, placeholder_text="Intervalo (h)")
        self.entry_intervalo.pack(pady=5, padx=20)
        self.entry_inicio = ctk.CTkEntry(popup, placeholder_text="Horário (HH:MM)")
        self.entry_inicio.pack(pady=5, padx=20)
        ctk.CTkButton(popup, text="Salvar", command=lambda: self.salvar_med(popup)).pack(pady=10)

    def salvar_med(self, popup):
        self.db.salvar_medicamento(self.entry_nome.get(), self.entry_dose.get(), "Comprimido", 1, "Oral", int(self.entry_intervalo.get()), self.entry_inicio.get())
        self.carregar_lista()
        popup.destroy()

    def verificar_alertas(self):
        agora = datetime.now().strftime("%H:%M")
        for med in self.db.buscar_medicamentos():
            if med[7] == agora:
                self.abrir_alerta(med)
        self.after(30000, self.verificar_alertas)

    def abrir_alerta(self, med):
        alerta = ctk.CTkToplevel(self)
        alerta.title("Hora do Remédio")
        ctk.CTkLabel(alerta, text=f"Hora de: {med[1]}").pack(pady=10)
        ctk.CTkButton(alerta, text="Tomado ✅", fg_color="green", command=lambda: self.confirmar(alerta, med, "Administrado")).pack(pady=5)
        ctk.CTkButton(alerta, text="Não Tomado ❌", fg_color="red", command=lambda: self.abrir_justificativa(alerta, med)).pack(pady=5)

    def abrir_justificativa(self, alerta, med):
        janela = ctk.CTkToplevel(alerta)
        txt = ctk.CTkEntry(janela, placeholder_text="Motivo...")
        txt.pack(pady=10)
        ctk.CTkButton(janela, text="Salvar", command=lambda: self.confirmar(alerta, med, "Pulado", txt.get())).pack()

    def confirmar(self, alerta, med, status, motivo=""):
        self.db.registrar_administracao(med[0], datetime.now().strftime("%d/%m %H:%M"), status, motivo)
        alerta.destroy()

    # Função do Histórico (Agora indentada corretamente)
    def abrir_historico(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Histórico")
        frame = ctk.CTkScrollableFrame(janela, width=300, height=300)
        frame.pack(pady=20, padx=20)
        dados = self.db.conn.execute("SELECT * FROM historico").fetchall()
        for registro in dados:
            texto = f"Data: {registro[2]} | {registro[3]}"
            if registro[4]: texto += f"\nObs: {registro[4]}"
            ctk.CTkLabel(frame, text=texto, anchor="w").pack(pady=5)