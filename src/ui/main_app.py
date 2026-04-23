import customtkinter as ctk
from datetime import datetime
import tkinter.messagebox as messagebox

# Importações do seu projeto e do novo serviço de automação
from src.database import MedDatabase
from src.services.automation import RelatorioAutomation

class MainApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.db = MedDatabase()
        
        # --- Interface Visual ---
        self.label = ctk.CTkLabel(self, text="MedControl - Gestão de Saúde", font=("Arial", 22, "bold"))
        self.label.pack(pady=15)

        self.lista_frame = ctk.CTkScrollableFrame(self, width=400, height=300)
        self.lista_frame.pack(pady=10, padx=20)
        
        # Botões Principais
        self.btn_mais = ctk.CTkButton(self, text="+ Novo Medicamento", command=self.abrir_popup, fg_color="green")
        self.btn_mais.pack(pady=5)
        
        self.btn_historico = ctk.CTkButton(self, text="Ver Histórico", command=self.abrir_historico, fg_color="gray")
        self.btn_historico.pack(pady=5)

        # --- BOTÃO DA ATIVIDADE FTP (REQUISITO DA MISSÃO) ---
        self.btn_exportar = ctk.CTkButton(
            self, 
            text="Enviar Relatório p/ Médico (SFTP)", 
            command=self.disparar_automacao_ftp,
            fg_color="#1f538d",
            hover_color="#14375e"
        )
        self.btn_exportar.pack(pady=15)
        
        # Inicialização
        self.carregar_lista()
        self.verificar_alertas()

    def carregar_lista(self):
        """Atualiza a exibição dos medicamentos na tela"""
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        
        meds = self.db.buscar_medicamentos()
        for med in meds:
            texto = f"💊 {med[1]} - {med[2]}"
            ctk.CTkLabel(self.lista_frame, text=texto).pack(pady=2, anchor="w")

    def abrir_historico(self):
        """Janela de Histórico de Doses"""
        janela = ctk.CTkToplevel(self)
        janela.title("Histórico de Doses")
        janela.geometry("350x400")
        
        frame = ctk.CTkScrollableFrame(janela, width=300, height=350)
        frame.pack(pady=20, padx=20)
        
        dados = self.db.conn.execute("SELECT * FROM historico").fetchall()
        for registro in dados:
            texto = f"📅 {registro[2]} | {registro[3]}"
            if len(registro) > 4 and registro[4]: 
                texto += f"\n📝 Obs: {registro[4]}"
            ctk.CTkLabel(frame, text=texto, anchor="w", justify="left").pack(pady=5, fill="x")

    def disparar_automacao_ftp(self):
        """Lógica da Missão: Conecta, Lista e Envia o relatório via SFTP"""
        self.master.config(cursor="watch")
        self.btn_exportar.configure(state="disabled", text="Enviando...")
        self.update()
        
        try:
            automacao = RelatorioAutomation()
            resultado = automacao.executar_missao_sftp()
            
            if "SUCESSO" in resultado or "Missão Cumprida" in resultado:
                messagebox.showinfo("Sucesso", resultado)
            else:
                messagebox.showerror("Erro na Missão", resultado)
                
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha ao iniciar serviço: {str(e)}")
        finally:
            self.master.config(cursor="")
            self.btn_exportar.configure(state="normal", text="Enviar Relatório p/ Médico (SFTP)")

    def abrir_popup(self):
        """Placeholder para cadastro de medicamentos"""
        print("Abrindo cadastro...")

    def verificar_alertas(self):
        """Monitoramento em tempo real"""
        self.after(60000, self.verificar_alertas)

    def confirmar(self, alerta, med, status, motivo=""):
        """Registra a administração no banco"""
        data_atual = datetime.now().strftime("%d/%m %H:%M")
        self.db.registrar_administracao(med[0], data_atual, status, motivo)
        alerta.destroy()
        self.carregar_lista()