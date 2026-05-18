"""
MedControl – Tela de Perfil (src/ui/perfil.py)

Novidades da entrega-intermediaria:
  • Campo de CEP com botão "Buscar CEP" (ViaCEP).
  • Campos de endereço preenchidos automaticamente após busca.
  • Botão "Traçar Rota" que abre o Google Maps no navegador.
  • Tratamento amigável de todos os erros de rede/CEP.
  • Carrega e salva os novos campos no banco de dados.
"""

import threading
import customtkinter as ctk

from src.database.db import get_perfil, salvar_perfil, init_db
from src.services.viacep import (
    buscar_endereco,
    CEPInvalidoError,
    CEPNaoEncontradoError,
    CEPConexaoError,
)
from src.services.maps import abrir_rota_no_maps


class PerfilWindow(ctk.CTkFrame):
    def __init__(self, master, callback_continuar):
        super().__init__(master)
        self.callback_continuar = callback_continuar

        # Garante que o banco está com o schema atualizado
        init_db()

        self._build_ui()
        self._carregar_dados()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(
            self,
            text="👤 Perfil do Idoso",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, pady=(24, 8), padx=24, sticky="w")

        # --- Dados pessoais -------------------------------------------
        self._entry_nome = self._campo(row=1, label="Nome completo")
        self._entry_idade = self._campo(row=2, label="Idade")
        self._entry_cuidadores = self._campo(row=3, label="Cuidadores responsáveis")

        # Separador visual
        ctk.CTkLabel(
            self,
            text="📍 Endereço",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=4, column=0, pady=(16, 4), padx=24, sticky="w")

        # --- CEP + botão buscar ----------------------------------------
        frame_cep = ctk.CTkFrame(self, fg_color="transparent")
        frame_cep.grid(row=5, column=0, sticky="ew", padx=24, pady=(0, 4))
        frame_cep.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_cep, text="CEP").grid(row=0, column=0, sticky="w")

        self._entry_cep = ctk.CTkEntry(
            frame_cep, placeholder_text="00000-000", width=150
        )
        self._entry_cep.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self._btn_buscar = ctk.CTkButton(
            frame_cep,
            text="🔍 Buscar CEP",
            width=130,
            command=self._buscar_cep_thread,
        )
        self._btn_buscar.grid(row=1, column=1, padx=(8, 0), pady=(2, 0))

        # Mensagem de status da busca de CEP
        self._label_status_cep = ctk.CTkLabel(
            frame_cep, text="", text_color="gray", font=ctk.CTkFont(size=12)
        )
        self._label_status_cep.grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))

        # --- Campos de endereço (preenchidos automaticamente) -----------
        self._entry_logradouro = self._campo(row=6,  label="Logradouro")
        self._entry_bairro     = self._campo(row=7,  label="Bairro")
        self._entry_cidade     = self._campo(row=8,  label="Cidade")
        self._entry_estado     = self._campo(row=9,  label="Estado (UF)", width=80)

        # --- Botões de ação --------------------------------------------
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.grid(row=10, column=0, pady=(20, 24), padx=24, sticky="ew")
        frame_botoes.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            frame_botoes,
            text="💾 Salvar Perfil",
            command=self._salvar,
        ).grid(row=0, column=0, padx=4, sticky="ew")

        ctk.CTkButton(
            frame_botoes,
            text="🗺️ Traçar Rota",
            fg_color="#2196F3",
            hover_color="#1565C0",
            command=self._tracar_rota,
        ).grid(row=0, column=1, padx=4, sticky="ew")

        ctk.CTkButton(
            frame_botoes,
            text="▶ Continuar",
            fg_color="#4CAF50",
            hover_color="#388E3C",
            command=self.callback_continuar,
        ).grid(row=0, column=2, padx=4, sticky="ew")

    def _campo(self, row: int, label: str, width: int = 300) -> ctk.CTkEntry:
        """Helper: cria label + CTkEntry e retorna o entry."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 6))
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text=label).grid(row=0, column=0, sticky="w")
        entry = ctk.CTkEntry(frame, width=width)
        entry.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        return entry

    # ------------------------------------------------------------------
    # Lógica de dados
    # ------------------------------------------------------------------

    def _carregar_dados(self):
        """Preenche os campos com os dados salvos no banco."""
        perfil = get_perfil()
        if not perfil:
            return

        self._preencher_entry(self._entry_nome,       perfil["nome"])
        self._preencher_entry(self._entry_idade,      str(perfil["idade"] or ""))
        self._preencher_entry(self._entry_cuidadores, perfil["cuidadores"])
        self._preencher_entry(self._entry_cep,        perfil["cep"])
        self._preencher_entry(self._entry_logradouro, perfil["logradouro"])
        self._preencher_entry(self._entry_bairro,     perfil["bairro"])
        self._preencher_entry(self._entry_cidade,     perfil["cidade"])
        self._preencher_entry(self._entry_estado,     perfil["estado"])

    def _preencher_entry(self, entry: ctk.CTkEntry, valor: str):
        entry.delete(0, "end")
        entry.insert(0, valor or "")

    def _salvar(self):
        try:
            idade = int(self._entry_idade.get() or 0)
        except ValueError:
            self._mostrar_erro("Idade deve ser um número inteiro.")
            return

        salvar_perfil(
            nome=self._entry_nome.get(),
            idade=idade,
            cuidadores=self._entry_cuidadores.get(),
            cep=self._entry_cep.get(),
            logradouro=self._entry_logradouro.get(),
            bairro=self._entry_bairro.get(),
            cidade=self._entry_cidade.get(),
            estado=self._entry_estado.get(),
        )
        self._mostrar_sucesso("✅ Perfil salvo com sucesso!")

    # ------------------------------------------------------------------
    # Busca de CEP (executada em thread separada para não travar a UI)
    # ------------------------------------------------------------------

    def _buscar_cep_thread(self):
        """Dispara a busca em background para não congelar a janela."""
        self._btn_buscar.configure(state="disabled", text="Buscando…")
        self._label_status_cep.configure(text="", text_color="gray")
        threading.Thread(target=self._buscar_cep, daemon=True).start()

    def _buscar_cep(self):
        cep_digitado = self._entry_cep.get()
        try:
            endereco = buscar_endereco(cep_digitado)
            # Atualização da UI deve ocorrer na thread principal
            self.after(0, self._preencher_endereco, endereco)
        except CEPInvalidoError as e:
            self.after(0, self._status_cep_erro, str(e))
        except CEPNaoEncontradoError as e:
            self.after(0, self._status_cep_erro, str(e))
        except CEPConexaoError as e:
            self.after(0, self._status_cep_erro, str(e))
        finally:
            self.after(0, self._btn_buscar.configure, {"state": "normal", "text": "🔍 Buscar CEP"})

    def _preencher_endereco(self, endereco):
        self._preencher_entry(self._entry_cep,        endereco.cep)
        self._preencher_entry(self._entry_logradouro, endereco.logradouro)
        self._preencher_entry(self._entry_bairro,     endereco.bairro)
        self._preencher_entry(self._entry_cidade,     endereco.cidade)
        self._preencher_entry(self._entry_estado,     endereco.estado)
        self._label_status_cep.configure(
            text=f"✅ Endereço encontrado: {endereco}", text_color="green"
        )

    def _status_cep_erro(self, mensagem: str):
        self._label_status_cep.configure(text=f"⚠️ {mensagem}", text_color="#E53935")

    # ------------------------------------------------------------------
    # Traçar Rota
    # ------------------------------------------------------------------

    def _tracar_rota(self):
        sucesso, mensagem = abrir_rota_no_maps()
        if sucesso:
            self._mostrar_sucesso(mensagem)
        else:
            self._mostrar_erro(mensagem)

    # ------------------------------------------------------------------
    # Helpers de feedback
    # ------------------------------------------------------------------

    def _mostrar_erro(self, texto: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Aviso")
        dialog.geometry("360x140")
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=texto, wraplength=320).pack(pady=24, padx=16)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack()

    def _mostrar_sucesso(self, texto: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sucesso")
        dialog.geometry("360x140")
        dialog.grab_set()
        ctk.CTkLabel(
            dialog, text=texto, text_color="green", wraplength=320
        ).pack(pady=24, padx=16)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack()
